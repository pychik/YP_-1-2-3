import os
import psycopg2
import pytz
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime as dt
from psycopg2.extensions import connection as _connection
from dotenv import load_dotenv, dotenv_values

# import global variables with path to database and path to repeatedly used modules
load_dotenv()
od = dotenv_values()
db_path = os.environ.get('DB_PATH_T')
m_path = os.environ.get('MODULE_PATH_T')

# setting path to repeatedly used modules
sys.path.insert(0, m_path)
from useful_sql import conn_context_sql
from useful_pg import conn_context_pg
from secondary import procedure_count, procedure_vals, dc_loader, set_env
from load_data import db_name, db_user, db_pass, db_host, db_port

# Declare DSL and Tables tuple
dsl = {'dbname': db_name,
       'user': db_user,
       'password': db_pass,
       'host': db_host,
       'port': db_port,
       'options': '-c search_path=content', }
tables = 'film_work', 'genre', 'genre_film_work', 'person', 'person_film_work'


def get_tables_sql(db_path: str, tables: tuple):
    """Return list object with rowcounts of sqlite tables"""
    with conn_context_sql(db_path) as sqlite_conn:
        curs = sqlite_conn.cursor()
        return procedure_count(curs, tables)


def get_tables_pg(dsl: dict, tables: tuple):
    """Return list object with rowcounts of postgress tables"""
    with conn_context_pg(dsl) as pgr_conn:
        with pgr_conn.cursor() as curs:
            return procedure_count(curs, tables)


def get_vals_sql(db_path: str, tables: tuple):
    """Return dict object with list of dataclasses. Contain values from sqlite db"""
    with conn_context_sql(db_path) as sqlite_conn:
        curs = sqlite_conn.cursor()
        return dc_loader(curs, tables, True)


def get_vals_pg(dsl: dict, tables: tuple):
    """Return dict object with list of dataclasses. Contain values from pg db"""
    with conn_context_pg(dsl) as pgr_conn:
        with pgr_conn.cursor() as curs:
            return dc_loader(curs, tables, False)


def test_sql_pg_db():
    sql = get_tables_sql(db_path, tables)
    pg = get_tables_pg(dsl, tables)
    for i in range(5):
        assert sql[i][0][0] == pg[i][0]['count']


def test_sql_pg_vals():
    sql_data = get_vals_sql(db_path, tables)
    pg_data = get_vals_pg(dsl, tables)
    assert sql_data == pg_data
