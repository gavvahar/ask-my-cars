from langchain_core.documents import Document

from .. import db
from .documents import build_description

SEARCH_VECTOR_EXPR = """
    to_tsvector(
        'english',
        make || ' ' || model || ' ' || CAST(year AS TEXT) || ' ' ||
        vehicle_size || ' ' || vehicle_style || ' ' ||
        engine_fuel_type || ' ' || transmission_type || ' ' ||
        driven_wheels || ' ' || market_category
    )
"""


def ensure_search_index():
    db.execute(
        f"ALTER TABLE cars ADD COLUMN IF NOT EXISTS search_vector tsvector "
        f"GENERATED ALWAYS AS ({SEARCH_VECTOR_EXPR}) STORED"
    )
    db.execute("CREATE INDEX IF NOT EXISTS cars_search_vector_idx ON cars USING GIN (search_vector)")


def _build_or_query(query):
    return " OR ".join(query.split())


def search(query, k=8):
    rows = db.search_cars(_build_or_query(query), limit=k)
    documents = []
    for row in rows:
        row = dict(row)
        row.pop("rank", None)
        documents.append(Document(page_content=build_description(row), metadata=row))
    return documents


if __name__ == "__main__":
    ensure_search_index()
    for document in search("Toyota Corolla"):
        print(document.page_content)
        print()
    print("---")
    for document in search("Honda good for families"):
        print(document.page_content)
        print()
