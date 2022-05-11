import json
import logging
import sys

from datetime import datetime
from elasticsearch.helpers import streaming_bulk
from typing import Coroutine

from .config import CHUNK_SIZE, Storages
from .decorators import coroutine
from .es_indexes import INDEX, INDEX_SETTINGS
from .models import FilmWork, PersonIds
from .queries import SQL
from .state_processor import BaseStorage, State

logger = logging.getLogger(__name__)


def producer(target: Coroutine, *, cursor, storage: BaseStorage):
    """ Build 'pages' of data  divided by CHUNK_SIZE from PG database
        Transmit them to transformer
    """
    state_proc = State(storage=storage)
    default_value = str(datetime(year=2021, month=1, day=1))
    current_state = state_proc.get_state("film_work", default_value)
    cursor.execute(SQL, (current_state,))

    while True:
        page = cursor.fetchmany(CHUNK_SIZE)
        if not page:
            break
        state_set = (state_proc, str(page[-1]["updated_at"]))
        transform_pack = (page, state_set)
        target.send(transform_pack)


@coroutine
def transform(target: Coroutine):
    """Receive  'pages' of data
       Transform them to dataclass objects
       Sends to loader
    """
    while True:
        page, state_set = (yield)
        if not page:
            break
        movies = [FilmWork(**data) for data in page]
        load_pack = (movies, state_set)

        target.send(load_pack)


class MakeData:
    def process(self, list_data) -> dict:
        """
        Return ES index Readable structure from list
        """

        for row in list_data:
            data_pack = {
                "_id": row.id,
                "_index": INDEX,
                "_type": "_doc",
                "_source":  json.dumps({
                    "id": row.id,
                    "imdb_rating": row.rating,
                    "genre": row.genres_names,
                    "title": row.title,
                    "description": row.description,
                    "director": row.directors_names if row.directors_names else [],
                    "actors_names": row.actors_names,
                    "writers_names": row.writers_names,
                    "actors": [
                        {"id": _id, "name": name}
                        for _id, name in zip(PersonIds(ids=row.actors_ids).ids, row.actors_names)]
                    if row.actors_ids else None,
                    "writers": [
                        {"id": _id, "name": name}
                        for _id, name in zip(PersonIds(ids=row.writers_ids).ids, row.writers_names,)
                    ]
                    if row.writers_ids else None,
                }),
            }
            yield data_pack


@coroutine
def loader(es_client):
    """
    Receive data from transformer,
    Load data to ES
    """
    while True:
        movies, state_set = (yield)
        if not movies:
            break
        es_gen_data = MakeData()
        successes = 0
        failed = 0
        for ok, response in streaming_bulk(
            es_client,
            es_gen_data.process(movies),
            chunk_size=CHUNK_SIZE,
        ):
            if not ok:
                failed += 1
            else:
                successes += 1
                # state_set[0] is our State instance, state_set[1] is a state_value to store
                state_set[0].set_state(key="film_work", value=state_set[1])
        print(f"Indexed documents success {successes}, fails {failed}")


class ETL(Storages):
    def run(self):
        try:
            client = self.get_es_client()
            client.indices.create(
                index=INDEX,
                body=INDEX_SETTINGS,
                ignore=400,
            )
            cursor = self.get_pg_conn().cursor()
            # Run infinite cycle for ETL
            while True:
                loader_p = loader(client)
                merger = transform(loader_p)
                producer(
                    merger, cursor=cursor, storage=self.storages.storage
                )
        except KeyboardInterrupt:
            self.get_pg_conn().close()
            logger.error("\nETL PROCESS ended by user CTRL-C action")
        except Exception as e:
            logger.exception(f"Got an Exception: {e}")
        sys.exit(0)
