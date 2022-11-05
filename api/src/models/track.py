from lib.engine import get_sessionmaker
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy import TIMESTAMP

db_sessionmaker = get_sessionmaker()
Base = orm.declarative_base()


class Track(Base):
    __tablename__ = "tracks"
    spotify_id = Column(Text, primary_key=True)
    name = Column(Text)
    name_fts_string = Column(Text)

    all_artists_string = Column(Text)
    genres_string = Column(Text)
    tempo = Column(SmallInteger)
    popularity = Column(SmallInteger)

    main_artist_popularity = Column(SmallInteger)
    main_artist_followers = Column(Integer)
    danceability = Column(SmallInteger)
    energy = Column(SmallInteger)
    speechiness = Column(SmallInteger)

    acousticness = Column(SmallInteger)
    instrumentalness = Column(SmallInteger)

    liveness = Column(SmallInteger)
    valence = Column(SmallInteger)
    release_date = Column(Date)
    key = Column(SmallInteger)
    preview_url = Column(Text)
    updated_at = Column(TIMESTAMP)

    def count(self):
        with db_sessionmaker() as session:
            return session.query(Track).count()

    def get_updated_at_minmax(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(updated_at) as min, max(updated_at) as max FROM tracks"
            )
            result = session.execute(statement).fetchone()
            return result

    def get_created_at_minmax(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(created_at) as min, max(created_at) as max FROM tracks"
            )
            result = session.execute(statement).fetchone()
            return result

    def count_with_audiofeatures(self):
        with db_sessionmaker() as session:
            return (
                session.query(Track.spotify_id)
                .filter(Track.energy != None)
                .with_entities(func.count())
                .scalar()
            )

    def search(
        self,
        name="",
        genres_string="",
        tempo_min=80,
        tempo_max=210,
        popularity_min=0,
        popularity_max=100,
        main_artist_popularity_min=0,
        main_artist_popularity_max=100,
        main_artist_followers_min=0,
        main_artist_followers_max=50_000_000,
        danceability_min=0,
        danceability_max=1000,
        energy_min=0,
        energy_max=1000,
        speechiness_min=0,
        speechiness_max=1000,
        acousticness_min=0,
        acousticness_max=1000,
        instrumentalness_min=0,
        instrumentalness_max=1000,
        liveness_min=0,
        liveness_max=1000,
        valence_min=0,
        valence_max=1000,
        release_date="2020-12-01",
        key=1,
    ):
        with db_sessionmaker() as session:
            result = (
                session.query(Track)
                .filter(
                    Track.name_fts_string.like(f"%{name.lower()}%")
                    | Track.all_artists_string.like(f"%{name.lower()}%")
                )
                .filter(Track.genres_string.like(f"%{genres_string.lower()}%"))
                .filter(Track.tempo >= tempo_min)
                .filter(Track.tempo <= tempo_max)
                .filter(Track.popularity >= popularity_min)
                .filter(Track.popularity <= popularity_max)
                .filter(Track.main_artist_popularity >= main_artist_popularity_min)
                .filter(Track.main_artist_popularity <= main_artist_popularity_max)
                .filter(Track.main_artist_followers >= main_artist_followers_min)
                .filter(Track.main_artist_followers <= main_artist_followers_max)
                .filter(Track.danceability >= danceability_min)
                .filter(Track.danceability <= danceability_max)
                .filter(Track.energy >= energy_min)
                .filter(Track.energy <= energy_max)
                .filter(Track.speechiness >= speechiness_min)
                .filter(Track.speechiness <= speechiness_max)
                .filter(Track.acousticness >= acousticness_min)
                .filter(Track.acousticness <= acousticness_max)
                .filter(Track.instrumentalness >= instrumentalness_min)
                .filter(Track.instrumentalness <= instrumentalness_max)
                .filter(Track.liveness >= liveness_min)
                .filter(Track.liveness <= liveness_max)
                .filter(Track.valence >= valence_min)
                .filter(Track.valence <= valence_max)
                .filter(Track.release_date >= release_date)
                .filter(Track.key == key)
                .order_by(Track.release_date.desc())
                .order_by(Track.popularity.desc())
                .order_by(Track.spotify_id.asc())
                .limit(100)
                .all()
            )
            # print(x.result.compile(compile_kwargs={"literal_binds": True}))
            # exit(1)
            return result
