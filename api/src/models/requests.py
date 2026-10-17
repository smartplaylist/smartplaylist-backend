from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, validator

# The oldest date Postgres and Python agree on; used when the website sends no
# release filter, so the query keeps a single shape.
EARLIEST_RELEASE = date(1, 1, 1)


class RangeParam(BaseModel):
    """Inclusive `min,max` filter on a non-negative column.

    No upper bound on purpose: tempo goes past 200 BPM and the website sends
    main artist followers up to 50,000,000.
    """

    min_val: int = Field(ge=0)
    max_val: int = Field(ge=0)

    @validator("max_val")
    def max_must_not_be_below_min(cls, v, values):
        if "min_val" in values and v < values["min_val"]:
            raise ValueError("max_val must be greater than or equal to min_val")
        return v

    @classmethod
    def from_string(cls, value: str, default_min: int = 0, default_max: int = 100):
        if not value:
            return cls(min_val=default_min, max_val=default_max)

        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError(f"Range must be 'min,max': {value}")
        try:
            return cls(min_val=int(parts[0]), max_val=int(parts[1]))
        except ValueError as e:
            raise ValueError(f"Invalid range: {value}") from e

    def bounds(self):
        return [self.min_val, self.max_val]


class KeyParam(BaseModel):
    """Musical key range; `any` stands for the whole 0-12 span."""

    min_val: int = Field(ge=0, le=12)
    max_val: int = Field(ge=0, le=12)

    @validator("max_val")
    def max_must_not_be_below_min(cls, v, values):
        if "min_val" in values and v < values["min_val"]:
            raise ValueError("max_val must be greater than or equal to min_val")
        return v

    @classmethod
    def from_string(cls, value: str):
        if not value:
            return cls(min_val=0, max_val=12)

        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError(f"Key range must be 'min,max': {value}")
        try:
            return cls(
                min_val=0 if parts[0] == "any" else int(parts[0]),
                max_val=12 if parts[1] == "any" else int(parts[1]),
            )
        except ValueError as e:
            raise ValueError(f"Invalid key range: {value}") from e

    def bounds(self):
        return [self.min_val, self.max_val]


class ReleaseDateParam(BaseModel):
    """`rel=YYYY-MM-DD`: tracks released on or after that day.

    Kept as a full date because the website lets you pick a day, not a year.
    """

    after: date = EARLIEST_RELEASE

    @classmethod
    def from_string(cls, value: str):
        if not value:
            return cls()
        try:
            return cls(after=date.fromisoformat(value.strip()))
        except ValueError as e:
            raise ValueError(f"Release date must be YYYY-MM-DD: {value}") from e


class TrackSearchParams(BaseModel):
    tempo: RangeParam
    popularity: RangeParam
    main_artist_popularity: RangeParam
    main_artist_followers: RangeParam
    danceability: RangeParam
    energy: RangeParam
    speechiness: RangeParam
    acousticness: RangeParam
    instrumentalness: RangeParam
    liveness: RangeParam
    valence: RangeParam
    release: ReleaseDateParam
    key: KeyParam

    genres: str = Field(default="", max_length=500)
    name: str = Field(default="", max_length=200)
    limit: int = Field(default=250, ge=1, le=1000)
    # The website sends `rel,des`; the search orders by release date either way.
    order: str = Field(default="rel,desc", regex="^(rel|pop|name),(asc|desc?)$")

    @classmethod
    def from_query_params(
        cls,
        tem: str = "0,100",
        pop: str = "0,100",
        map: str = "0,100",
        maf: str = "0,100",
        dan: str = "0,100",
        ene: str = "0,100",
        spe: str = "0,100",
        aco: str = "0,100",
        ins: str = "0,100",
        liv: str = "0,100",
        val: str = "0,100",
        rel: str = "",
        key: str = "0,12",
        gen: str = "",
        nam: str = "",
        limit: int = 250,
        order: str = "rel,desc",
    ):
        return cls(
            tempo=RangeParam.from_string(tem),
            popularity=RangeParam.from_string(pop),
            main_artist_popularity=RangeParam.from_string(map),
            main_artist_followers=RangeParam.from_string(maf),
            danceability=RangeParam.from_string(dan),
            energy=RangeParam.from_string(ene),
            speechiness=RangeParam.from_string(spe),
            acousticness=RangeParam.from_string(aco),
            instrumentalness=RangeParam.from_string(ins),
            liveness=RangeParam.from_string(liv),
            valence=RangeParam.from_string(val),
            release=ReleaseDateParam.from_string(rel),
            key=KeyParam.from_string(key),
            genres=gen.strip(","),
            name=nam.strip(","),
            limit=limit,
            order=order,
        )

    def filters(self):
        """Keyword arguments shared by Track.search and Track.count."""
        return {
            "name": self.name,
            "genres": self.genres,
            "tempo": self.tempo.bounds(),
            "popularity": self.popularity.bounds(),
            "main_artist_popularity": self.main_artist_popularity.bounds(),
            "main_artist_followers": self.main_artist_followers.bounds(),
            "danceability": self.danceability.bounds(),
            "energy": self.energy.bounds(),
            "speechiness": self.speechiness.bounds(),
            "acousticness": self.acousticness.bounds(),
            "instrumentalness": self.instrumentalness.bounds(),
            "liveness": self.liveness.bounds(),
            "valence": self.valence.bounds(),
            "release": [self.release.after],
            "key": self.key.bounds(),
        }


class SavePlaylistRequest(BaseModel):
    """Body of POST /user/save_playlist, in the shape the website sends it."""

    access_token: str = Field(..., min_length=1, max_length=500, alias="accessToken")
    # Spotify caps a playlist at 10,000 tracks.
    track_ids: List[str] = Field(..., min_items=1, max_items=10000, alias="ids")
    playlist_name: Optional[str] = Field(None, max_length=100)

    @validator("track_ids", each_item=True)
    def track_id_must_look_like_a_spotify_id(cls, v):
        # Spotify IDs are 22 base62 characters; the slack catches truncation
        # without guessing at the exact alphabet.
        if not 10 <= len(v) <= 30:
            raise ValueError(f"Invalid track ID: {v}")
        return v

    class Config:
        allow_population_by_field_name = True
