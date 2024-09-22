from fastapi import HTTPException


class CommonValidators:

    @staticmethod
    def is_valid_size(value: str):
        print("aaaaaaaaaaaaaaaaaaaaaaaa", value)
        if value is None or len(value) < 1 or len(value) > 32:
            raise HTTPException(
                status_code=400, detail="El valor proporcionado no cumple con los requisitos de longitud permitidos.")

    @staticmethod
    def is_ascii(username: str):
        if not username.isascii():
            raise HTTPException(
                status_code=400, detail="El valor proporcionado contiene caracteres no permitidos.")
