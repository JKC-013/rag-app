from google import genai
from google.genai import types
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

import os

import os
try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key and st is not None:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"Failed to initialize GenAI client: {e}")
    client = None
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, 'text', None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not client:
        raise ValueError("Google GenAI client is not initialized. Please set GEMINI_API_KEY.")
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBED_DIM)
    )
    return [item.values for item in response.embeddings]