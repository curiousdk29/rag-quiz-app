# ingest.py

from dotenv import load_dotenv
load_dotenv()

import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "models/gemini-embedding-001"



def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

def sanitize_collection_name(filename: str) -> str:
    # ChromaDB collection names must be 3-63 chars, alphanumeric + hyphens only
    name = filename.replace(".pdf", "").lower()
    name = re.sub(r"[^a-z0-9-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:63] if len(name) >= 3 else name + "-col"

def get_vectorstore(collection_name: str = "default") -> Chroma:
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings(),
        collection_name=collection_name
    )

def ingest_pdf(pdf_path: str, collection_name: str = None) -> dict:
    print(f"Loading {pdf_path}...")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    embeddings = get_embeddings()

    # Use the filename as collection name if not provided
    if not collection_name:
        collection_name = sanitize_collection_name(os.path.basename(pdf_path))

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=collection_name
    )
    vectorstore.add_documents(chunks)

    print(f"Stored {len(chunks)} chunks in collection '{collection_name}'")
    return {"pages": len(documents), "chunks": len(chunks), "collection": collection_name}


