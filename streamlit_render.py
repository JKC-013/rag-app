import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import rag_service  # Using direct service for file access + speed

load_dotenv()

st.set_page_config(page_title="RAG Ingest PDF (Render)", page_icon="📄", layout="centered")

# Initialize Inngest Client (Production Mode determined by Render Env)
inngest_client = inngest.Inngest(
    app_id="rag_app",
    is_production=os.getenv("RENDER") == "true",
)

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path

async def report_ingest_event(pdf_path: Path, num_chunks: int) -> None:
    """Sends a 'success' event to Inngest so it appears in the Dashboard."""
    await inngest_client.send(
        inngest.Event(
            name="rag/ingest_completed",
            data={
                "pdf_path": str(pdf_path.name),
                "num_chunks": num_chunks,
                "status": "success"
            },
        )
    )

async def report_query_event(question: str, answer: str) -> None:
    """Sends a 'query' event to Inngest."""
    await inngest_client.send(
        inngest.Event(
            name="rag/query_completed",
            data={
                "question": question,
                "answer_snippet": answer[:100], # Log first 100 chars
            },
        )
    )

st.title("Upload a PDF to Ingest (Render + Inngest)")
uploaded = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)

if uploaded is not None:
    path = save_uploaded_pdf(uploaded)
    if st.button("Ingest PDF"):
        with st.spinner("Ingesting and Reporting to Inngest..."):
            try:
                # 1. Do the work locally (because we have the file)
                num_chunks = rag_service.ingest_pdf(str(path.resolve()))
                
                # 2. Report to Inngest (Fire and forget)
                asyncio.run(report_ingest_event(path, num_chunks))
                
                st.success(f"Successfully processed {path.name} ({num_chunks} chunks) and logged to Inngest!")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.title("Ask a question")

with st.form("rag_query_form"):
    question = st.text_input("Your question")
    top_k = st.number_input("Chunks", min_value=1, value=5)
    submitted = st.form_submit_button("Ask")

    if submitted and question.strip():
        with st.spinner("Thinking..."):
            try:
                # 1. Query locally (Direct speed)
                result = rag_service.query_pdf(question.strip(), int(top_k))
                answer = result.get("answer", "")
                
                # 2. Report to Inngest
                asyncio.run(report_query_event(question, answer))
                
                st.subheader("Answer")
                st.write(answer)
                if result.get("sources"):
                    st.caption(f"Sources: {result['sources']}")
            except Exception as e:
                st.error(f"Error: {e}")
