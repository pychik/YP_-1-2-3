import psycopg2

from dataclasses import dataclass
from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from .connections import DSL, URL, JSON_STORE
from .decorators import backoff
from .state_processor import BaseStorage, JsonFileStorage


CHUNK_SIZE = 100


@dataclass
class ConnectStorages:
    storage: BaseStorage = None
    pg_conn: _connection = None
    es_client: Elasticsearch = None


class Storages:
    @property
    def storages(self) -> ConnectStorages:
        return ConnectStorages(
            storage=JsonFileStorage(JSON_STORE),
            pg_conn=psycopg2.connect(**DSL, cursor_factory=DictCursor),
            es_client=Elasticsearch(URL),
        )

    @backoff()
    def get_es_client(self):
        return self.storages.es_client

    @backoff()
    def get_pg_conn(self) -> _connection:
        return self.storages.pg_conn
