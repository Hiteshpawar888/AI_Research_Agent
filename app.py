
import hashlib
import logging
from pathlib import Path

import firebase_admin
from firebase_admin import auth as firebase_auth

from fastapi import (
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    Request,
    UploadFile
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from document_reader import read_pdf, chunk_pages
from vector_store import store_chunks, is_document_indexed
from retriever import retrieve_relevant_chunks
from prompt_builder import build_rag_prompt

from research_agent import (
    generate_answer,
    generate_rag_answer,
    generate_combined_answer
)


# ==========================================
# CONFIGURATION
# ==========================================

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = "ai-research-agent-f00a9"

MAX_FILES = 10
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_PAGES = 300


# ==========================================
# FIREBASE ADMIN INITIALIZATION
# ==========================================

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(
        options={"projectId": FIREBASE_PROJECT_ID}
    )


# ==========================================
# FASTAPI
# ==========================================

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


# ==========================================
# RESEARCH REQUEST FORMAT
# ==========================================

class ResearchRequest(BaseModel):
    question: str
    source: str


# ==========================================
# FIREBASE TOKEN VERIFICATION
# ==========================================

def require_user(
    authorization: str | None = Header(default=None)
) -> str:

    if (
        not authorization or
        not authorization.lower().startswith("bearer ")
    ):
        raise HTTPException(
            status_code=401,
            detail="Please sign in to continue.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing Firebase ID token."
        )

    try:
        decoded = firebase_auth.verify_id_token(token)

    except (
        firebase_auth.InvalidIdTokenError,
        firebase_auth.ExpiredIdTokenError,
        ValueError
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired login. Please sign in again."
        )

    except Exception:
        logger.exception("Firebase token verification error")

        raise HTTPException(
            status_code=503,
            detail="Authentication is temporarily unavailable."
        )

    uid = decoded.get("uid")

    if not uid:
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase user identity."
        )

    return uid


# ==========================================
# SECURE USER WORKSPACE
# ==========================================

def workspace_id(uid: str) -> str:

    hashed_uid = hashlib.sha256(
        uid.encode("utf-8")
    ).hexdigest()

    return "user_" + hashed_uid


# ==========================================
# HOME PAGE
# ==========================================

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# ==========================================
# PDF UPLOAD
# ==========================================

@app.post("/upload")
async def upload_pdfs(
    files: list[UploadFile] = File(...),
    uid: str = Depends(require_user)
):

    if len(files) > MAX_FILES:
        return {
            "success": False,
            "message": (
                f"You can upload a maximum of "
                f"{MAX_FILES} PDF files at a time."
            )
        }

    session_id = workspace_id(uid)

    upload_folder = Path("uploads") / session_id

    upload_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    uploaded_files = []
    file_path = None

    try:
        for file in files:

            safe_filename = Path(
                file.filename or ""
            ).name

            if not safe_filename.lower().endswith(".pdf"):
                continue

            file_path = upload_folder / safe_filename

            if file_path.exists():
                return {
                    "success": False,
                    "message": (
                        f"{safe_filename} has already been uploaded."
                    )
                }

            file_content = await file.read(
                MAX_FILE_BYTES + 1
            )

            if len(file_content) > MAX_FILE_BYTES:
                return {
                    "success": False,
                    "message": (
                        f"{safe_filename} is too large. "
                        "Maximum file size is 20 MB."
                    )
                }

            if not file_content.startswith(b"%PDF-"):
                return {
                    "success": False,
                    "message": (
                        f"{safe_filename} is not a valid PDF file."
                    )
                }

            # Save PDF

            file_path.write_bytes(file_content)

            # Read PDF

            _, page_texts = read_pdf(
                str(file_path)
            )

            if len(page_texts) > MAX_PAGES:

                file_path.unlink(missing_ok=True)

                return {
                    "success": False,
                    "message": (
                        f"{safe_filename} has too many pages. "
                        f"Maximum allowed is {MAX_PAGES} pages."
                    )
                }

            # Create chunks

            chunks, page_metadatas = chunk_pages(
                page_texts
            )

            # Store in ChromaDB

            store_chunks(
                chunks,
                safe_filename,
                page_metadatas,
                session_id
            )

            uploaded_files.append(safe_filename)

            file_path = None

        if not uploaded_files:
            return {
                "success": False,
                "message": "No valid PDF files were uploaded."
            }

        return {
            "success": True,
            "message": "PDFs uploaded and indexed successfully.",
            "filenames": uploaded_files
        }

    except Exception:

        logger.exception("PDF processing failed")

        if file_path is not None:
            file_path.unlink(missing_ok=True)

        return {
            "success": False,
            "message": "PDF processing failed. Please try again."
        }

    finally:

        for file in files:
            await file.close()


