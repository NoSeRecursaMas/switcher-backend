from fastapi import FastAPI
from src.players.infrastructure.api import router as players_router
from src.database import engine
from src.players.domain.model import Base
from sqlalchemy.ext.declarative import declarative_base

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(players_router, prefix="/players", tags=["player"] )