# Release Notes 🎞

## 0.9.1

### 🟥  LAST RELEASE FOR AUTHX - 0.x.x

As you may observe, my primary shift has been towards concentrating on the development of the new release, with a strong emphasis on incorporating features that users would appreciate to enhance authentication capabilities.

In doing so, I have intentionally omitted several functions. This is why I strongly believe that having two distinct versions is truly beneficial.

#### 0.x.x

The primary focus will be on addressing bug fixes and improving documentation in the previous version. It appears that the excessive use of dependencies may have been a factor that many people did not appreciate.

You can open a pull request in case you want to fix something related to it 🙌🏻

#### 1.x.x

You can read here what is new until now:

AuthX Revamp - V 1.0.0 will be our authentication system New design. This version comes with several new features and enhancements to improve security, usability, and performance.

##### Core Functionality

- JWT encoding/decoding for application authentication
- Automatic detection of JWTs in requests:
  - JWTs in headers
  - JWTs in cookies
  - JWTs in query strings
  - JWTs in JSON bodies
- Implicit/explicit token refresh mechanism
- Tracking the freshness state of tokens
- Route protection:
  - Protection based on token type (access/refresh)
  - Protection based on token freshness
  - Partial route protection
- Handling custom user logic for revoked token validation
- Handling custom logic for token recipient retrieval (ORM, pydantic serialization...)
- Providing FastAPI-compliant dependency injection API
- Automatic error handling

##### External Support

- Keeping profiler
- Keeping Redis
- Keeping Instrument
- Keeping Metrics
- Providing OAuth2 support

### Fixes 🐛

- ➖ Remove Documentation Workflow by @yezz123 in <https://github.com/yezz123/authx/pull/414>

### Dependencies 📦

- ⬆ Update sqlalchemy requirement from <2.0.4,>=1.4.37 to >=1.4.37,<2.0.5 by @dependabot in <https://github.com/yezz123/authx/pull/370>

