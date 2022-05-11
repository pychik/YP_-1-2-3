import os
import sqlite3
import psycopg2
from dotenv import load_dotenv, dotenv_values
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from pg_saver import PostgresSaver
from sql_dumper import SQLiteLoader
from secondary import set_env
from useful_sql import conn_context_sql
from useful_pg import conn_context_pg

# getting and setting environment variables
load_dotenv()
od = dotenv_values()
db_path, db_name, db_user, db_pass, db_host, db_port = set_env(od)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Main method of loading data from sqlite to postgress"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)
    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {'dbname': db_name,
           'user': db_user,
           'password': db_pass,
           'host': db_host,
           'port': db_port,
           'options': '-c search_path=content', }
    with conn_context_sql(db_path) as sqlite_conn, conn_context_pg(dsl) as pgr_conn:
        load_from_sqlite(sqlite_conn, pgr_conn)
