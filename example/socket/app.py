import asyncio
import json
from contextlib import suppress

import aiodocker
from fastapi import FastAPI

from authx import AuthXSocket


class GlobalSub:
    def __init__(self):
        self.subscribers = {}

    async def emit(self, event):
        for handler in self.subscribers.values():
            with suppress(Exception):
                await handler("docker_event", json.dumps(event))

    def sub(self, sid, handler):
        self.subscribers[sid] = handler

    def unsub(self, sid):
        del self.subscribers[sid]


def bind_sio(app, registry):
    @app.sio.on("connect")
    async def handle_connect(sid, *args, **kwargs):
        registry.sub(sid, app.sio.emit)

    @app.sio.on("disconnect")
    async def handle_disconnect(sid):
        registry.unsub(sid)


async def listen(registry, docker):
    sub = docker.events.subscribe()
    while True:
        event = await sub.get()
        if not event:
            break
        event.pop("time")
        await registry.emit(event)


def print_routes(smth):
    if hasattr(smth, "routes"):
        for route in getattr(smth, "routes"):
            print_routes(route)
        if hasattr(smth, "path"):
            print(f"NR: {smth.path} => {smth.routes}")
    else:
        print(f"Route: {smth.path}")


def get_app():
    registry = GlobalSub()
    docker = aiodocker.Docker()
    asyncio.create_task(listen(registry, docker))
    app = FastAPI()
    manager = AuthXSocket(app=app, mount_location="/")
    bind_sio(app, registry)
    print_routes(app)
    return app
