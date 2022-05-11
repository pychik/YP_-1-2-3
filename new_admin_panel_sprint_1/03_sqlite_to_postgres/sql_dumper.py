import sqlite3
from secondary import BATCH_SIZE
from secondary import dc_loader, SELECT_ALL
 

class SQLiteLoader:

    def __init__(self, connection):
        self.conn = connection
    
    def load_movies(self):
        """
            Return dict object,
            that contains Dict object with
            Dataclass values sorted by tables
            from all tables we request in our DB
        """

        # define tables for select query
        tables = 'film_work', 'genre', 'genre_film_work', 'person', 'person_film_work'

        # retrieve data from sqlite using context manager option
        curs = self.conn.cursor()
        return dc_loader(curs, tables, True)