- ⬆ Bump pre-commit from 3.0.4 to 3.1.0 by @dependabot in <https://github.com/yezz123/authx/pull/371>
- ⬆ Bump pre-commit from 3.1.0 to 3.1.1 by @dependabot in <https://github.com/yezz123/authx/pull/372>
- ⬆ Bump cryptography from 39.0.1 to 39.0.2 by @dependabot in <https://github.com/yezz123/authx/pull/373>
- ⬆ Update sqlalchemy requirement from <2.0.5,>=1.4.37 to >=1.4.37,<2.0.6 by @dependabot in <https://github.com/yezz123/authx/pull/374>
- ⬆ Bump pymdown-extensions from 9.9.2 to 9.10 by @dependabot in <https://github.com/yezz123/authx/pull/375>
- ⬆ Bump pytest from 7.2.1 to 7.2.2 by @dependabot in <https://github.com/yezz123/authx/pull/376>
- ⬆ Update fastapi requirement from <0.93.0,>=0.65.2 to >=0.65.2,<0.94.0 by @dependabot in <https://github.com/yezz123/authx/pull/380>
- ⬆ Bump pydantic from 1.10.5 to 1.10.6 by @dependabot in <https://github.com/yezz123/authx/pull/381>
- ⬆ Bump uvicorn from 0.20.0 to 0.21.0 by @dependabot in <https://github.com/yezz123/authx/pull/382>
- ⬆ Update starlette requirement from <0.25.1,>=0.14.02 to >=0.14.02,<0.26.1 by @dependabot in <https://github.com/yezz123/authx/pull/383>
- ⬆ Update fastapi requirement from <0.94.0,>=0.65.2 to >=0.65.2,<0.95.0 by @dependabot in <https://github.com/yezz123/authx/pull/385>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.6.4 to 1.7.1 by @dependabot in <https://github.com/yezz123/authx/pull/386>
- ⬆ Update sqlalchemy requirement from <2.0.6,>=1.4.37 to >=1.4.37,<2.0.7 by @dependabot in <https://github.com/yezz123/authx/pull/387>
- ⬆ Update starlette requirement from <0.26.1,>=0.14.02 to >=0.14.02,<0.26.2 by @dependabot in <https://github.com/yezz123/authx/pull/388>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.7.1 to 1.8.0 by @dependabot in <https://github.com/yezz123/authx/pull/389>
- ⬆ Bump uvicorn from 0.21.0 to 0.21.1 by @dependabot in <https://github.com/yezz123/authx/pull/390>
- ⬆ Update python-socketio requirement from <5.7.3,>=4.6.0 to >=4.6.0,<5.8.1 by @dependabot in <https://github.com/yezz123/authx/pull/391>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.8.0 to 1.8.1 by @dependabot in <https://github.com/yezz123/authx/pull/392>
- ⬆ Bump pre-commit from 3.1.1 to 3.2.0 by @dependabot in <https://github.com/yezz123/authx/pull/394>
- ⬆ Bump pytest-asyncio from 0.20.3 to 0.21.0 by @dependabot in <https://github.com/yezz123/authx/pull/395>
- ⬆ Update fastapi requirement from <0.95.0,>=0.65.2 to >=0.65.2,<0.96.0 by @dependabot in <https://github.com/yezz123/authx/pull/396>
- ⬆ Update sqlalchemy requirement from <2.0.7,>=1.4.37 to >=1.4.37,<2.0.8 by @dependabot in <https://github.com/yezz123/authx/pull/397>
- ⬆ Update redis requirement from <4.5.2,>=4.3.3 to >=4.3.3,<4.5.3 by @dependabot in <https://github.com/yezz123/authx/pull/398>
- ⬆ Bump pydantic from 1.10.6 to 1.10.7 by @dependabot in <https://github.com/yezz123/authx/pull/399>
- ⬆ Update redis requirement from <4.5.3,>=4.3.3 to >=4.3.3,<4.5.4 by @dependabot in <https://github.com/yezz123/authx/pull/400>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.8.1 to 1.8.3 by @dependabot in <https://github.com/yezz123/authx/pull/401>
- ⬆ Bump cryptography from 39.0.2 to 40.0.0 by @dependabot in <https://github.com/yezz123/authx/pull/402>
- ⬆ Bump cryptography from 40.0.0 to 40.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/404>
- ⬆ Bump pre-commit from 3.2.0 to 3.2.1 by @dependabot in <https://github.com/yezz123/authx/pull/405>
- ⬆ Bump pytz from 2022.7.1 to 2023.2 by @dependabot in <https://github.com/yezz123/authx/pull/403>
- ⬆ Bump pytz from 2023.2 to 2023.3 by @dependabot in <https://github.com/yezz123/authx/pull/406>
- ⬆ Update redis requirement from <4.5.4,>=4.3.3 to >=4.3.3,<4.5.5 by @dependabot in <https://github.com/yezz123/authx/pull/407>
- ⬆ Update sqlalchemy requirement from <2.0.8,>=1.4.37 to >=1.4.37,<2.0.9 by @dependabot in <https://github.com/yezz123/authx/pull/408>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.8.3 to 1.8.4 by @dependabot in <https://github.com/yezz123/authx/pull/410>
- ⬆ Bump websockets from 10.4 to 11.0 by @dependabot in <https://github.com/yezz123/authx/pull/409>
- ⬆ Bump pre-commit from 3.2.1 to 3.2.2 by @dependabot in <https://github.com/yezz123/authx/pull/411>
- ⬆ Bump motor from 3.1.1 to 3.1.2 by @dependabot in <https://github.com/yezz123/authx/pull/412>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.8.4 to 1.8.5 by @dependabot in <https://github.com/yezz123/authx/pull/413>
- ⬆ Update sqlalchemy requirement from <2.0.9,>=1.4.37 to >=1.4.37,<2.0.10 by @dependabot in <https://github.com/yezz123/authx/pull/415>
- ⬆ Bump websockets from 11.0 to 11.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/416>
- ⬆ Bump pytest from 7.2.2 to 7.3.0 by @dependabot in <https://github.com/yezz123/authx/pull/417>
- ⬆ Bump pymdown-extensions from 9.10 to 9.11 by @dependabot in <https://github.com/yezz123/authx/pull/418>
- ⬆ Bump httpx from 0.23.3 to 0.24.0 by @dependabot in <https://github.com/yezz123/authx/pull/419>
- ⬆ Update email-validator requirement from <1.3.2,>=1.1.0 to >=1.1.0,<2.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/420>
- ⬆ Bump pytest from 7.3.0 to 7.3.1 by @dependabot in <https://github.com/yezz123/authx/pull/421>
- ⬆ Bump websockets from 11.0.1 to 11.0.2 by @dependabot in <https://github.com/yezz123/authx/pull/424>
- ⬆ Bump cryptography from 40.0.1 to 40.0.2 by @dependabot in <https://github.com/yezz123/authx/pull/422>
- ⬆ Update sqlalchemy requirement from <2.0.10,>=1.4.37 to >=1.4.37,<2.0.11 by @dependabot in <https://github.com/yezz123/authx/pull/425>
- ⬆ Update sqlalchemy requirement from <2.0.11,>=1.4.37 to >=1.4.37,<2.0.12 by @dependabot in <https://github.com/yezz123/authx/pull/426>
- ⬆ Bump requests from 2.28.2 to 2.29.0 by @dependabot in <https://github.com/yezz123/authx/pull/427>
- ⬆ Bump uvicorn from 0.21.1 to 0.22.0 by @dependabot in <https://github.com/yezz123/authx/pull/428>
- ⬆ Update sqlalchemy requirement from <2.0.12,>=1.4.37 to >=1.4.37,<2.0.13 by @dependabot in <https://github.com/yezz123/authx/pull/429>
- ⬆ Bump pre-commit from 3.2.2 to 3.3.0 by @dependabot in <https://github.com/yezz123/authx/pull/430>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.8.5 to 1.8.6 by @dependabot in <https://github.com/yezz123/authx/pull/432>
- ⬆ Bump pre-commit from 3.3.0 to 3.3.1 by @dependabot in <https://github.com/yezz123/authx/pull/431>
- ⬆ Bump requests from 2.29.0 to 2.30.0 by @dependabot in <https://github.com/yezz123/authx/pull/433>
- ⬆ Update redis requirement from <4.5.5,>=4.3.3 to >=4.3.3,<4.5.6 by @dependabot in <https://github.com/yezz123/authx/pull/435>
- ⬆ Bump websockets from 11.0.2 to 11.0.3 by @dependabot in <https://github.com/yezz123/authx/pull/434>
- ⬆ Bump pyjwt from 2.6.0 to 2.7.0 by @dependabot in <https://github.com/yezz123/authx/pull/436>
- ⬆ Update sqlalchemy requirement from <2.0.13,>=1.4.37 to >=1.4.37,<2.0.14 by @dependabot in <https://github.com/yezz123/authx/pull/437>
- ⬆ Bump pymdown-extensions from 9.11 to 10.0 by @dependabot in <https://github.com/yezz123/authx/pull/438>
- ⬆️ Bump starlette from 0.25.0 to 0.27.0 in /tests/middleware/example by @dependabot in <https://github.com/yezz123/authx/pull/439>
- ⬆ Bump pymdown-extensions from 10.0 to 10.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/440>
- ⬆ Update starlette requirement from <0.26.2,>=0.14.02 to >=0.14.02,<0.27.1 by @dependabot in <https://github.com/yezz123/authx/pull/441>
- ⬆ Bump pre-commit from 3.3.1 to 3.3.2 by @dependabot in <https://github.com/yezz123/authx/pull/442>
- ⬆ Update sqlalchemy requirement from <2.0.14,>=1.4.37 to >=1.4.37,<2.0.15 by @dependabot in <https://github.com/yezz123/authx/pull/444>
- ⬆ Bump httpx from 0.24.0 to 0.24.1 by @dependabot in <https://github.com/yezz123/authx/pull/443>
- ⬆ Update sqlalchemy requirement from <2.0.15,>=1.4.37 to >=1.4.37,<2.0.16 by @dependabot in <https://github.com/yezz123/authx/pull/445>
- ⬆ Bump requests from 2.30.0 to 2.31.0 by @dependabot in <https://github.com/yezz123/authx/pull/450>
- ⬆ Bump pytest-cov from 4.0.0 to 4.1.0 by @dependabot in <https://github.com/yezz123/authx/pull/452>
- ⬆ Bump cryptography from 40.0.2 to 41.0.0 by @dependabot in <https://github.com/yezz123/authx/pull/453>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.9.0...0.9.1>

## 0.9.0

### Fixes 🐛

- ➕ Support Python 3.11 by @yezz123 in <https://github.com/yezz123/authx/pull/355>
- 🐛  Support `aioredis` from redis package by @yezz123 in <https://github.com/yezz123/authx/pull/369>

### Dependencies 🔨

