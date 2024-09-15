from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


sqlite_file_url = '../database.sqlite'
base_dir = os.path.dirname(os.path.realpath(__file__)) 
database_url = f"sqlite:///{os.path.join(base_dir,sqlite_file_url)}"

# Maneja conexion de BD
engine = create_engine(database_url, echo=True)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()