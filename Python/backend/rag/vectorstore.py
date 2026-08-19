from langchain_postgres import PGVector

from ..db_config import sqlalchemy_url
from .embeddings import get_embeddings_model

COLLECTION_NAME = "car_documents"


def get_vectorstore():
    return PGVector(
        embeddings=get_embeddings_model(),
        collection_name=COLLECTION_NAME,
        connection=sqlalchemy_url(),
        use_jsonb=True,
        create_extension=False,
    )


if __name__ == "__main__":
    vectorstore = get_vectorstore()
    print(f"PGVector store ready: collection={COLLECTION_NAME}")
