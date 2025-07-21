import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
import numpy as np
import requests

# Load embedder once
embedder = SentenceTransformer("models/all-MiniLM-L6-v2")

# These will be set after loading the index
index = None
chunks = None

def load_index():
    global index, chunks
    if not (os.path.exists("index/faiss_index.index") and os.path.exists("index/faiss_index.pkl")):
        raise FileNotFoundError(
            "\n\n🚫 FAISS index not found.\n➡️ Please upload PDFs first through the GUI so the index can be built.\n"
        )
    index = faiss.read_index("index/faiss_index.index")
    with open("index/faiss_index.pkl", "rb") as f:
        chunks = pickle.load(f)

# Search top-k chunks
def search(question, top_k=5):
    global index, chunks
    if index is None or chunks is None:
        load_index()

    q_vec = embedder.encode([question])
    D, I = index.search(np.array(q_vec), top_k)

    results = []
    for i in I[0]:
        if "|||" in chunks[i]:
            fname, text = chunks[i].split("|||", 1)
            results.append((fname.strip(), text.strip()))
        else:
            results.append(("Unknown", chunks[i].strip()))
    return results

# Call Ollama LLM
def ask_llm(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        return response.json()["response"]
    except Exception as e:
        return f"Error: {e}"

# Full QA pipeline
def answer_question(question):
    results = search(question)
    context = "\n\n".join([f"[{fname}]\n{text}" for fname, text in results])
    top_file = results[0][0] if results else "Unknown"

    prompt = f"""You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question: {question}
Answer:"""

    answer = ask_llm(prompt)
    return f"(Found in: {top_file})\n\n{answer}"