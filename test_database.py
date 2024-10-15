import os
from urllib.parse import urlparse

import pytest
from sqlalchemy.orm import Session

from src.database import SessionLocal, engine, get_db


def test_get_db():
    db_gen = get_db()
    db: Session = next(db_gen)

    assert isinstance(db, Session)
    db.rollback()
    db_gen.close()


def test_session_local():
    session = SessionLocal()
    assert session.bind == engine
    session.close()
