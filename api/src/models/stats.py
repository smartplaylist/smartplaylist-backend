from lib import engine
from sqlalchemy import Column
from sqlalchemy import text
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import declarative_base

db_sessionmaker = engine.get_sessionmaker()
Base = declarative_base()


class Stats(Base):
    __tablename__ = "db_stats"
    created_at = Column(TIMESTAMP, primary_key=True)

    def get_stats(self):
        with db_sessionmaker() as session:
            statement = text("SELECT * FROM db_stats ORDER BY created_at DESC LIMIT 1")
            result = session.execute(statement).fetchone()
            return result if result != None else {}