- ⬆ Update email-validator requirement from <1.3.1,>=1.1.0 to >=1.1.0,<1.3.2 by @dependabot in <https://github.com/yezz123/authx/pull/347>
- ⬆ Bump pymdown-extensions from 9.9.1 to 9.9.2 by @dependabot in <https://github.com/yezz123/authx/pull/346>
- ⬆ Bump pre-commit from 2.21.0 to 3.0.0 by @dependabot in <https://github.com/yezz123/authx/pull/348>
- ⬆ Update sqlalchemy requirement from <1.4.47,>=1.4.37 to >=1.4.37,<2.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/350>
- ⬆ Bump pre-commit from 3.0.0 to 3.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/349>
- ⬆ Bump pre-commit from 3.0.1 to 3.0.4 by @dependabot in <https://github.com/yezz123/authx/pull/354>
- ⬆ Update sqlalchemy requirement from <2.0.1,>=1.4.37 to >=1.4.37,<2.0.2 by @dependabot in <https://github.com/yezz123/authx/pull/353>
- ⬆ Update starlette requirement from <0.23.2,>=0.14.02 to >=0.14.02,<0.24.1 by @dependabot in <https://github.com/yezz123/authx/pull/356>
- ⬆ Update sqlalchemy requirement from <2.0.2,>=1.4.37 to >=1.4.37,<2.0.3 by @dependabot in <https://github.com/yezz123/authx/pull/357>
- ⬆ Bump cryptography from 39.0.0 to 39.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/358>
- ⬆ Update redis requirement from <4.4.3,>=4.3.3 to >=4.3.3,<4.5.1 by @dependabot in <https://github.com/yezz123/authx/pull/359>
- ⬆ Bump markdown-include from 0.8.0 to 0.8.1 by @dependabot in <https://github.com/yezz123/authx/pull/360>
- ⬆ Update fastapi requirement from <0.90.0,>=0.65.2 to >=0.65.2,<0.91.0 by @dependabot in <https://github.com/yezz123/authx/pull/361>
- ⬆ Update redis requirement from <4.5.1,>=4.3.3 to >=4.3.3,<4.5.2 by @dependabot in <https://github.com/yezz123/authx/pull/362>
- ⬆ Update sqlalchemy requirement from <2.0.3,>=1.4.37 to >=1.4.37,<2.0.4 by @dependabot in <https://github.com/yezz123/authx/pull/363>
- ⬆ Update fastapi requirement from <0.91.0,>=0.65.2 to >=0.65.2,<0.92.0 by @dependabot in <https://github.com/yezz123/authx/pull/364>
- ⬆ Update starlette requirement from <0.24.1,>=0.14.02 to >=0.14.02,<0.25.1 by @dependabot in <https://github.com/yezz123/authx/pull/366>
- ⬆ Update fastapi requirement from <0.92.0,>=0.65.2 to >=0.65.2,<0.93.0 by @dependabot in <https://github.com/yezz123/authx/pull/367>
- ⬆ Bump pydantic from 1.10.4 to 1.10.5 by @dependabot in <https://github.com/yezz123/authx/pull/368>
- ⬆ Bump starlette from 0.17.1 to 0.25.0 in /tests/middleware/example by @dependabot in <https://github.com/yezz123/authx/pull/365>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.8.3...0.9.0>

## 0.8.3

### Fixes 🐛

- Fixes a few imports in the documentation by @alobbs in <https://github.com/yezz123/authx/pull/343>
- ✨ Use Ruff for linting by @yezz123 in <https://github.com/yezz123/authx/pull/344>

### Docs 📝

- docs: add @alobbs as a contributor for doc by @allcontributors in <https://github.com/yezz123/authx/pull/345>

### Dependencies 🔨

- ⬆ Bump pymdown-extensions from 9.9 to 9.9.1 by @dependabot in <https://github.com/yezz123/authx/pull/338>
- ⬆ Update redis requirement from <4.4.2,>=4.3.3 to >=4.3.3,<4.4.3 by @dependabot in <https://github.com/yezz123/authx/pull/337>
- ⬆ Bump requests from 2.28.1 to 2.28.2 by @dependabot in <https://github.com/yezz123/authx/pull/339>
- ⬆ Bump pytz from 2022.7 to 2022.7.1 by @dependabot in <https://github.com/yezz123/authx/pull/340>
- ⬆ Bump pytest from 7.2.0 to 7.2.1 by @dependabot in <https://github.com/yezz123/authx/pull/341>

### New Contributors

- @alobbs made their first contribution at <https://github.com/yezz123/authx/pull/343>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.8.2...0.8.3>

## 0.8.2

### What's Changed

