import sqlite3
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime
from dateutil.parser import parse
from useful_sql import conn_context_sql
BATCH_SIZE = 5000
SELECT_ALL = '*'
SELECT_COUNT = 'COUNT (*)'


@dataclass
class Filmwork:
    id: str = None
    title: str = None
    description: str = None
    creation_date: date = None
    file_path: str = None
    rating: float = None
    type: str = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Genre:
    id: str = None
    name: str = None
    description: str = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class GenreFilmwork:
    id: str = None
    film_work_id: str = None
    genre_id: str = None
    created_at: datetime = None


@dataclass
class Person:
    id: str = None
    full_name: str = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class PersonFilmwork:
    id: str = None
    film_work_id: str = None
    person_id: str = None
    role: str = None
    created_at: datetime = None


def procedure_count(curs, tables: tuple):
    """
    Return tuple of Count of Rows from each table
    sqlite and pg DB
    """

    data_list = []
    for t in tables:
        data_list.append(tuple(extract_data_from(curs, t, SELECT_COUNT)))
    return tuple(data_list)


def procedure_vals(curs, tables: tuple):
    """
    Return tuple of tablesorted rows data from sqlite and pg db
    """

    data_list = []
    for t in tables:
        data_list.append(tuple(extract_data_from(curs, t, SELECT_ALL)))

    return tuple(data_list)


def dc_loader(curs, tables: tuple, flag: bool):
    """
    Return Dict object tablesorted with dataclass values from  db
    sqlite created_at and updated_at fields differ from pg
    So we need to use django_utilse.parser.parse and we process them with my_parse func
    """
    data = {}
    filmwork_raw, genre_raw, gf_raw, person_raw, pf_raw = procedure_vals(curs, tables)

    # sorting raw_data to dataclass data and packing it to dict
    data["film_work"] = [Filmwork(d["id"], d["title"], d["description"], d["creation_date"],
                                  d["file_path"], d["rating"], d["type"], my_parse(d["created_at"], flag),
                                  my_parse(d["updated_at"], flag)) for d in filmwork_raw]
    data["genre"] = [Genre(g["id"], g["name"], g["description"],
                           my_parse(g["created_at"], flag), my_parse(g["updated_at"], flag)) for g in genre_raw]
    data["genre_film_work"] = [GenreFilmwork(gf["id"], gf["film_work_id"], gf["genre_id"],
                                             my_parse(gf["created_at"], flag)) for gf in gf_raw]
    data["person"] = [Person(p["id"], p["full_name"], my_parse(p["created_at"], flag),
                             my_parse(p["updated_at"], flag)) for p in person_raw]
    data["person_film_work"] = [PersonFilmwork(pf["id"], pf["film_work_id"], pf["person_id"], pf["role"],
                                               my_parse(pf["created_at"], flag)) for pf in pf_raw]
    return data


def set_env(dict_vars: OrderedDict):
    mt = dict_vars.values()
    return tuple(mt)[1:]


def my_parse(obj: str, flag: bool):
    if flag:
        return parse(obj)
    else:
        return obj


def extract_data_from(curs: sqlite3.Cursor, table: str, operator: str):
    try:
        curs.execute(f'SELECT {operator} FROM {table}')
    except sqlite3.Error as e:
        raise e
    while True:
        rows = curs.fetchmany(size=BATCH_SIZE)
        if not rows:
            break
        yield from rows
    return rows
