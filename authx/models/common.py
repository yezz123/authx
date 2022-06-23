from datetime import datetime

from pydantic import BaseConfig, BaseModel


def convert_field_to_camel_case(string: str) -> str:
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )


def set_created_at(v):
    return datetime.utcnow()


def set_last_login(v, values):
    return values.get("created_at")


class DefaultModel(BaseModel):
    """Base model for all models"""

    class Config(BaseConfig):
        """Config for pydantic models"""

        allow_population_by_field_name = True
        alias_generator = convert_field_to_camel_case