# ==========================================
# RESEARCH ENDPOINT
# ==========================================

@app.post("/ask")
def ask_question(
    data: ResearchRequest,
    uid: str = Depends(require_user)
):

    session_id = workspace_id(uid)

    question = data.question.strip()
    source = data.source.lower().strip()

    if not question:
        return {
            "answer": "Please enter a research question."
        }

    if source not in ("pdf", "web", "both"):
        return {
            "answer": "Please select PDF, Web, or PDF + Web."
        }

    # ======================================
    # WEB ONLY
    # ======================================

    if source == "web":

        answer = generate_answer(question)

        return {
            "answer": answer
        }

    # ======================================
    # FIND USER PDF FILES
    # ======================================

    user_upload_folder = Path("uploads") / session_id

    pdf_files = list(
        user_upload_folder.glob("*.pdf")
    )

    if not pdf_files:
        return {
            "answer": "No PDF files were found."
        }

    all_chunks = []
    all_metadatas = []
    all_distances = []

    # ======================================
    # PDF RETRIEVAL
    # ======================================

    for pdf_file in pdf_files:

        try:

            if not is_document_indexed(
                pdf_file.name,
                session_id
            ):

                _, page_texts = read_pdf(
                    str(pdf_file)
                )

                chunks, page_metadatas = chunk_pages(
                    page_texts
                )

                store_chunks(
                    chunks,
                    pdf_file.name,
                    page_metadatas,
                    session_id
                )

            chunks, metadatas, distances = (
                retrieve_relevant_chunks(
                    question,
                    source_name=pdf_file.name,
                    session_id=session_id,
                    top_k=3
                )
            )

            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
            all_distances.extend(distances)

        except Exception:
            logger.exception(
                "Skipping PDF during retrieval"
            )

    # ======================================
    # CHECK RESULTS
    # ======================================

    if not all_chunks:
        return {
            "answer": (
                "I could not find relevant information "
                "in the available documents."
            )
        }

    # ======================================
    # GLOBAL RANKING
    # ======================================

    combined_results = sorted(
        zip(
            all_chunks,
            all_metadatas,
            all_distances
        ),
        key=lambda item: item[2]
    )

    top_results = combined_results[:3]

    relevant_chunks = [
        item[0] for item in top_results
    ]

    metadatas = [
        item[1] for item in top_results
    ]

    # ======================================
    # BUILD RAG PROMPT
    # ======================================

    prompt = build_rag_prompt(
        question,
        relevant_chunks,
        metadatas
    )

    if prompt is None:
        return {
            "answer": (
                "I could not find this information "
                "in the provided documents."
            )
        }

    # ======================================
    # PDF ONLY
    # ======================================

    if source == "pdf":

        answer = generate_rag_answer(
            prompt
        )

        return {
            "answer": answer
        }

    # ======================================
    # PDF + WEB
    # ======================================

    combined_context = "\n\n".join(

        f"[Source: {metadata.get('source', 'Unknown')}, "
        f"Page: {metadata.get('page', 'Unknown')}]\n{chunk}"

        for chunk, metadata in zip(
            relevant_chunks,
            metadatas
        )
    )

    combined_prompt = f"""
Research the user's question using BOTH:

1. The PDF context below.
2. Reliable current web sources.

PDF CONTEXT:
{combined_context}

QUESTION:
{question}

INSTRUCTIONS:
- Use the PDF evidence where relevant.
- Use current web sources for additional or up-to-date information.
- Do not invent information.
- Clearly distinguish PDF evidence from web information.
- Cite PDF information using filename and page number.
- Cite web information using the actual source.
- Keep the answer clear and concise.
- Add a Sources section at the end containing both PDF and web sources actually used.
"""

    answer = generate_combined_answer(
        combined_prompt
    )

    return {
        "answer": answer
    }
