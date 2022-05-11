from pydantic import BaseModel, validator
from typing import Optional


class PersonIds(BaseModel):
    ids: Optional[str]

    @validator("ids")
    def annotate(cls, v):
        data = v.replace("{", "").replace("}", "").split(",")
        return data


class FilmWork(BaseModel):
    id: str
    title: str
    description: Optional[str]
    rating: Optional[float]
    actors_names: Optional[list[str]]
    directors_names: Optional[list[str]]
    writers_names: Optional[list[str]]
    genres_names: Optional[list[str]]
    actors_ids: Optional[str]
    writers_ids: Optional[str]
