from fastapi import HTTPException
from pydantic import ValidationInfo
from pydantic_core import PydanticCustomError


class CommonValidators:

    @staticmethod
    def is_valid_size(value: str, info: ValidationInfo):
        if value is None or not (1 <= len(value) <= 32):
            raise PydanticCustomError(
                'invalid_length', 'El {value} proporcionado no cumple con los requisitos de longitud permitidos.', {'value': info.field_name})
    # status_code=400, detail="El valor proporcionado no cumple con los requisitos de longitud permitidos.")

    @staticmethod
    def is_ascii(username: str, info: ValidationInfo):
        if not username.isascii():
            raise HTTPException(
                status_code=400, detail="El valor proporcionado contiene caracteres no permitidos.")

    @staticmethod
    def verify_whitespaces(value: str, info: ValidationInfo):
        if value.isspace():
            raise HTTPException(
                status_code=400, detail="El valor proporcionado no puede contener solo espacios en blanco.")

    @staticmethod
    def verify_whitespace_count(value: str, info: ValidationInfo):
        if " " * 4 in value:
            raise HTTPException(
                status_code=400, detail="El valor proporcionado no puede contener más de 3 espacios consecutivos.")

    @classmethod
    def validate_string(cls, value: str, info: ValidationInfo):
        cls.is_valid_size(value, info)
        cls.is_ascii(value, info)
        cls.verify_whitespaces(value, info)
        cls.verify_whitespace_count(value, info)
        return value
