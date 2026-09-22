from pathlib import Path

import chromadb

from embeddings import model


# Store vector data locally on your computer
client = chromadb.PersistentClient(path="./chroma_db")

# Create the collection if it does not already exist
collection = client.get_or_create_collection(
    name="research_documents"
)


def store_chunks(chunks, source_name, page_metadatas):
    """Store document chunks, embeddings, and page metadata in ChromaDB."""

    if not chunks:
        return

    source_name = Path(source_name).name

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True
    ).tolist()

    ids = [
        f"{source_name}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = []

    for i, page_metadata in enumerate(page_metadatas):
        metadatas.append({
            "source": source_name,
            "page": page_metadata["page"],
            "chunk_index": i
        })

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
def is_document_indexed(source_name):
    """Check whether a PDF is already stored in ChromaDB."""

    source_name = Path(source_name).name

    results = collection.get(
        where={"source": source_name},
        limit=1
    )

    return len(results["ids"]) > 0


def search_chunks(question, source_name, top_k=3):
    """Find the most relevant chunks from the selected PDF."""

    source_name = Path(source_name).name

    question_embedding = model.encode(
        [question],
        normalize_embeddings=True
    )[0].tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where={"source": source_name},
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"]:
        return [], [], []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return documents, metadatas, distances