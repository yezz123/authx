# Overview

## Models

Pydantic models representing the data structure of a user. Base classes are provided with the required fields to make authentication work. You should sub-class each of them and add your own fields there.

➡️ [Configure the Models](models/index.md)

## Database Provider

AuthX is compatible with MongoDB (other ORM & provider Soon...). To build the interface between the database tool and the library, we provide database adapter class that you need to instantiate and configure.

➡️ [Configure the Database](database/index.md)

## Cache Provider

AuthX provide Redis cache, is a fast and reliable cache provider that can be used to cache the authentication results, and to store the user data. This one is based on `aioredis` a pure Python asynchronous Redis client.

➡️ [Configure the Cache](cache/index.md)

## Authentication Provider

Authentication backends define the way users sessions are managed in your app, like access tokens or cookies, and Admin Manager.

➡️ [Configure the Authentication](auth/index.md)

## Social Authentication Provider

Social authentication backends define the way users are authenticated with social networks like Google, Facebook, etc.

➡️ [Configure the Social Authentication](social/index.md)

## UserManager Provider

The UserManager object bears most of the logic of AuthX: registration, verification, password reset, Captcha... We provide a `BaseUserManager` with this common logic; which you should overload to define how to validate passwords or handle events.

This `UserManager` object should be provided through a `FastAPI` dependency.

➡️ [Configure the UserManager](core/index.md)

## AuthX & Routers

Finally, AuthX object is the main class from which you'll be able to generate routers for classic routes like registration, login or logout but also get the `current_user` dependency factory to inject the authenticated user in your own routes.

➡️ [Configure the Routers](routers/index.md)
