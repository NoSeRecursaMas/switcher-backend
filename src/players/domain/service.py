from fastapi import HTTPException
from src.shared.validators import CommonValidators


class DomainService:
    def is_valid_size(username: str):
        if len(username) < 1 or len(username) > 32:
            raise HTTPException(
                status_code=400, detail="El nombre debe tener entre 1 y 32 caracteres")

    def validate_username(username: str):
        CommonValidators.is_valid_size(username)
        CommonValidators.is_ascii(username)
        CommonValidators.verify_whitespaces(username)
        CommonValidators.verify_whitespace_count(username)
