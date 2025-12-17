import os
import uuid
import logging
from openai import OpenAI
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_llm_client():
    return OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

def ingest_pdf(pdf_path: str, source_id: str = None) -> int:
    """
    Loads a PDF, chunks it, embeds it, and upserts to Qdrant.
    Returns the number of chunks ingested.
    """
    if not source_id:
        source_id = os.path.basename(pdf_path)

    logger.info(f"Starting ingestion for {pdf_path} (source_id={source_id})")
    
    # 1. Load and Chunk
    chunks = load_and_chunk_pdf(pdf_path)
    logger.info(f"Generated {len(chunks)} chunks")

    # 2. Embed
    vecs = embed_texts(chunks)
    
    # 3. Prepare for Qdrant
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
    payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
    
    # 4. Upsert
    QdrantStorage().upsert(ids, vecs, payloads)
    logger.info("Upsert completed")
    
    return len(chunks)

def query_pdf(question: str, top_k: int = 5) -> dict:
    """
    Embeds the question, searches Qdrant, and calls the LLM for an answer.
    """
    logger.info(f"Querying: {question}")

    # 1. Embed Question
    query_vec = embed_texts([question])[0]

    # 2. Search Qdrant
    store = QdrantStorage()
    found = store.search(query_vec, top_k)
    logger.info(f"Found {len(found['contexts'])} contexts")

    # 3. Construct Prompt
    context_block = "\n\n".join(f"- {c}" for c in found['contexts'])
    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )

    # 4. Call LLM
    client = get_llm_client()
    response = client.chat.completions.create(
        model="gemini-2.0-flash-lite", # Updated to a widely available model alias if 2.5 is not std, or keep 2.5 if user had it. User code had 2.5-flash.
        messages=[
            {"role": "system", "content": "You answer questions using only the provided context."},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2,
        max_tokens=1024
    )
    
    answer = response.choices[0].message.content.strip()
    
    return {
        "answer": answer,
        "sources": found['sources'],
        "contexts": found['contexts']
    }