- ⬆ Bump jinja2 from 3.0.3 to 3.1.2 by @dependabot in <https://github.com/yezz123/authx/pull/268>
- ⬆ Bump databases from 0.6.0 to 0.6.1 by @dependabot in <https://github.com/yezz123/authx/pull/270>
- ⬆ Update email-validator requirement from <1.2.1,>=1.1.0 to >=1.1.0,<1.3.1 by @dependabot in <https://github.com/yezz123/authx/pull/271>
- ⬆ Bump pytz from 2022.1 to 2022.6 by @dependabot in <https://github.com/yezz123/authx/pull/273>
- ⬆ Update pyinstrument requirement from <4.2.0,>=4.1.1 to >=4.1.1,<4.4.0 by @dependabot in <https://github.com/yezz123/authx/pull/274>
- ⬆ Bump pymdown-extensions from 9.5 to 9.7 by @dependabot in <https://github.com/yezz123/authx/pull/275>
- ⬆ Bump pytest-cov from 3.0.0 to 4.0.0 by @dependabot in <https://github.com/yezz123/authx/pull/276>
- ⬆ Update redis requirement from <4.3.4,>=4.3.3 to >=4.3.3,<4.3.5 by @dependabot in <https://github.com/yezz123/authx/pull/277>
- ⬆ Bump pytest from 7.1.3 to 7.2.0 by @dependabot in <https://github.com/yezz123/authx/pull/278>
- ⬆ Update fastapi requirement from <=0.81.0,>=0.65.2 to >=0.65.2,<0.87.0 by @dependabot in <https://github.com/yezz123/authx/pull/279>
- ⬆ Bump bcrypt from 3.2.2 to 4.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/281>
- ⬆ Bump pytest-asyncio from 0.19.0 to 0.20.1 by @dependabot in <https://github.com/yezz123/authx/pull/280>
- ⬆ Bump pydantic from 1.9.1 to 1.10.2 by @dependabot in <https://github.com/yezz123/authx/pull/282>
- ⬆ Update sqlalchemy requirement from <=1.4.40,>=1.4.37 to >=1.4.37,<1.4.43 by @dependabot in <https://github.com/yezz123/authx/pull/283>
- ⬆ Bump aiosmtplib from 1.1.6 to 2.0.0 by @dependabot in <https://github.com/yezz123/authx/pull/285>
- ⬆ Update pyinstrument requirement from <4.4.0,>=4.1.1 to >=4.1.1,<4.5.0 by @dependabot in <https://github.com/yezz123/authx/pull/286>
- ⬆ Bump pymdown-extensions from 9.7 to 9.8 by @dependabot in <https://github.com/yezz123/authx/pull/287>
- ⬆ Update python-socketio requirement from <5.7.1,>=4.6.0 to >=4.6.0,<5.7.3 by @dependabot in <https://github.com/yezz123/authx/pull/288>
- ⬆ Bump databases from 0.6.1 to 0.6.2 by @dependabot in <https://github.com/yezz123/authx/pull/289>
- ⬆ Update starlette requirement from <0.20.4,>=0.14.02 to >=0.14.02,<0.21.1 by @dependabot in <https://github.com/yezz123/authx/pull/290>
- ⬆ Update sqlalchemy requirement from <1.4.43,>=1.4.37 to >=1.4.37,<1.4.44 by @dependabot in <https://github.com/yezz123/authx/pull/291>
- ⬆ Bump cryptography from 37.0.4 to 38.0.3 by @dependabot in <https://github.com/yezz123/authx/pull/292>
- ⬆ Bump uvloop from 0.16.0 to 0.17.0 by @dependabot in <https://github.com/yezz123/authx/pull/293>
- ⬆ Bump websockets from 10.3 to 10.4 by @dependabot in <https://github.com/yezz123/authx/pull/294>
- ⬆ Bump pyjwt from 2.4.0 to 2.6.0 by @dependabot in <https://github.com/yezz123/authx/pull/296>
- ⬆ Bump motor from 3.0.0 to 3.1.1 by @dependabot in <https://github.com/yezz123/authx/pull/297>
- ⬆ Bump pytest-asyncio from 0.20.1 to 0.20.2 by @dependabot in <https://github.com/yezz123/authx/pull/300>
- ⬆ Update sqlalchemy requirement from <1.4.44,>=1.4.37 to >=1.4.37,<1.4.45 by @dependabot in <https://github.com/yezz123/authx/pull/298>
- ⬆ Update starlette requirement from <0.21.1,>=0.14.02 to >=0.14.02,<0.22.1 by @dependabot in <https://github.com/yezz123/authx/pull/301>
- ⬆ Bump httpx from 0.23.0 to 0.23.1 by @dependabot in <https://github.com/yezz123/authx/pull/303>
- ⬆ Bump uvicorn from 0.18.3 to 0.20.0 by @dependabot in <https://github.com/yezz123/authx/pull/302>
- ⬆ Update redis requirement from <4.3.5,>=4.3.3 to >=4.3.3,<4.3.6 by @dependabot in <https://github.com/yezz123/authx/pull/304>
- ⬆ Bump pymdown-extensions from 9.8 to 9.9 by @dependabot in <https://github.com/yezz123/authx/pull/305>
- ⬆ Bump markdown-include from 0.7.0 to 0.8.0 by @dependabot in <https://github.com/yezz123/authx/pull/306>
- ⬆ Bump cryptography from 38.0.3 to 38.0.4 by @dependabot in <https://github.com/yezz123/authx/pull/307>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.5.1 to 1.6.1 by @dependabot in <https://github.com/yezz123/authx/pull/312>
- ⬆ Bump jsmrcaga/action-netlify-deploy from 1.1.0 to 1.8.1 by @dependabot in <https://github.com/yezz123/authx/pull/309>
- Revert "⬆ Bump jsmrcaga/action-netlify-deploy from 1.1.0 to 1.8.1" by @yezz123 in <https://github.com/yezz123/authx/pull/314>
- ⬆ Update redis requirement from <4.3.6,>=4.3.3 to >=4.3.3,<4.4.1 by @dependabot in <https://github.com/yezz123/authx/pull/311>
- ⬆ Update starlette requirement from <0.22.1,>=0.14.02 to >=0.14.02,<0.23.1 by @dependabot in <https://github.com/yezz123/authx/pull/315>
- ⬆ Bump pypa/gh-action-pypi-publish from 1.6.1 to 1.6.4 by @dependabot in <https://github.com/yezz123/authx/pull/318>
- ⬆ Bump pytest-asyncio from 0.20.2 to 0.20.3 by @dependabot in <https://github.com/yezz123/authx/pull/319>
- ⬆ Update sqlalchemy requirement from <1.4.45,>=1.4.37 to >=1.4.37,<1.4.46 by @dependabot in <https://github.com/yezz123/authx/pull/320>
- ⬆ Update starlette requirement from <0.23.1,>=0.14.02 to >=0.14.02,<0.23.2 by @dependabot in <https://github.com/yezz123/authx/pull/321>
- ⬆ Bump databases from 0.6.2 to 0.7.0 by @dependabot in <https://github.com/yezz123/authx/pull/324>
- ⬆ Bump pytz from 2022.6 to 2022.7 by @dependabot in <https://github.com/yezz123/authx/pull/323>
- ⬆ Bump pre-commit from 2.20.0 to 2.21.0 by @dependabot in <https://github.com/yezz123/authx/pull/325>
- ⬆ Bump pydantic from 1.10.2 to 1.10.3 by @dependabot in <https://github.com/yezz123/authx/pull/326>
- ⬆ Bump cryptography from 38.0.4 to 39.0.0 by @dependabot in <https://github.com/yezz123/authx/pull/328>
- ⬆ Bump pydantic from 1.10.3 to 1.10.4 by @dependabot in <https://github.com/yezz123/authx/pull/327>
- ⬆ Update mkdocs-material requirement from <9.0.0,>=8.1.4 to >=8.1.4,<10.0.0 by @dependabot in <https://github.com/yezz123/authx/pull/330>
- ⬆ Bump httpx from 0.23.1 to 0.23.2 by @dependabot in <https://github.com/yezz123/authx/pull/329>
- ⬆ Update sqlalchemy requirement from <1.4.46,>=1.4.37 to >=1.4.37,<1.4.47 by @dependabot in <https://github.com/yezz123/authx/pull/331>
- ⬆ Update fastapi requirement from <0.87.0,>=0.65.2 to >=0.65.2,<0.89.0 by @dependabot in <https://github.com/yezz123/authx/pull/308>
- ⬆ Bump httpx from 0.23.2 to 0.23.3 by @dependabot in <https://github.com/yezz123/authx/pull/332>
- ⬆ Bump aiosmtplib from 2.0.0 to 2.0.1 by @dependabot in <https://github.com/yezz123/authx/pull/334>
- ⬆ Update redis requirement from <4.4.1,>=4.3.3 to >=4.3.3,<4.4.2 by @dependabot in <https://github.com/yezz123/authx/pull/335>
- ⬆ Update fastapi requirement from <0.87.0,>=0.65.2 to >=0.65.2,<0.90.0 by @dependabot in <https://github.com/yezz123/authx/pull/336>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.8.1...0.8.2>

