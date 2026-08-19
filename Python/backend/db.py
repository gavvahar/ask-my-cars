from psycopg_pool import ConnectionPool

from .db_config import connection_string

_pool = ConnectionPool(conninfo=connection_string(), open=True)
_pool.wait(timeout=30)


def get_all_cars():
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cars")
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]


def get_cars_by_ids(ids):
    if not ids:
        return []
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cars WHERE id = ANY(%s)", (list(ids),))
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]


def execute(sql, params=None):
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


def search_cars(query, limit=8):
    sql = """
        SELECT *, ts_rank(search_vector, websearch_to_tsquery('english', %s)) AS rank
        FROM cars
        WHERE search_vector @@ websearch_to_tsquery('english', %s)
        ORDER BY rank DESC
        LIMIT %s
    """
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (query, query, limit))
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]


CARS_COLUMNS = (
    "id, make, model, year, engine_fuel_type, engine_hp, engine_cylinders, "
    "transmission_type, driven_wheels, number_of_doors, market_category, "
    "vehicle_size, vehicle_style, highway_mpg, city_mpg, popularity, msrp"
)


def get_cars_where_not_embedded():
    sql = f"SELECT {CARS_COLUMNS} FROM cars WHERE embedded_at IS NULL"
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]


def mark_embedded(ids):
    sql = "UPDATE cars SET embedded_at = NOW() WHERE id = ANY(%s)"
    with _pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, ([int(i) for i in ids],))
