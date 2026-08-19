import os

from langchain_ollama import OllamaEmbeddings

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://192.168.1.14:11434")
EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")

_embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)


def embed_text(text):
    return _embeddings.embed_query(text)


def embed_texts(texts):
    return _embeddings.embed_documents(texts)


def get_embeddings_model():
    return _embeddings


if __name__ == "__main__":
    vector = embed_text("This is a test car description.")
    print(f"Embedding dimension: {len(vector)}")
    print(vector[:5])
