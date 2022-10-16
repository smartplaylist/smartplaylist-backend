import os
from sqlalchemy import Column, Integer, Text, SmallInteger, Date, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker


def get_sessionmaker():

    # Update connection string information
    host = os.environ["POSTGRES_HOST"]
    dbname = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    # Construct connection string
    conn_string = "postgresql://{0}:{1}@{2}/{3}".format(user, password, host, dbname)
    return sessionmaker(bind=create_engine(conn_string))


db_sessionmaker = get_sessionmaker()

Base = declarative_base()


class CRUD:
    def save(self):
        if self.spotify_id == None:
            with db_sessionmaker() as session:
                session.add(self)
                return session.commit()

    def destroy(self):
        with db_sessionmaker() as session:
            session.delete(self)
            return session.commit()


class Track(Base, CRUD):
    __tablename__ = "tracks"
    spotify_id = Column(Text, primary_key=True)
    name = Column(Text)
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

    def count(self):
        with db_sessionmaker() as session:
            return session.query(Track).count()

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
        all_artists_string="",
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
        release_date="2021-12-01",
        key=1,
    ):
        with db_sessionmaker() as session:
            x = (
                session.query(Track)
                .filter(
                    Track.name.ilike(f"%{name}%")
                    | Track.all_artists_string.ilike(f"%{name}%")
                )
                .filter(Track.genres_string.ilike(f"%{genres_string}%"))
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
            # print(x.statement.compile(compile_kwargs={"literal_binds": True}))
            # os._exit(1)
            return x
