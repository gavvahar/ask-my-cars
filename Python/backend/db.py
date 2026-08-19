import os

from psycopg.conninfo import make_conninfo
from psycopg_pool import ConnectionPool


def _connection_string():
    return make_conninfo(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )


_pool = ConnectionPool(conninfo=_connection_string(), open=True)
_pool.wait(timeout=30)


def get_all_cars():
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cars")
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def get_cars_by_ids(ids):
    if not ids:
        return []
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cars WHERE id = ANY(%s)", (list(ids),))
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
