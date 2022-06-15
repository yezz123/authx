from typing import Union

import socketio
from fastapi import FastAPI


class Socket:
    def __init__(
        self,
        app: FastAPI,
        mount_location: str = "/ws",
        socketio_path: str = "socket.io",
        cors_allowed_origins: Union[str, list] = "*",
        async_mode: str = "asgi",
    ) -> None:
        self._socket = socketio.AsyncServer(
            async_mode=async_mode, cors_allowed_origins=cors_allowed_origins
        )
        self._app = socketio.ASGIApp(
            socketio_server=self._socket, socketio_path=socketio_path
        )

        app.mount(mount_location, self._app)
        app.sio = self._socket

    def is_asyncio_based(self) -> bool:
        return True

    @property
    def on(self):
        return self._socket.on

    @property
    def attach(self):
        return self._socket.attach

    @property
    def emit(self):
        return self._socket.emit

    @property
    def send(self):
        return self._socket.send

    @property
    def call(self):
        return self._socket.call

    @property
    def close_room(self):
        return self._socket.close_room

    @property
    def get_session(self):
        return self._socket.get_session

    @property
    def save_session(self):
        return self._socket.save_session

    @property
    def session(self):
        return self._socket.session

    @property
    def disconnect(self):
        return self._socket.disconnect

    @property
    def handle_request(self):
        return self._socket.handle_request

    @property
    def start_background_task(self):
        return self._socket.start_background_task

    @property
    def sleep(self):
        return self._socket.sleep

    @property
    def enter_room(self):
        return self._socket.enter_room

    @property
    def leave_room(self):
        return self._socket.leave_room
