from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.runnables import RunnableLambda

from . import fts_search
from .vectorstore import get_vectorstore

RETRIEVAL_K = 8
SPARSE_WEIGHT = 0.4
DENSE_WEIGHT = 0.6


def _fts_retrieve(query):
    return fts_search.search(query, k=RETRIEVAL_K)


def get_hybrid_retriever():
    vectorstore = get_vectorstore()
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVAL_K})
    sparse_retriever = RunnableLambda(_fts_retrieve)

    return EnsembleRetriever(
        retrievers=[sparse_retriever, dense_retriever],
        weights=[SPARSE_WEIGHT, DENSE_WEIGHT],
    )


if __name__ == "__main__":
    retriever = get_hybrid_retriever()
    results = retriever.invoke("fuel-efficient family SUV under $35k")
    for document in results:
        print(document.page_content)
        print()
