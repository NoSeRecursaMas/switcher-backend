from pydantic import BaseModel, ValidationInfo, field_validator

from src.shared.validators import CommonValidators


class Player(BaseModel):
    playerID: int
    username: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str, info: ValidationInfo):
        return CommonValidators.validate_string(value, info)


class PlayerCreationRequest(BaseModel):
    username: str

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value: str, info: ValidationInfo):
        return CommonValidators.validate_string(value, info)


class PlayerID(BaseModel):
    playerID: int
