from typing import Optional

from fastapi import HTTPException
from pydantic import ValidationInfo
from pydantic_core import PydanticCustomError


class CommonValidators:
    @staticmethod
    def validate_length(value: str, info: ValidationInfo):
        if value is None or not (1 <= len(value) <= 32):
            raise PydanticCustomError(
                "invalid_length",
                "El {value} proporcionado no cumple con los requisitos de longitud permitidos.",
                {"value": info.field_name},
            )

    @staticmethod
    def validate_no_only_whitespaces(username: str, info: ValidationInfo):
        if not username.isascii():
            raise PydanticCustomError(
                "invalid_length",
                "El {value} proporcionado contiene caracteres no permitidos.",
                {"value": info.field_name},
            )

    @staticmethod
    def verify_whitespaces(value: str, info: ValidationInfo):
        if value.isspace():
            raise PydanticCustomError(
                "invalid_length",
                "El {value} proporcionado no puede contener solo espacios en blanco.",
                {"value": info.field_name},
            )

    @staticmethod
    def verify_whitespace_count(value: str, info: ValidationInfo):
        if " " * 4 in value:
            raise PydanticCustomError(
                "invalid_length",
                "El {value} proporcionado no puede contener más de 3 espacios consecutivos.",
                {"value": info.field_name},
            )

    @staticmethod
    def verify_no_special_characters(value: Optional[str], info: ValidationInfo):
        if value is not None and value == "":
            raise PydanticCustomError(
                "invalid_length",
                "El {value} proporcionado no puede estar vacío.",
                {"value": info.field_name},
            )
        if value and not value.isalnum():
            raise PydanticCustomError(
                "invalid_length",
                "El {value} proporcionado contiene caracteres no permitidos.",
                {"value": info.field_name},
            )

    @staticmethod
    def validate_password_length(value: Optional[str], info: ValidationInfo):
        if value is not None and not (0 < len(value) <= 16):
            raise PydanticCustomError(
                "invalid_length",
                "El {value} proporcionado no cumple con los requisitos de longitud permitidos.",
                {"value": info.field_name},
            )

    @classmethod
    def validate_string(cls, value: str, info: ValidationInfo):
        cls.validate_length(value, info)
        cls.validate_no_only_whitespaces(value, info)
        cls.verify_whitespaces(value, info)
        cls.verify_whitespace_count(value, info)
        return value

    @classmethod
    def validate_password(cls, value: Optional[str], info: ValidationInfo):
        cls.validate_password_length(value, info)
        cls.verify_no_special_characters(value, info)
        return value
