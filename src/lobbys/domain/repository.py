from abc import ABC, abstractmethod
from typing import Union
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest,GetLobbyResponse, GetLobbyData

class LobbyRepository(ABC):
    @abstractmethod
    def save(self, lobby: CreateLobbyRequest) -> LobbyResponse:
        pass

    @abstractmethod
    def save_lobby_player(self, playerID: int, roomID: int) -> None:
        pass

    @abstractmethod
    def get_all(self) -> list[GetLobbyResponse]:
        pass   

    @abstractmethod
    def get_data_lobby(self,lobby_id) -> GetLobbyData:
        pass
    
    @abstractmethod
    def find(self, roomID: int) -> bool:
        pass
    