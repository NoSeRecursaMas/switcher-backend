from fastapi import HTTPException
from src.shared.validators import CommonValidators


class DomaineService:

    def validate_username(username: str):
        CommonValidators.is_valid_size(username)
        CommonValidators.is_ascii(username)
        CommonValidators.verify_whitespaces(username)
        CommonValidators.verify_whitespace_count(username)
