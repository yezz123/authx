import asyncio

import socketio

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print("connected to server")


@sio.event
async def disconnect():
    print("disconnected from server")


@sio.event
def docker_event(event):
    print(f"Got docker_event: {event}")


async def start_server():
    await sio.connect("http://localhost:8009/")
    await sio.wait()


if __name__ == "__main__":
    asyncio.run(start_server())
