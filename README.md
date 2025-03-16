# Authx

<p align="center">
<a href="https://authx.yezz.me" target="_blank">
    <img src="https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png" alt="AuthX">
</a>
<p align="center">
    <em>Ready-to-use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>
</p>

---

| Project | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI      | [ ![ CI ]( https://github.com/yezz123/authx/actions/workflows/ci.yml/badge.svg ) ]( https://github.com/yezz123/authx/actions/workflows/ci.yml )  [ ![ pre-commit.ci status ]( https://results.pre-commit.ci/badge/github/yezz123/authx/main.svg )   ]( https://results.pre-commit.ci/latest/github/yezz123/authx/main )  [ ![ Codecov ]( https://codecov.io/gh/yezz123/authx/branch/main/graph/badge.svg )   ]( https://codecov.io/gh/yezz123/authx ) |
| Meta    | [ ![ Package version ]( https://img.shields.io/pypi/v/authx?color=%2334D058&label=pypi%20package )   ]( https://pypi.org/project/authx )  [ ![ Downloads ]( https://static.pepy.tech/badge/authx )   ]( https://pepy.tech/project/authx )  [ ![ Pydantic Version 2 ]( https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json )   ]( https://pydantic.dev )  [ ![ Ruff ]( https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json ) ]( https://github.com/astral-sh/ruff ) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=yezz123_authx&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=yezz123_authx)                                                                                                                                                 |

---

**Source Code**: <https://github.com/yezz123/authx>

**Documentation**: <https://authx.yezz.me/>

---

Add a Fully registration and authentication or authorization system to your
[FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be as
customizable and adaptable as possible.

## Features

- [x] Support Python 3.8+ & Pydantic 1.7+.
- [x] Multiple customizable authentication backend:
  - [x] JWT authentication backend included
    - [x] JWT encoding/decoding for application authentication
    - [x] Automatic detection of JWTs in requests:
      - [x] JWTs in headers
      - [x] JWTs in cookies
      - [x] JWTs in query parameters
      - [x] JWTs in request bodies
  - [x] Cookie authentication backend included
- [x] Middleware for authentication and authorization through JWT.
- [x] Extensible Error Handling System.

### Extra Features

AuthX is designed to be as customizable and adaptable as possible.

So you need to install [`authx-extra`](https://github.com/yezz123/authx-extra) to get extra features.

- [x] Using Redis as a session store & cache.
- [x] Support HTTPCache.
- [x] Support Sessions and Pre-built CRUD functions and Instance to launch Redis.
- [x] Support Middleware of [pyinstrument](https://pyinstrument.readthedocs.io/) to check your service performance.
- [x] Support Middleware for collecting and exposing [Prometheus](https://prometheus.io/) metrics.

**Note:** Check [Release Notes](https://authx.yezz.me/release/).

## Project using

Here is a simple way to kickstart your project with AuthX:

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig, RequestToken

app = FastAPI()

config = AuthXConfig(
     JWT_ALGORITHM = "HS256",
     JWT_SECRET_KEY = "SECRET_KEY",
     JWT_TOKEN_LOCATION = ["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)

@app.get('/login')
def login(username: str, password: str):
     if username == "xyz" and password == "xyz":
          token = auth.create_access_token(uid=username)
          return {"access_token": token}
     raise HTTPException(401, detail={"message": "Invalid credentials"})

@app.get("/protected", dependencies=[Depends(auth.get_token_from_request)])
def get_protected(token: RequestToken = Depends()):
     try:
          auth.verify_token(token=token)
          return {"message": "Hello world !"}
     except Exception as e:
          raise HTTPException(401, detail={"message": str(e)}) from e
```

## Contributors and sponsors

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-14-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thanks goes to these wonderful people
([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://yezz.me"><img src="https://avatars.githubusercontent.com/u/52716203?v=4?s=100" width="100px;" alt="Yasser Tahiri"/><br /><sub><b>Yasser Tahiri</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=yezz123" title="Code">💻</a> <a href="https://github.com/yezz123/authx/commits?author=yezz123" title="Documentation">📖</a> <a href="#maintenance-yezz123" title="Maintenance">🚧</a> <a href="#infra-yezz123" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://soubai.me"><img src="https://avatars.githubusercontent.com/u/11523791?v=4?s=100" width="100px;" alt="Abderrahim SOUBAI-ELIDRISI"/><br /><sub><b>Abderrahim SOUBAI-ELIDRISI</b></sub></a><br /><a href="https://github.com/yezz123/authx/pulls?q=is%3Apr+reviewed-by%3AAbderrahimSoubaiElidrissi" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/yezz123/authx/commits?author=AbderrahimSoubaiElidrissi" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://smakosh.com"><img src="https://avatars.githubusercontent.com/u/20082141?v=4?s=100" width="100px;" alt="Ismail Ghallou "/><br /><sub><b>Ismail Ghallou </b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=smakosh" title="Code">💻</a> <a href="#security-smakosh" title="Security">🛡️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/MojixCoder"><img src="https://avatars.githubusercontent.com/u/76670309?v=4?s=100" width="100px;" alt="MojixCoder"/><br /><sub><b>MojixCoder</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=MojixCoder" title="Code">💻</a> <a href="https://github.com/yezz123/authx/issues?q=author%3AMojixCoder" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://sralab.com"><img src="https://avatars.githubusercontent.com/u/1815?v=4?s=100" width="100px;" alt="Stéphane Raimbault"/><br /><sub><b>Stéphane Raimbault</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=stephane" title="Code">💻</a> <a href="#plugin-stephane" title="Plugin/utility libraries">🔌</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/theoohoho"><img src="https://avatars.githubusercontent.com/u/31537466?v=4?s=100" width="100px;" alt="theoohoho"/><br /><sub><b>theoohoho</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=theoohoho" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://yogeshupadhyay.netlify.app/"><img src="https://avatars.githubusercontent.com/u/53992168?v=4?s=100" width="100px;" alt="Yogesh Upadhyay"/><br /><sub><b>Yogesh Upadhyay</b></sub></a><br /><a href="https://github.com/yezz123/authx/issues?q=author%3AYogeshUpdhyay" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/iftenet"><img src="https://avatars.githubusercontent.com/u/1397880?v=4?s=100" width="100px;" alt="Roman"/><br /><sub><b>Roman</b></sub></a><br /><a href="https://github.com/yezz123/authx/issues?q=author%3Aiftenet" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.linkedin.com/today/author/alobbs"><img src="https://avatars.githubusercontent.com/u/170559?v=4?s=100" width="100px;" alt="Alvaro Lopez Ortega"/><br /><sub><b>Alvaro Lopez Ortega</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=alobbs" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/pinchXOXO"><img src="https://avatars.githubusercontent.com/u/68501799?v=4?s=100" width="100px;" alt="Devy Santo"/><br /><sub><b>Devy Santo</b></sub></a><br /><a href="#infra-pinchXOXO" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/pg365"><img src="https://avatars.githubusercontent.com/u/173273017?v=4?s=100" width="100px;" alt="pg365"/><br /><sub><b>pg365</b></sub></a><br /><a href="#infra-pg365" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jor-rit"><img src="https://avatars.githubusercontent.com/u/16398756?v=4?s=100" width="100px;" alt="Jorrit"/><br /><sub><b>Jorrit</b></sub></a><br /><a href="#platform-jor-rit" title="Packaging/porting to new platform">📦</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/callamd"><img src="https://avatars.githubusercontent.com/u/1664656?v=4?s=100" width="100px;" alt="Callam"/><br /><sub><b>Callam</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=callamd" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/lmasikl"><img src="https://avatars.githubusercontent.com/u/1556136?v=4?s=100" width="100px;" alt="Maxim"/><br /><sub><b>Maxim</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=lmasikl" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the
[all-contributors](https://github.com/all-contributors/all-contributors)
specification. Contributions of any kind welcome!

## License

This project is licensed under the terms of the MIT License.
