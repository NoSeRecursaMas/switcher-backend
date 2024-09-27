from fastapi import FastAPI
from src.players.infrastructure.api import router as players_router
from src.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(players_router, prefix="/players", tags=["players"])
