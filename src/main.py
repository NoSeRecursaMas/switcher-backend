import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from src.players.infrastructure.api import router as players_router
from src.rooms.infrastructure.api import room_router as rooms_router
from src.rooms.infrastructure.api import websocket_router as websocket_router
from src.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Switcher Card Game",
    description="API for Switcher Card Game"
)

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

app.include_router(websocket_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
