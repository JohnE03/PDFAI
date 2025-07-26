import os
import fitz
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import numpy as np
import pickle

# Load model
embedder = SentenceTransformer("models/distiluse-base-multilingual-cased-v2")

# Step 1: Extract text from PDFs
def extract_texts(folder_path):
    all_docs = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            path = os.path.join(folder_path, file)
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            print("[DEBUG] Sample Arabic text:\n", text[:500])
            all_docs.append({"filename": file, "content": text})
    return all_docs

# Step 2: Chunk text and tag with filename
def chunk_texts(docs, chunk_size=500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    for doc in docs:
        for chunk in splitter.split_text(doc["content"]):
            chunks.append(f"{doc['filename']} ||| {chunk}")
    return chunks

# Step 3: Embed and store FAISS index
def build_faiss_index(chunks, index_path="index/faiss_index"):
    if not chunks:
        print("[ERROR] No text chunks were generated. Please check your PDFs.")
        return

    os.makedirs("index", exist_ok=True)
    vectors = embedder.encode(chunks, show_progress_bar=True)
    dim = vectors[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors))
    faiss.write_index(index, index_path + ".index")
    with open(index_path + ".pkl", "wb") as f:
        pickle.dump(chunks, f)
    print("[INFO] FAISS index built and saved.")

# Build the index (used for manual testing)
if __name__ == "__main__":
    docs = extract_texts("data")
    chunks = chunk_texts(docs)
    build_faiss_index(chunks)