from pydantic import BaseModel, field_validator
from src.shared.validators import CommonValidators


def validate_username(value: str) -> str:
    CommonValidators.is_valid_size(value)
    CommonValidators.is_ascii(value)
    CommonValidators.verify_whitespaces(value)
    CommonValidators.verify_whitespace_count(value)
    return value
