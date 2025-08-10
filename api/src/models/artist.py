from sqlalchemy import Boolean, Column, SmallInteger, Text, TIMESTAMP, text, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Artist(Base):
    __tablename__ = "artists"
    spotify_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    popularity = Column(SmallInteger, nullable=False)
    followers = Column(Integer, nullable=False)
    genres = Column(ARRAY(Text), nullable=False)
    genres_string = Column(Text, nullable=False)
    total_albums = Column(SmallInteger, nullable=False)
    albums_updated_at = Column(TIMESTAMP, nullable=True)
    related_to = Column(Text, nullable=True)
    related_to_spotify_id = Column(Text, nullable=True)
    has_related = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
    updated_at = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
