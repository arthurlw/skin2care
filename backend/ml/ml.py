import os
import json
from typing import List, Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# ------------------- Load JSON -------------------
def read_json(filepath: str) -> List[Dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return []

# ------------------- Prepare Docs -------------------
def json_to_documents(json_data: List[Dict]) -> List[Document]:
    documents = []
    for i, item in enumerate(json_data):
        text = json.dumps(item, indent=2)
        doc = Document(page_content=text, metadata={"source": f"product_{i}"})
        documents.append(doc)
    return documents

# ------------------- Index to FAISS -------------------
def index_to_faiss(json_path: str, save_path: str = "faiss_index"):
    print("🔄 Reading skincare data...")
    data = read_json(json_path)
    documents = json_to_documents(data)

    print("🧠 Generating embeddings...")
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    print("🗃️ Creating FAISS index...")
    vectorstore = FAISS.from_documents(documents, embedding)
    vectorstore.save_local(save_path)

    print(f"✅ Saved FAISS index to '{save_path}'")

# ------------------- RAG Query -------------------
def perform_rag(query: str, embedding_model, userdata: Dict, save_path: str = "faiss_index", model="deepseek/deepseek-r1:free"):
    print("🔎 Loading FAISS index...")
    vectorstore = FAISS.load_local(save_path, embedding_model, allow_dangerous_deserialization=True)
    docs = vectorstore.similarity_search(query, k=5)

    context_string = "\n\n-----\n\n".join(doc.page_content for doc in docs)
    augmented_query = f"<CONTEXT>\n{context_string}\n</CONTEXT>\n\nMY QUESTION:\n{query}"

    system_prompt = """You are a skincare expert. Answer clearly using only the context provided.
Only recommend products if they are mentioned in the context."""

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=userdata["OPENROUTER_API_KEY"]
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": augmented_query}
        ]
    )

    return response.choices[0].message.content

# ------------------- Example Usage -------------------
if __name__ == "__main__":
    userdata = {
        "OPENROUTER_API_KEY": "insert-key-here"
    }

    json_path = "./content/sheet_masks_products.json"
    faiss_path = "faiss_index"

    # 1. Index the JSON file to FAISS
    index_to_faiss(json_path, faiss_path)

    # 2. Ask a question
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    question = input("What question do you have? ")
    response = perform_rag(question, embed_model, userdata)
    print("💬 RAG Response:\n", response)
