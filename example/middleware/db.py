import typing

from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import create_session
from starlette.config import Config

config = Config(".env.sample")


class DB:
    def __init__(self) -> None:
        self._engine = create_engine(config("DATABASE_URL"))
        _metatable = Table(
            "users",
            MetaData(bind=self._engine),
            *[
                Column("id", String, primary_key=True, nullable=False),
                Column("token", JSON),
            ],
        )
        _metatable.create(checkfirst=True)

        Base = automap_base(metadata=_metatable.metadata)
        Base.prepare()

        self._session = create_session(bind=self._engine)
        self._User = Base.classes.users

    def put(self, user_id: str, token: typing.Dict[str, typing.Any]) -> None:
        self._session.merge(self._User(id=user_id, token=dict(token)))
        self._session.flush()

    def get(self, user_id: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        result = (
            self._session.query(self._User).filter(self._User.id == user_id).first()
        )
        if result is not None:
            return result.token

    def delete(self, user_id: str) -> None:
        self._session.query(self._User).filter(self._User.id == user_id).delete()
        self._session.flush()
