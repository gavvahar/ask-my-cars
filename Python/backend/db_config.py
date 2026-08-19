import os

from psycopg.conninfo import make_conninfo
from sqlalchemy import URL


def connection_string():
    return make_conninfo(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )


def sqlalchemy_url():
    # langchain_postgres.PGVector builds a SQLAlchemy engine internally, which
    # needs a SQLAlchemy-format URL (postgresql+psycopg://...) -- the libpq
    # keyword/value conninfo from connection_string() (used by psycopg.connect
    # / ConnectionPool directly) fails SQLAlchemy's URL parser.
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB"),
    ).render_as_string(hide_password=False)
