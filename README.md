# AuthX

<p align="center">
<a href="https://authx.yezz.me" target="_blank">
    <img src="https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png" alt="AuthX">
</a>
<p align="center">
    <em>Ready-to-use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>
</p>

---

| Project | Status |
|---------|--------|
| CI      | [![CI](https://github.com/yezz123/authx/actions/workflows/ci.yml/badge.svg)](https://github.com/yezz123/authx/actions/workflows/ci.yml) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/yezz123/authx/main.svg)](https://results.pre-commit.ci/latest/github/yezz123/authx/main) [![Codecov](https://codecov.io/gh/yezz123/authx/branch/main/graph/badge.svg)](https://codecov.io/gh/yezz123/authx) |
| Meta    | [![Package version](https://img.shields.io/pypi/v/authx?color=%2334D058&label=pypi%20package)](https://pypi.org/project/authx) [![Downloads](https://static.pepy.tech/badge/authx)](https://pepy.tech/project/authx) [![Pydantic Version 2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=yezz123_authx&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=yezz123_authx) |

---

**Source Code**: <https://github.com/yezz123/authx>

**Documentation**: <https://authx.yezz.me/>

---

Add a fully featured authentication and authorization system to your [FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be simple, customizable, and secure.

## Installation

```bash
pip install authx
```

## Quick Start

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",  # Change this!
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)

@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        token = auth.create_access_token(uid=username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")

@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Hello World"}
```

**Test it:**

```bash
# Get a token
curl -X POST "http://localhost:8000/login?username=test&password=test"

# Access protected route
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/protected
```

## Features

- Support for Python 3.9+ and Pydantic 2
- JWT authentication with multiple token locations:
  - Headers (Bearer token)
  - Cookies (with CSRF protection)
  - Query parameters
  - JSON body
- Access and refresh token support
- Token freshness for sensitive operations
- Token blocklist/revocation
- Extensible error handling

### Extra Features

Install [`authx-extra`](https://github.com/yezz123/authx-extra) for additional features:

```bash
pip install authx-extra
```

- Redis session store and cache
- HTTP caching
- Performance profiling with pyinstrument
- Prometheus metrics

**Note:** Check [Release Notes](https://authx.yezz.me/release/).

## Contributors and Sponsors

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-17-orange.svg?style=flat-square)](#contributors-)
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
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://evergreenies.github.io"><img src="https://avatars.githubusercontent.com/u/33820365?v=4?s=100" width="100px;" alt="Suyog Shimpi"/><br /><sub><b>Suyog Shimpi</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=Evergreenies" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/NeViNez"><img src="https://avatars.githubusercontent.com/u/91369880?v=4?s=100" width="100px;" alt="NeViNez"/><br /><sub><b>NeViNez</b></sub></a><br /><a href="https://github.com/yezz123/authx/issues?q=author%3ANeViNez" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Antareske"><img src="https://avatars.githubusercontent.com/u/171327898?v=4?s=100" width="100px;" alt="Antareske"/><br /><sub><b>Antareske</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=Antareske" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the
[all-contributors](https://github.com/all-contributors/all-contributors)
specification. Contributions of any kind welcome!

## License

This project is licensed under the terms of the MIT License.
