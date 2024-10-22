from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.database import Base, engine
from src.games.infrastructure.api import router as games_router
from src.players.infrastructure.api import router as players_router
from src.rooms.infrastructure.api import router as rooms_router
from src.rooms.infrastructure.websocket import ws_manager_room, ws_manager_room_list

app = FastAPI(title="Switcher Card Game", description="API for Switcher Card Game")


Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ws_manager_room_list.clean_up()
    ws_manager_room.clean_up()
    yield
    ws_manager_room_list.clean_up()
    ws_manager_room.clean_up()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def redirect_to_documentation():
    return RedirectResponse(url="/docs/")


app.include_router(players_router, prefix="/players", tags=["players"])

app.include_router(rooms_router, prefix="/rooms", tags=["rooms"])


app.include_router(games_router, prefix="/games", tags=["games"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
