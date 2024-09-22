import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from src.players.infrastructure.api import router as players_router
from src.lobbys.infrastructure.api import lobby_router as lobbys_router
from src.lobbys.infrastructure.api import websocket_router as ws_router
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
def redirect_to_docs():
    return RedirectResponse(url="/docs/")

app.include_router(players_router, prefix="/players", tags=["players"])

app.include_router(lobbys_router, prefix="/lobbys", tags=["lobbys"])

app.include_router(ws_router, prefix="/ws", tags=["websockets"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",reload=True, port=8000)