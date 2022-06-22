# Overview

## Models

Pydantic models represent the data structure of a user. Base classes are provided with the required fields to make authentication work. You should sub-class each of them and add your own fields there.

➡️ [Models](models/index.md)

## Database

AuthX is compatible with MongoDB (other ORMs & providers coming soon). To build the interface between the database tool and the library, we provide a database adapter class that you need to instantiate and configure.

AuthX is compatible and extendible with the necessary tools to work with SQL databases thanks to the [Encode/Databases](https://www.encode.io/databases/) library.

➡️ [Database](database/index.md)

## Cache

AuthX provides Redis cache, a fast and reliable cache provider that can be used to cache the authentication results and store the user data. This one is based on `aioredis` a pure Python asynchronous Redis client.

➡️ [Cache](cache/index.md)

## Security

AuthX provides strong Utils to work with while developing your API. JWT is a simple and secure way to authenticate users, Now also we Have a supportable Sessions based on Redis; Captcha is a simple way to protect your API from bots;  `Hmac` and `Hashlib` to generate a strong password hash.

➡️ [Security](security/index.md)

## CRUD

Helping Developers to create, read, update and delete data is a common task. AuthX provides an Extensible CRUD API Helping you integrate it with your existing code.

➡️ [CRUD](crud/index.md)

## Services

Designing and configuring your API is a very important part of the development process. We provide a strong CRUD functional API to manage your API.

➡️ [Services](services/index.md)

## Routers

AuthX object is the main class from which you'll be able to generate routers for classic routes like registration, login or logout but also get the `current_user` dependency factory to inject the authenticated user in your own routes.

➡️ [Routers](routers/index.md)

## Middleware

Supporting OAuth2 is one of the most important feature of AuthX. We provide a middleware to handle the OAuth2 flow for both FastAPI app and Starlette app that could help you to integrate AuthX with your existing app.

Supporting Pyinstrument is also a helpful feature of AuthX. We provide a middleware to instrument your API, and check your service code performance.

➡️ [Middleware](middleware/index.md)

## SocketIO

AuthX provides a Socket.IO server that can be used to communicate with your API.

➡️ [SocketIO](socket/index.md)
