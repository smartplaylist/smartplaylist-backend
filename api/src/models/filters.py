from typing import Optional
from pydantic import BaseModel, Field

class TrackFilterParams(BaseModel):
    """
    Pydantic model for track search filter parameters.
    Used as a dependency in API endpoints to clean up the endpoint signature
    and leverage FastAPI's automatic validation.
    """
    name: Optional[str] = Field(default="", description="Text search for track name or artist")
    genres: Optional[str] = Field(default="", description="Text search for genres")

    tempo: tuple[int, int] = Field(default=(0, 250), description="Tempo range")
    popularity: tuple[int, int] = Field(default=(0, 100), description="Popularity range")
    main_artist_popularity: tuple[int, int] = Field(default=(0, 100), description="Main artist popularity range")
    main_artist_followers: tuple[int, int] = Field(default=(0, 100000000), description="Main artist followers range")
    danceability: tuple[float, float] = Field(default=(0.0, 1.0), description="Danceability range")
    energy: tuple[float, float] = Field(default=(0.0, 1.0), description="Energy range")
    speechiness: tuple[float, float] = Field(default=(0.0, 1.0), description="Speechiness range")
    acousticness: tuple[float, float] = Field(default=(0.0, 1.0), description="Acousticness range")
    instrumentalness: tuple[float, float] = Field(default=(0.0, 1.0), description="Instrumentalness range")
    liveness: tuple[float, float] = Field(default=(0.0, 1.0), description="Liveness range")
    valence: tuple[float, float] = Field(default=(0.0, 1.0), description="Valence range")
    key: tuple[int, int] = Field(default=(0, 11), description="Key range")

    release_date_start: Optional[str] = Field(default="1900-01-01", description="Start of release date range (YYYY-MM-DD)")
    release_date_end: Optional[str] = Field(default="9999-12-31", description="End of release date range (YYYY-MM-DD)")

    def to_dict(self):
        """
        Converts the model to a dictionary suitable for the repository,
        handling the composition of range tuples.
        """
        return {
            "name": self.name,
            "genres": self.genres,
            "tempo": self.tempo,
            "popularity": self.popularity,
            "main_artist_popularity": self.main_artist_popularity,
            "main_artist_followers": self.main_artist_followers,
            "danceability": (self.danceability[0] * 100, self.danceability[1] * 100), # Scale to 0-100 as in original DB
            "energy": (self.energy[0] * 100, self.energy[1] * 100),
            "speechiness": (self.speechiness[0] * 100, self.speechiness[1] * 100),
            "acousticness": (self.acousticness[0] * 100, self.acousticness[1] * 100),
            "instrumentalness": (self.instrumentalness[0] * 100, self.instrumentalness[1] * 100),
            "liveness": (self.liveness[0] * 100, self.liveness[1] * 100),
            "valence": (self.valence[0] * 100, self.valence[1] * 100),
            "key": self.key,
            "release": (self.release_date_start, self.release_date_end)
        }
