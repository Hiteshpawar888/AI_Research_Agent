from urllib import request
import uuid
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File
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


app = FastAPI()


# =====================================================
# STATIC FILES
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =====================================================
# HTML TEMPLATES
# =====================================================

templates = Jinja2Templates(
    directory="templates"
)


# =====================================================
# REQUEST FORMAT FROM JAVASCRIPT
# =====================================================

class ResearchRequest(BaseModel):
    question: str
    source: str


# =====================================================
# HOME PAGE
# =====================================================

@app.get("/")
def home(request: Request):

    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True
    )

    return response


# =====================================================
# MULTIPLE PDF UPLOAD
# =====================================================

@app.post("/upload")
async def upload_pdfs(
    request: Request,
    files: list[UploadFile] = File(...)
):

    uploaded_files = []
    
    # Maximum number of PDFs allowed per upload
    max_files = 10

    if len(files) > max_files:

        return {
            "success": False,
            "message": f"You can upload a maximum of {max_files} PDF files at a time."
        }

    session_id = request.cookies.get("session_id")

    if not session_id:
        return {
            "success": False,
            "message": "Session not found. Please refresh the page."
        }

    upload_folder = Path("uploads") / session_id

    upload_folder.mkdir(
        parents=True,
        exist_ok=True
    )
    
    file_path = None

    try:

        for file in files:

            # Skip non-PDF files
            if not file.filename.lower().endswith(".pdf"):
                continue
            # Keep only the real filename
            safe_filename = Path(file.filename).name


            # -----------------------------------------
            # SAVE PDF
            # -----------------------------------------

            file_path = upload_folder / safe_filename
            
            # Prevent duplicate PDF uploads
            if file_path.exists():

                return {
                    "success": False,
                    "message": f"{safe_filename} has already been uploaded."
                }

            file_content = await file.read()
            
            # Maximum PDF size: 20 MB
            max_file_size = 20 * 1024 * 1024

            if len(file_content) > max_file_size:

                return {
                    "success": False,
                    "message": f"{safe_filename} is too large. Maximum file size is 20 MB."
                }
            
            # Validate that the file is actually a PDF
            if not file_content.startswith(b"%PDF-"):

                return {
                    "success": False,
                    "message": f"{safe_filename} is not a valid PDF file."
                }


            with open(file_path, "wb") as saved_file:

                saved_file.write(
                    file_content
                )


            # -----------------------------------------
            # READ PDF
            # -----------------------------------------

            _, page_texts = read_pdf(
                str(file_path)
            )
            
            # Maximum number of pages allowed per PDF
            max_pages = 300

            if len(page_texts) > max_pages:

                if file_path.exists():
                    file_path.unlink()

                return {
                    "success": False,
                    "message": f"{safe_filename} has too many pages. Maximum allowed is {max_pages} pages."
                }


            # -----------------------------------------
            # CREATE CHUNKS
            # -----------------------------------------

            chunks, page_metadatas = chunk_pages(
                page_texts
            )


            # -----------------------------------------
            # STORE IN CHROMADB
            # -----------------------------------------

            store_chunks(
                chunks,
                safe_filename,
                page_metadatas,
                session_id
            )


            uploaded_files.append(
                safe_filename
            )


        if not uploaded_files:

            return {
                "success": False,
                "message":
                    "No valid PDF files were uploaded."
            }


        return {
            "success": True,
            "message":
                "PDFs uploaded and indexed successfully.",
            "filenames": uploaded_files
        }


    except Exception as e:

        # Remove unreadable or partially processed PDF
        if file_path and file_path.exists():
            file_path.unlink()

        return {
            "success": False,
            "message": f"PDF processing failed: {e}"
        }


# =====================================================
# RESEARCH ENDPOINT
# =====================================================

@app.post("/ask")
def ask_question(data: ResearchRequest, request: Request):
    
     # Get current user's session ID
    session_id = request.cookies.get("session_id")

    if not session_id:

        return {
            "answer": "Session not found. Please refresh the page."
        }

    question = data.question.strip()

    source = data.source.lower().strip()


    # -----------------------------------------
    # CHECK EMPTY QUESTION
    # -----------------------------------------

    if not question:

        return {
            "answer":
                "Please enter a research question."
        }


    # =================================================
    # WEB ONLY
    # =================================================

    if source == "web":

        answer = generate_answer(
            question
        )


        return {
            "answer": answer
        }


    # =================================================
    # FIND ALL PDF FILES
    # =================================================

    user_upload_folder = Path("uploads") / session_id

    pdf_files = list(
        user_upload_folder.glob("*.pdf")
    )


    if not pdf_files:

        return {
            "answer":
                "No PDF files were found."
        }


    all_chunks = []

    all_metadatas = []

    all_distances = []


    # =================================================
    # PDF INDEXING + RETRIEVAL
    # =================================================

    for pdf_file in pdf_files:

        try:

            # -----------------------------------------
            # INDEX PDF IF NOT ALREADY INDEXED
            # -----------------------------------------

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


            # -----------------------------------------
            # RETRIEVE RELEVANT CHUNKS
            # -----------------------------------------

            chunks, metadatas, distances = (
                retrieve_relevant_chunks(
                    question,
                    source_name=pdf_file.name,
                    session_id=session_id,
                    top_k=3
                )
            )


            all_chunks.extend(
                chunks
            )


            all_metadatas.extend(
                metadatas
            )


            all_distances.extend(
                distances
            )


        except Exception as e:

            print(
                f"Skipping {pdf_file.name}: {e}"
            )


    # =================================================
    # NO RETRIEVAL RESULTS
    # =================================================

    if not all_chunks:

        return {
            "answer":
                "I could not find relevant information "
                "in the available documents."
        }


    # =================================================
    # GLOBAL RANKING ACROSS ALL PDFs
    # =================================================

    combined_results = list(
        zip(
            all_chunks,
            all_metadatas,
            all_distances
        )
    )


    combined_results.sort(
        key=lambda item: item[2]
    )


    # Keep best 3 results globally
    top_results = combined_results[:3]


    relevant_chunks = [
        item[0]
        for item in top_results
    ]


    metadatas = [
        item[1]
        for item in top_results
    ]


    # =================================================
    # BUILD RAG PROMPT
    # =================================================

    prompt = build_rag_prompt(
        question,
        relevant_chunks,
        metadatas
    )


    if prompt is None:

        return {
            "answer":
                "I could not find this information "
                "in the provided documents."
        }


    # =================================================
    # PDF ONLY
    # =================================================

    if source == "pdf":

        answer = generate_rag_answer(
            prompt
        )


        return {
            "answer": answer
        }


    # =================================================
    # PDF + WEB
    # =================================================

    if source == "both":

        combined_context = "\n\n".join(
            [
                f"[Source: {metadata.get('source', 'Unknown')}, "
                f"Page: {metadata.get('page', 'Unknown')}]\n{chunk}"
                for chunk, metadata in zip(
                    relevant_chunks,
                    metadatas
                )
            ]
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


    # =================================================
    # INVALID SOURCE
    # =================================================

    return {
        "answer":
            "Please select PDF, Web, or PDF + Web."
    }