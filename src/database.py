import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

sqlite_file_url = "../database.sqlite"
base_dir = os.path.dirname(os.path.realpath(__file__))
database_url = f"sqlite:///{os.path.join(base_dir, sqlite_file_url)}"

engine = create_engine(database_url, echo=False, pool_size=100, max_overflow=100)


SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