## 0.8.1

### What's Changed

- increment postfix to find the possible username to use by @iftenet in <https://github.com/yezz123/authx/pull/266>
- docs: add @iftenet as a contributor for bug by @allcontributors in <https://github.com/yezz123/authx/pull/267>

### New Contributors

- @iftenet made their first contribution in <https://github.com/yezz123/authx/pull/266>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.8.0...0.8.1>

## 0.8.0

### Implementation in FastAPI applications

Thats Work by adding a Middleware to your FastAPI application, work on collecting prometheus metrics for each request, and then to handle that we need a function `get_metrics` work on handling exposing the prometheus metrics into `/metrics` endpoint.

```python
from fastapi import FastAPI
from authx.middleware import MetricsMiddleware, get_metrics

app = FastAPI()
app.add_middleware(MetricsMiddleware)
app.add_route("/metrics", get_metrics)
```

### What's Changed

- :construction_worker: chore(dev): Support middleware for Prometheus metrics by @yezz123 in <https://github.com/yezz123/authx/pull/262>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.7.0...0.8.0>

## 0.7.0

- 🔧 Update package metadata and move build internals from Flit to Hatch.

### What's Changed

- Migrate to Hatchling by @yezz123 in <https://github.com/yezz123/authx/pull/261>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.6.1...0.7.0>

## 0.6.1

Fix Client issue for launching both the client and database_name in `MongoDBBackend`.

```py
from authx import Authentication
from authx.database import MongoDBBackend
from motor.motor_asyncio import AsyncIOMotorClient


authx = Authentication(
     database_backend=MongoDBBackend(
          client=AsyncIOMotorClient("mongodb://localhost:27017"),
          database_name="test",
     )
)
```

### What's Changed

