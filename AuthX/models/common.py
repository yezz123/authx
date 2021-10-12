from datetime import datetime

from pydantic import BaseConfig, BaseModel


def convert_field_to_camel_case(string: str) -> str:
    # TODO: implement
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )


def set_created_at(v):
    """
    Set created_at field to current datetime

    Args:
        v (object): pydantic model object

    Returns:
        datetime: current datetime
    """
    return datetime.utcnow()


def set_last_login(v, values):
    """
    Set last_login field to current datetime

    Args:
        v (object): pydantic model object
        values (dict): values to be set

    Returns:
        datetime: current datetime
    """
    return values.get("created_at")


class DefaultModel(BaseModel):
    """
    Base model for all models

    Args:
        BaseModel (pydantic.BaseModel): Base model for all models
    """

    class Config(BaseConfig):
        """
        Config for pydantic models

        Args:
            BaseConfig: pydantic config
        """

        allow_population_by_field_name = True
        alias_generator = convert_field_to_camel_case
