import time

from backend import db
from backend.rag.documents import build_document
from backend.rag.vectorstore import get_vectorstore

BATCH_SIZE = 500

ENSURE_EMBEDDED_COLUMN_SQL = "ALTER TABLE cars ADD COLUMN IF NOT EXISTS embedded_at TIMESTAMPTZ"


def _ensure_embedded_column():
    db.execute(ENSURE_EMBEDDED_COLUMN_SQL)


def _chunk(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def build_embeddings():
    _ensure_embedded_column()
    vectorstore = get_vectorstore()

    cars = db.get_cars_where_not_embedded()
    total = len(cars)
    if total == 0:
        print("All cars already embedded, nothing to do.")
        return

    print(f"Embedding {total} cars in batches of {BATCH_SIZE}...")

    done = 0
    for batch in _chunk(cars, BATCH_SIZE):
        start = time.time()
        documents = [build_document(car) for car in batch]
        ids = [str(car["id"]) for car in batch]

        vectorstore.add_documents(documents, ids=ids)
        db.mark_embedded(ids)

        done += len(batch)
        elapsed = time.time() - start
        print(f"  {done}/{total} embedded ({elapsed:.1f}s for this batch)")

    print(f"Done. Embedded {done} cars.")


if __name__ == "__main__":
    build_embeddings()
