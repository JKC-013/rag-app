import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import rag_service

load_dotenv()

st.set_page_config(page_title="RAG Ingest PDF", page_icon="📄", layout="centered")

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path

st.title("Upload a PDF to Ingest")
uploaded = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)

if uploaded is not None:
    path = save_uploaded_pdf(uploaded)
    if st.button("Ingest PDF"):
        with st.spinner("Uploading and ingesting..."):
            try:
                # Direct call to service
                num_chunks = rag_service.ingest_pdf(str(path.resolve()))
                st.success(f"Successfully digested {path.name} into {num_chunks} chunks.")
            except Exception as e:
                st.error(f"Error during ingestion: {e}")

st.divider()
st.title("Ask a question about your PDFs")

with st.form("rag_query_form"):
    question = st.text_input("Your question")
    top_k = st.number_input("How many chunks to retrieve", min_value=1, max_value=20, value=5, step=1)
    submitted = st.form_submit_button("Ask")

    if submitted and question.strip():
        with st.spinner("Generating answer..."):
            try:
                # Direct call to service
                result = rag_service.query_pdf(question.strip(), int(top_k))
                
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                
                st.subheader("Answer")
                st.write(answer or "(No answer)")
                
                if sources:
                    st.caption("Sources")
                    for s in sources:
                        st.write(f"- {s}")
            except Exception as e:
                st.error(f"Error during query: {e}")
