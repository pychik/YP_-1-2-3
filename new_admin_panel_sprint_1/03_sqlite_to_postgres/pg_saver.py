from datetime import datetime
from useful_pg import save_table, create_fg_index, create_fpr_index


class PostgresSaver:

    def __init__(self, pg_conn):
        self.pg_conn = pg_conn

    def save_all_data(self, data: dict):
        """
            Save received dict object,
            to assigned tables and creates(with Existence check)
            new UNIQUE INDEXES from sqlite DB
        """
        with self.pg_conn.cursor() as cur:
            for k, v in data.items():
                save_table(self.pg_conn, cur, k, v)
            create_fg_index(self.pg_conn, cur)
            create_fpr_index(self.pg_conn, cur)
