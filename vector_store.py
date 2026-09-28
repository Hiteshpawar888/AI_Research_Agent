from pathlib import Path

import chromadb

from embeddings import model


# =====================================================
# CHROMA DATABASE
# =====================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)


collection = client.get_or_create_collection(
    name="research_documents"
)


# =====================================================
# STORE DOCUMENT CHUNKS
# =====================================================

def store_chunks(
    chunks,
    source_name,
    page_metadatas,
    session_id
):
    """
    Store document chunks in ChromaDB.

    Each chunk is isolated by:
    - session ID
    - PDF source
    - page number
    """

    if not session_id:
        raise ValueError(
            "Session ID is required."
        )

    if not source_name:
        raise ValueError(
            "Source name is required."
        )

    if not chunks:
        raise ValueError(
            "No document chunks were provided."
        )

    if not page_metadatas:
        raise ValueError(
            "Page metadata is required."
        )

    if len(chunks) != len(page_metadatas):
        raise ValueError(
            "Chunks and page metadata must have the same length."
        )


    # Store only the filename,
    # not the full Windows path
    source_name = Path(
        source_name
    ).name


    # Remove old chunks for the same
    # session + document before re-indexing.
    #
    # This prevents stale duplicate chunks
    # if the document is indexed again.
    collection.delete(
        where={
            "$and": [
                {
                    "session_id": session_id
                },
                {
                    "source": source_name
                }
            ]
        }
    )


    # Create normalized embeddings
    embeddings = model.encode(
        chunks,
        normalize_embeddings=True
    ).tolist()


    ids = []

    metadatas = []


    for index, metadata in enumerate(
        page_metadatas
    ):

        page = metadata.get(
            "page",
            "Unknown"
        )


        ids.append(
            f"{session_id}_"
            f"{source_name}_"
            f"chunk_{index}"
        )


        metadatas.append(
            {
                "session_id": session_id,
                "source": source_name,
                "page": page,
                "chunk_index": index
            }
        )


    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )


# =====================================================
# CHECK WHETHER DOCUMENT IS ALREADY INDEXED
# =====================================================

def is_document_indexed(
    source_name,
    session_id
):
    """
    Check whether a document already exists
    inside the current user's session.
    """

    if not session_id:
        return False

    if not source_name:
        return False


    source_name = Path(
        source_name
    ).name


    results = collection.get(
        where={
            "$and": [
                {
                    "session_id": session_id
                },
                {
                    "source": source_name
                }
            ]
        },
        limit=1
    )


    ids = results.get(
        "ids",
        []
    )


    return len(ids) > 0


# =====================================================
# SEARCH DOCUMENT CHUNKS
# =====================================================

def search_chunks(
    question,
    source_name,
    session_id,
    top_k=3
):
    """
    Search relevant chunks only inside:
    - the selected PDF
    - the current user's session
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not source_name:
        raise ValueError(
            "Source name is required."
        )

    if not session_id:
        raise ValueError(
            "Session ID is required."
        )

    if not isinstance(
        top_k,
        int
    ) or top_k < 1:

        raise ValueError(
            "top_k must be a positive integer."
        )


    source_name = Path(
        source_name
    ).name


    # Create query embedding
    query_embedding = model.encode(
        question.strip(),
        normalize_embeddings=True
    ).tolist()


    results = collection.query(
        query_embeddings=[
            query_embedding
        ],

        n_results=top_k,

        where={
            "$and": [
                {
                    "session_id": session_id
                },
                {
                    "source": source_name
                }
            ]
        },

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


    documents = results.get(
        "documents",
        []
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    distances = results.get(
        "distances",
        []
    )


    # Safe empty-result handling
    if (
        not documents
        or not documents[0]
    ):
        return [], [], []


    return (
        documents[0],
        metadatas[0],
        distances[0]
    )