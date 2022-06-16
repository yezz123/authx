# Socket

Socket.IO was created in 2010. It was developed to use open connections to facilitate realtime communication, still a relatively new phenomenon at the time.

Socket.IO allows bi-directional communication between client and server. Bi-directional communications are enabled when a client has Socket.IO in the browser, and a server has also integrated the Socket.IO package. While data can be sent in a number of forms, JSON is the simplest.

To establish the connection, and to exchange data between client and server, Socket.IO uses Engine.IO. This is a lower-level implementation used under the hood. Engine.IO is used for the server implementation and Engine.IO-client is used for the client.

![socket](https://images.ctfassets.net/ee3ypdtck0rk/1Lj7lbqX54WCiHI2uVVL3x/a7f857e10d3c1e93b4349639c04318bc/websocket.io-1b_2x.png?w=1841&h=690&q=50&fm=webp)

## Usage

To add SocketIO support to FastAPI all you need to do is import `AuthXSocket` and pass it `FastAPI` object.

```python
from fastapi import FastAPI
from authx import AuthXSocket

app = FastAPI()
socket = AuthXSocket(app=app)
```

you can import `AuthXSocket` object that exposes most of the SocketIO functionality.

```python
@AuthXSocket.on('leave')
async def handle_leave(sid, *args, **kwargs):
    await AuthXSocket.emit('lobby', 'User left')
```

## Working with distributed applications

When working with distributed applications, it is often necessary to access the functionality of the Socket.IO from multiple processes. As a solution to the above problems, the Socket.IO server can be configured to connect to a message queue such as `Redis` or `RabbitMQ`, to communicate with other related Socket.IO servers or auxiliary workers.

Refer this link for more details [using-a-message-queue](https://python-socketio.readthedocs.io/en/latest/server.html#using-a-message-queue)

```python

import socketio
from fastapi import FastAPI
from authx import AuthXSocket

app = FastAPI()

redis_manager = socketio.AsyncRedisManager('redis://')

socket_manager = AuthXSocket(app=app, client_manager=redis_manager)
```

### Emitting from external process

```python

import socketio

# connect to the redis queue as an external process
external_sio = socketio.RedisManager('redis://', write_only=True)

# emit an event
external_sio.emit('my event', data={'foo': 'bar'}, room='my room')
```
