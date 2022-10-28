import os

from lib.engine import get_sessionmaker
from sqlalchemy import (
    TIMESTAMP,
    Column,
    Date,
    Integer,
    SmallInteger,
    Text,
    func,
    text,
)
from sqlalchemy.orm import declarative_base

db_sessionmaker = get_sessionmaker()
Base = declarative_base()


class Artist(Base):
    __tablename__ = "artists"
    spotify_id = Column(Text, primary_key=True)
    name = Column(Text)
    updated_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)

    def count(self):
        with db_sessionmaker() as session:
            return session.query(Artist).count()

    def get_updated_at_minmax(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(updated_at) as min, max(updated_at) as max FROM artists"
            )
            result = session.execute(statement).fetchone()
            return result

    def get_created_at_minmax(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(created_at) as min, max(created_at) as max FROM artists"
            )
            result = session.execute(statement).fetchone()
            return result

    def get_album_updated_at_minmax(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(albums_updated_at) as min, max(albums_updated_at) as max FROM artists"
            )
            result = session.execute(statement).fetchone()
            return result
