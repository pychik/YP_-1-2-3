import psycopg2
from contextlib import contextmanager
from dataclasses import fields, astuple
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from secondary import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


table_map = {'film_work': Filmwork,
             'genre': Genre,
             'genre_film_work': GenreFilmwork,
             'person': Person,
             'person_film_work': PersonFilmwork}


@contextmanager
def conn_context_pg(dsl: dict):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    yield conn
    conn.close()


def save_table(pg_conn: _connection, cur: psycopg2.extensions.cursor, table: str, data_list: list):
    """
    Save data_list  with dataclass objects to pg_DB table
    """
    # extract dataclass obj for further keys retrieving
    model_dataclass = table_map[table]

    # get column names from dataclass object
    columns = ','.join(at for at in model_dataclass.__annotations__.keys())

    # get %s+ string
    columns_subs = ','.join(['%s' for _ in range(len(columns.split(',')))])

    # forming args expression  to insert
    args = ','.join(cur.mogrify(f'({columns_subs})', astuple(item)).decode('utf-8') for item in data_list)
    try:
        cur.execute(f"""
                           INSERT INTO {table} ({columns})
                           VALUES {args} ON CONFLICT (id) DO NOTHING
                           """)
        pg_conn.commit()
    except psycopg2.Error as e:
        raise e


def create_fg_index(pg_conn: _connection, cur: psycopg2.extensions.cursor):
    filmwork_genre_index = 'CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre ' \
                           'ON genre_film_work (film_work_id, genre_id);'
    cur.execute(filmwork_genre_index)
    pg_conn.commit()


def create_fpr_index(pg_conn: _connection, cur: psycopg2.extensions.cursor):
    filmwork_person_role_index = 'CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role ' \
                                 'ON person_film_work (film_work_id, person_id, role);'
    cur.execute(filmwork_person_role_index)
    pg_conn.commit()