- 🛠 chore(refactor): Improve Errors  by @yezz123 in [#257](https://github.com/yezz123/authx/pull/257)
- 🔊 Update Dependencies by @yezz123 in [#259](https://github.com/yezz123/authx/pull/259)
- :bug: [WIP] fix client issue by @yezz123 in [#260](https://github.com/yezz123/authx/pull/260)

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.6.0...0.6.1>

## 0.6.0

### Idea

Profiling is a technique to figure out how time is spent in a program. With
these statistics, we can find the “hot spot” of a program and think about ways
of improvement. Sometimes, a hot spot in an unexpected location may also hint at
a bug in the program.

> Pyinstrument is a Python profiler. A profiler is a tool to help you optimize
> your code - make it faster.

### Profile a web request in FastAPI

To profile call stacks in FastAPI, you can write a middleware extension for
`pyinstrument`.

Create an async function and decorate it with `app.middleware('http')` where the
app is the name of your FastAPI application instance.

Make sure you configure a setting to only make this available when required.

```py
from pyinstrument import Profiler
PROFILING = True  # Set this from a settings model
if PROFILING:
    @app.middleware("http")
    async def profile_request(request: Request, call_next):
        profiling = request.query_params.get("profile", False)
        if profiling:
            profiler = Profiler(interval=settings.profiling_interval, async_mode="enabled")
            profiler.start()
            await call_next(request)
            profiler.stop()
            return HTMLResponse(profiler.output_html())
        else:
            return await call_next(request)
```

To invoke, make any request to your application with the GET parameter
`profile=1` and it will print the HTML result from `pyinstrument`.

### AuthX's Support

With AuthX the abstract of profiling is easy, it's just about calling the
`ProfilerMiddleware` 's class and calling it in
`add_middleware(ProfilerMiddleware)` func that FastAPI provides.

#### Example

```py
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from authx import ProfilerMiddleware
app = FastAPI()
app.add_middleware(ProfilerMiddleware)
@app.get("/test")
async def normal_request():
    return JSONResponse({"retMsg": "Hello World!"})
if __name__ == '__main__':
    app_name = os.path.basename(__file__).replace(".py", "")
    uvicorn.run(app=f"{app_name}:app", host="0.0.0.0", port=8080, workers=1)
```

### References

- [Profiling Python Code](https://machinelearningmastery.com/profiling-python-code/)
- [profile-a-web-request-in-fastapi](https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi)

### What's Changed

- 👷 Support Profiling for checking service performance by @yezz123 in
  <https://github.com/yezz123/authx/pull/240>
- 👷 chore(fix): Fix Failed tests for Oauth2 by @yezz123 in
  <https://github.com/yezz123/authx/pull/241>
- 🔖 Clean codebase from unread Docstrings by @yezz123 in
  <https://github.com/yezz123/authx/pull/242>
- 📝 Docs: Upgrade pre-commit and add new markdown's linter by @yezz123 in
  <https://github.com/yezz123/authx/pull/243>
- 🔧 Upgrade all Github Actions by @yezz123 in
  <https://github.com/yezz123/authx/pull/249>
- Chore(deps): Bump jsmrcaga/action-netlify-deploy from 1.1.0 to 1.8.0 by
  @dependabot in <https://github.com/yezz123/authx/pull/250>
- Add license scan report and status by @fossabot in
  <https://github.com/yezz123/authx/pull/253>
- 🔖 release 0.6.0 - Supporting Profiling by @yezz123 in
  <https://github.com/yezz123/authx/pull/255>

### New Contributors

- @fossabot made their first contribution in
  <https://github.com/yezz123/authx/pull/253>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.5.1...0.6.0>

## 0.5.1

Fix Wrong `username` validation `UserInRegister` model #237, Thanks to
[@YogeshUpdhyay](https://yogeshupadhyay.netlify.app/) 🙏🏻

### What's Changed

- Username Validation Fixed by
  [@YogeshUpdhyay](https://yogeshupadhyay.netlify.app/) in
  <https://github.com/yezz123/authx/pull/238>

### New Contributors

- [@YogeshUpdhyay](https://yogeshupadhyay.netlify.app/) made their first
  contribution in <https://github.com/yezz123/authx/pull/238>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.5.0...0.5.1>

## 0.5.0

Supporting SocketIO that's allows bi-directional communication between client
and server. Bi-directional communications are enabled when a client has
Socket.IO in the browser, and a server has also integrated the Socket.IO
package. While data can be sent in a number of forms, JSON is the simplest.

### Usage

To add SocketIO support to FastAPI all you need to do is import `AuthXSocket`
and pass it `FastAPI` object.

```python
from fastapi import FastAPI
from authx import AuthXSocket

app = FastAPI()
socket = AuthXSocket(app=app)
```

you can import `AuthXSocket` object that exposes most of the SocketIO
functionality.

```python
@AuthXSocket.on('leave')
async def handle_leave(sid, *args, **kwargs):
    await AuthXSocket.emit('lobby', 'User left')
```

### Working with distributed applications

When working with distributed applications, it is often necessary to access the
functionality of the Socket.IO from multiple processes. As a solution to the
above problems, the Socket.IO server can be configured to connect to a message
queue such as `Redis` or `RabbitMQ`, to communicate with other related Socket.IO
servers or auxiliary workers.

Refer this link for more details
[using-a-message-queue](https://python-socketio.readthedocs.io/en/latest/server.html#using-a-message-queue)

```python

import socketio
from fastapi import FastAPI
from authx import AuthXSocket

app = FastAPI()

redis_manager = socketio.AsyncRedisManager('redis://')

socket_manager = AuthXSocket(app=app, client_manager=redis_manager)
```

### What's Changed

- chore(ref): Improve API and refactor users management code by @yezz123 in
  <https://github.com/yezz123/authx/pull/222>
- chore: Fix Issue of Missing requirements by @yezz123 in
  <https://github.com/yezz123/authx/pull/225>
- chore(deps): update dependencies by @yezz123 in
  <https://github.com/yezz123/authx/pull/233>
- 🔧 change domain from `.codes` to `.me` by @yezz123 in
  <https://github.com/yezz123/authx/pull/235>
- chore(feat): support SocketIO in authx ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/234>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.4.0...0.5.0>

## 0.4.0

## HTTPCache

### Overview

HTTP caching occurs when the browser stores local copies of web resources for
faster retrieval the next time the resource is required. As your application
serves resources it can attach cache headers to the response specifying the
desired cache behavior.

![Overview](https://devcenter1.assets.heroku.com/article-images/782-imported-1443570279-782-imported-1443554749-55-original.jpg)

When an item is fully cached, the browser may choose to not contact the server
at all and simply use its cached copy:

![Overview](https://devcenter1.assets.heroku.com/article-images/782-imported-1443570282-782-imported-1443554751-54-original.jpg)

### HTTP cache headers

There are two primary cache headers, `Cache-Control` and `Expires`.

#### Cache-Control

The `Cache-Control` header is the most important header to set as it effectively
`switches on` caching in the browser. With this header in place, and set with a
value that enables caching, the browser will cache the file for as long as
specified. Without this header, the browser will re-request the file on each
subsequent request.

#### Expires

When accompanying the `Cache-Control` header, Expires simply sets a date from
which the cached resource should no longer be considered valid. From this date
forward the browser will request a fresh copy of the resource.

> This Introduction to HTTP Caching is based on the
> [HTTP Caching Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching).

AuthX provides a simple HTTP caching model designed to work with
[FastAPI](https://fastapi.tiangolo.com/),

### Initialize the cache

```python
from authx import HTTPCache
from pytz import timezone

africa_Casablanca = timezone('Africa/Casablanca')
HTTPCache.init(redis_url=REDIS_URL, namespace='test_namespace', tz=africa_Casablanca)
```

- Read More in the New Documentation:
  <https://authx.yezz.me/configuration/cache/httpcache/>

### What's Changed

- chore(docs): Improve Documentation by @yezz123 in
  <https://github.com/yezz123/authx/pull/209>
- chore(dev): refactor code & improve some exceptions ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/212>
- ref: Use the built-in function `next` instead of a for-loop. by @yezz123 in
  <https://github.com/yezz123/authx/pull/213>
- chore(docs): add New Sponsors ✨❤️ by @yezz123 in
  <https://github.com/yezz123/authx/pull/214>
- docs(mkdocs.yml): Change name from `middlewares` to `middleware` by @theoohoho
  in <https://github.com/yezz123/authx/pull/215>
- chore(f/l): Integrate `Pyupgrade` to AuthX Environment by @yezz123 in
  <https://github.com/yezz123/authx/pull/216>
- chore(feat): Integrate HTTP Caching Model for authx ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/217>
- docs: add theoohoho as a contributor for doc by @allcontributors in
  <https://github.com/yezz123/authx/pull/218>
- chore(Example): Provide New Cache Example✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/219>

### New Contributors

- @theoohoho made their first contribution in
  <https://github.com/yezz123/authx/pull/215>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.3.1...0.4.0>

## 0.3.1

### Session

This is a supported Redis Based Session Storage for your FastAPI Application,
you can use it with any Session Backend.

```sh
pip install authx[session]
```

**Note**: The requirements in `authx[redis]` are not the same used in Sessions
features.

#### Features

---

- [x] Dependency injection to protect routes
- [x] Compatible with FastAPI's auto-generated docs
- [x] Pydantic models for verifying session data
- [x] Abstract session backend so you can build one that fits your needs
- [x] Abstract frontends to choose how you extract the session ids (cookies,
      header, etc.)
- [x] Create verifiers based on the session data.
- [x] Compatible with any Redis Configuration.

##### Redis Configuration

Before setting up our Sessions Storage and our CRUD Backend, we need to
configure our Redis Instance.

`BasicConfig` is a function that helps us set up the Instance Information like
Redis Link Connection or ID Name or Expiration Time.

###### Default Config

- [x] url of Redis: `redis://localhost:6379/0`
- [x] name of sessionId: `ssid`
- [x] generator function of `sessionId`: `lambda :uuid.uuid4().hex`
- [x] expire time of session in redis: `6 hours`

```py
import random
from datetime import timedelta
from authx.cache import basicConfig

basicConfig(
    redisURL="redis://localhost:6379/1",
    sessionIdName="sessionId",
    sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
    expireTime=timedelta(days=1),
)
```

- Read the Changelog <https://authx.yezz.me/release/>

## What's Changed

- chore(dev): Add Sessions Requirements by @yezz123 in
  <https://github.com/yezz123/authx/pull/207>

- chore(docs): Documented the Functionality of Session Storing by @yezz123 in
  <https://github.com/yezz123/authx/pull/208>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.3.0...0.3.1>

## 0.3.0

## What's Changed

### Release Notes

Finally, we drop the full support from MongoDB Thanks to @stephane That's
implemented some functionality under the name of `BaseDBBackend` and Create some
Database Crud Functionality without a database.

- Database Plugins:

  - MongoDB: Using MongoDB as a Database Backend is now supported as a plugin
    based on `BaseDBBackend`.
  - EncodeDB: Databases give you simple asyncio support for a range of
    databases.

    It allows you to make queries using the powerful `SQLAlchemy Core`
    expression language and provides support for `PostgreSQL`, `MySQL`, and
    `SQLite`.

    We can now provide some SQL queries to the database on the top of
    `BaseDBBackend`.

### MongoDB

```python
from authx import MongoDBBackend
```

### EncodeDB

```python
from authx import EncodeDBBackend
```

**Note**: Don't forget to set up the database connection as a client that will
be functioned under pre-built Methods.

- Improve the package by Switching to `flit` to build the package.
  - Improve Workflow and integrate `codecov.yml`.
  - Use the issue of new Functionalities in Github.
  - Create New Directory called `scripts` to store the shell scripts to run
    tests or linting.
- Improve Importing the package
  <https://github.com/yezz123/authx/blob/main/authx/__init__.py>.
  - Calling the function or the class directly from the `__init__.py` file.
- Improve Documentation, and Describe different new Addons, that AuthX now
  provide such as new Database Backends or Plugins or the new middleware
  add-ons, Thanks to @AbderrahimSoubaiElidrissi
- Update and upgrade Dependencies.
- Inline and improve IDLE Support.

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.2.0...0.3.0>

## 0.2.0

## What's Changed

### Middleware - Oauth2

The OAuth 2.0 authorization framework is a protocol that allows a user to grant
a third-party website or application access to the user's protected resources,
without necessarily revealing their long-term credentials or even their
identity.

Starlette middleware for authentication through oauth2's via a secret key, which
is often used to add authentication and authorization to a web application that
interacts with an API on behalf of the user.

That's why AuthX provides a Configuration `MiddlewareOauth2` to configure the
OAuth2 middleware.

```py
from authx import MiddlewareOauth2

class AuthenticateMiddleware(MiddlewareOauth2):
    PUBLIC_PATHS = {"/public"}
```

### Code Enhancement

- Remove unnecessary calls to `enumerate` when the index variable is not used.
  by @yezz123 in <https://github.com/yezz123/authx/pull/179>
- chore: Create a Basic Example to serve the utility of AuthX by @yezz123 in
  <https://github.com/yezz123/authx/pull/178>
- Clean DocString & Define Functions by @yezz123 in
  <https://github.com/yezz123/authx/pull/189>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.4...0.2.0>

## 0.1.4

### What's Changed

- Chore(deps-dev): Bump pymdown-extensions from 9.0 to 9.1 by @dependabot in
  <https://github.com/yezz123/authx/pull/155>
- empty Scheduled daily dependency update on Monday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/156>
- empty Scheduled daily dependency update on Tuesday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/157>
- chore: add FastAPI to Classifiers by @yezz123 in
  <https://github.com/yezz123/authx/pull/163>
- Chore: Fix CI & Delete Docker Configuration ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/165>
- empty Scheduled daily dependency update on Monday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/166>
- empty Scheduled daily dependency update on Monday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/167>
- CI: Ignore some Directories 🪨 by @yezz123 in
  <https://github.com/yezz123/authx/pull/168>
- empty Scheduled daily dependency update on Wednesday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/169>
- empty Scheduled daily dependency update on Thursday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/170>
- empty Scheduled daily dependency update on Saturday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/171>
- empty Scheduled daily dependency update on Wednesday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/172>
- empty Scheduled daily dependency update on Friday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/173>
- empty Scheduled daily dependency update on Sunday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/174>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.3...0.1.4>

## 0.1.3

- Fix the issue relate to PyJWT (Bumping version #151 )
- Add `sameSite` to Cookies metadata ( #134)

### What's Changed

- chore: add sameSite attribute to the http only cookie by @smakosh in
  <https://github.com/yezz123/authx/pull/134>
- docs: add smakosh as a contributor for code, security by @allcontributors in
  <https://github.com/yezz123/authx/pull/138>
- chore: update Requirements ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/139>
- CI: Add Code Security Analyse ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/140>
- empty Scheduled daily dependency update on Tuesday by @pyup-bot in
  <https://github.com/yezz123/authx/pull/141>
- chore: Add JWT Algorithm Choices ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/143>
- Docs: Add financial Supporters ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/144>
- Bump PyJWT version from 1.7.1 to 2.3.0 by @MojixCoder in
  <https://github.com/yezz123/authx/pull/151>
- docs: add MojixCoder as a contributor for code, bug by @allcontributors in
  <https://github.com/yezz123/authx/pull/152>
- chore: Remove Todos assign 🖇 by @yezz123 in
  <https://github.com/yezz123/authx/pull/153>
- Upgrade `pre-commit` requirements ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/154>

## New Contributors

- @smakosh made their first contribution in
  <https://github.com/yezz123/authx/pull/134>
- @MojixCoder made their first contribution in
  <https://github.com/yezz123/authx/pull/151>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.2...0.1.3>

## 0.1.2

After this discussion #124 with [@stephane](https://github.com/stephane) we need
to change the package name that what pep's rules provide.

> Modules should have short, all-lowercase names. Underscores can be used in the
> module name if it improves readability. Python packages should also have
> short, all-lowercase names, although the use of underscores is discouraged.

![carbon](https://user-images.githubusercontent.com/52716203/140792904-39a9ddfa-c91b-4aa4-8069-955e38bf22a0.png)

## What's Changed

- Bump mkdocs-material from 7.2.6 to 7.3.5 by @dependabot in
  <https://github.com/yezz123/authx/pull/101>
- Docs: Prepare Project for Being Public ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/102>
- Bump mkdocs-material from 7.3.5 to 7.3.6 by @dependabot in
  <https://github.com/yezz123/authx/pull/103>
- Bump python from 3.9.2 to 3.10.0 by @dependabot in
  <https://github.com/yezz123/authx/pull/104>
- docs: add yezz123 as a contributor for code, doc, maintenance, infra by
  @allcontributors in <https://github.com/yezz123/authx/pull/105>
- docs: add AbderrahimSoubaiElidrissi as a contributor for review, doc by
  @allcontributors in <https://github.com/yezz123/authx/pull/106>
- CI: Delete Docs Build ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/108>
- Docs: Delete a part of FAQ ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/109>
- chore: Fix workflows ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/112>
- chore: Rename Website name & Fix Build Issue 🚀 by @yezz123 in
  <https://github.com/yezz123/authx/pull/113>
- Chore: Delete `aiohttp` by @yezz123 in
  <https://github.com/yezz123/authx/pull/114>
- WIP: Add Code owner 🖇 by @yezz123 in
  <https://github.com/yezz123/authx/pull/117>
- Chore: Fix Key Directory 🔑 by @yezz123 in
  <https://github.com/yezz123/authx/pull/115>
- Configure `.pyup` ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/120>
- pep-0008: Fix Package and Module Names✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/126>
- chore: Change project Name by @yezz123 in
  <https://github.com/yezz123/authx/pull/128>
- chore: fix dockerfile commands by @yezz123 in
  <https://github.com/yezz123/authx/pull/130>
- Chore: change Name from `AuthX` to `authx` ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/131>
- Bump version from 0.1.1 to 0.1.2 ✨ by @yezz123 in
  <https://github.com/yezz123/authx/pull/132>

## New Contributors

- @allcontributors made their first contribution in
  <https://github.com/yezz123/authx/pull/105>

**Full Changelog**: <https://github.com/yezz123/authx/compare/0.1.1...0.1.2>

## 0.1.1

- Kuddos to
  [@AbderrahimSoubaiElidrissi](https://github.com/AbderrahimSoubaiElidrissi) for
  fixing multiple issues in docs ✨
- Fix Database partial router.
- Now we can call the `cache` or `mongo` only from a partial router.

### Example

<img width="654" alt="main py" src="https://user-images.githubusercontent.com/52716203/138797035-549804e4-0609-46aa-ba2f-e1b1f8757f59.png">

## What's Changed

- Add a partial router to Database ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/97>
- Docs: Update documentation by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/98>
- Bump from 0.1.0 to 0.1.1 ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/99>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.1.0...0.1.1>

## 0.1.0

- Provide a full support for python 3.10 after adding a testcase (workflow), and
  fix the version of pytest.
- Provide a full requirements for `Setup.py` with all the dependencies and
  classifiers.

## What's Changed

- docs: Add All Contributor by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/89>
- 📃 Docs: Add Codacy Review ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/90>
- CI: Fix Workflows ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/92>
- chore: Provide all requirements relate to `Setup.py` ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/93>
- ⬆️ Bump from 0.0.9 to 0.1.0 by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/94>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.9...0.1.0>

## 0.0.9

- Add Code coverage and local testing for AuthenticationX.
- Add DocString to Some Functions relate to `Services`.
- Bump multiple packages to last release.

### What's Changed

- Bump mkdocs from 1.2.2 to 1.2.3 by @dependabot in
  <https://github.com/yezz123/AuthX/pull/78>
- Bump pytest-asyncio from 0.14.0 to 0.16.0 by @dependabot in
  <https://github.com/yezz123/AuthX/pull/77>
- 🐳 DockerFile Checker ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/80>
- chore: Provide DocString for Functions ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/84>
- Docs: Create a Release Notes ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/85>
- Chore: Add Local Testing & Code Coverage ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/86>
- Docs: Add Coverage Badge ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/87>
- ⬆️ Bump Version from 0.0.8 to 0.0.9 by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/88>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.8...0.0.9>

## 0.0.8

### What's Changed

- Fix Highlighting Issue ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/69>
- Docs: Add some Typo ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/70>
- Add Code of Conducts & License ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/71>
- Switch to MIT License ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/73>
- Test Documentation Build ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/74>
- ⬆️ Bump from 0.0.7 to 0.0.8 ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/75>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.7...0.0.8>

## 0.0.7

### What's Changed

- Implement DocStrings ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/60>
- Create a Global Documentation using Mkdocs by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/63>
- Fix Requirements by @yezz123 in <https://github.com/yezz123/AuthX/pull/66>
- Fix Documentation by @yezz123 in <https://github.com/yezz123/AuthX/pull/67>
- Version 0.0.7 ✨ by @yezz123 in <https://github.com/yezz123/AuthX/pull/68>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.6...0.0.7>

## 0.0.6

### What's Changed

- Fix Environment Files by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/54>
- Provide More Classifiers ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/57>
- Setup Tests DocStrings ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/58>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.5...0.0.6>

## 0.0.5

All this is based on This PR #45 :

- here I fix issues related to documentation.
- Generate a docstring for the main file.

### What's Changed

- ✨: Fix Documentation issue by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/45>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.4...0.0.5>

## 0.0.4

During the work on this PR #44 :

- I generate a docstring to improve the project & clear some parts of the code.
- Add an Issue Template (Pre-public).
- Create a simple Readme For the whole users.
- Adding New Commands relate to the bumpversion package in the Makefile.

### What's Changed

- Setup docstring & Create Documentation by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/44>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.3...0.0.4>

## 0.0.3

- Create a simple Readme.
- Create a Build to release the package.
- Fix Test Issues

### What's Changed

- Test : All functions in the Services and Fix some issues related to Raise() by
  @yezz123 in <https://github.com/yezz123/AuthX/pull/23>
- Release the first Version of AuthX ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/28>
- Create a Simple Readme by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/42>
- Create 0.0.3 version by @yezz123 in <https://github.com/yezz123/AuthX/pull/43>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.2...0.0.3>

## 0.0.2

Create a Testable Core for Email and work on Users and JWT. work on a PR to test
the Services and Provide more Routers tests

### What's Changed

- Create a test for Email ✨ by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/25>

**Full Changelog**: <https://github.com/yezz123/AuthX/compare/0.0.1...0.0.2>

## 0.0.1

- Create Authentication Routes ex. Register, login, logout, and Reset.
- Add The Social Authentication Routes, Connecting using Google and Facebook.
- Give the Admin the Permission of Adding a User to the Blacklist or Ban a User
  from The API.
- Done with Setup of Multiple Routes and Fix The Crud Issues.
- Use the JWT package For Creating tokens and checking, also the Email Provider
  works with booths aiosmtplib and email-validator.
- Provide the Common Models ex. Users Models and Social Models.
- Create a Multiple Errors Support for Route and Models Validation or also if
  the Social Authentication CallBack got Errors.
- Add A Recaptcha Bypass using Httpx Library and Create A String and Signature
  Generator using Passlib.
- Using passlib to Verify the Password and Hash it under sha256.
- Set up a workflow to Test The Project in a Docker environment.

### What's Changed

- chore : Create Package Core by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/1>
- chore: Provide The Full Functionality of Routers and Services by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/2>
- chore: Create the Package Main file by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/3>
- chore: Add Testing and Building Configuration by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/5>
- chore: Add Last Build Addons to Test Branch by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/8>
- chore: Create Dev work for testing the Package by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/4>
- chore: Fix Build Files by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/10>
- Isort AuthX path and Fix Missing packages for test by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/18>
- adding test case to workflow by @yezz123 in
  <https://github.com/yezz123/AuthX/pull/19>

**Full Changelog**: <https://github.com/yezz123/AuthX/commits/0.0.1>
