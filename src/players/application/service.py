from sqlalchemy.orm import Session
from src.players.domain.model import Player
from src.players.domain.service import PlayerDomaineService
from src.players.domain.repository import PlayerRepository

class PlayerService():
    def __init__(self, player_repository: PlayerRepository):
        self.player_repository = player_repository 

    def create_player_use_case(self, player_name: str) -> Player:

        
        PlayerDomaineService.validate_length_name(player_name)
        PlayerDomaineService.validate_is_ascii(player_name)
        
        player = Player(name=player_name)
        
        return self.player_repository.save(player)