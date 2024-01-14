# AuthenticationX 💫

<p align="center">
<a href="https://authx.yezz.me" target="_blank">
    <img src="https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png" alt="AuthX">
</a>
<p align="center">
    <em>Ready-to-use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>
<p align="center">
<a href="https://github.com/yezz123/authx/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/yezz123/authx/actions/workflows/ci.yml/badge.svg" alt="lint">
</a>
<a href="https://pypi.org/project/authx" target="_blank">
    <img src="https://img.shields.io/pypi/v/authx?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://codecov.io/gh/yezz123/authx">
    <img src="https://codecov.io/gh/yezz123/authx/branch/main/graph/badge.svg"/>
</a>
<a href="https://pepy.tech/project/authx" target="_blank">
    <img src="https://static.pepy.tech/badge/authx" alt="Test">
</a>
</p>
</p>

---

**Source Code**: <https://github.com/yezz123/authx>

**Documentation**: <https://authx.yezz.me/>

---

Add a Fully registration and authentication or authorization system to your
[FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be as
customizable and adaptable as possible.

> **Notes**:
>
> [Authx V0.9.x](https://authx-v0.yezz.me/) This branch relates to development of authx V1 which is not yet ready for production use.
>
>If you're a Authx user, you probably want either Authx V0.9 [Documentation](https://authx-v0.yezz.me/) or, [0.X.X-fix](https://github.com/yezz123/authx/tree/0.X.X-fix) git branch.

## Features 🔧

- [x] Support Python 3.8+.
- [x] Multiple customizable authentication backend:
  - [x] JWT authentication backend included
    - [x] JWT encoding/decoding for application authentication
    - [x] Automatic detection of JWTs in requests:
      - [x] JWTs in headers
      - [x] JWTs in cookies
      - [x] JWTs in query parameters
      - [x] JWTs in request bodies
  - [x] Cookie authentication backend included
- [x] middleware for authentication and authorization through JWT.
- [x] Extensible Error Handling System.

### Extra Features 🎁

AuthX is designed to be as customizable and adaptable as possible.

So you need to install [`authx-extra`](https://github.com/yezz123/authx-extra) to get extra features.

- [x] Using Redis as a session store & cache.
- [x] Support HTTPCache.
- [x] Support Sessions and Pre-built CRUD functions and Instance to launch Redis.
- [x] Support Middleware of [pyinstrument](https://pyinstrument.readthedocs.io/) to check your service performance.
- [x] Support Middleware for collecting and exposing [Prometheus](https://prometheus.io/) metrics.

**Note:** Check [Release Notes](https://authx.yezz.me/release/).

## Project using 🚀

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

## Contributors and sponsors 👏

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-11-orange.svg?style=flat-square)](#contributors-)

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
      <td align="center" valign="top" width="14.28%"><a href="https://talentuno.com/en/matchmakers"><img src="https://talentuno.com/assets/img/talentuno/mm/mm-letsdoit_num1.png?s=100" width="100px;" alt="talentuno LLC"/><br /><sub><b>talentuno LLC</b></sub></a><br /><a href="#financial-talentuno" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.stryker.com/us/en/index.html"><img src="https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_256,w_256,f_auto,q_auto:eco,dpr_1/v1492757324/sdovorqhcnnkgybhf05h.jpg?s=100" width="100px;" alt="Cactus LLC"/><br /><sub><b>Cactus LLC</b></sub></a><br /><a href="#financial-Cactus" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/MojixCoder"><img src="https://avatars.githubusercontent.com/u/76670309?v=4?s=100" width="100px;" alt="MojixCoder"/><br /><sub><b>MojixCoder</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=MojixCoder" title="Code">💻</a> <a href="https://github.com/yezz123/authx/issues?q=author%3AMojixCoder" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://sralab.com"><img src="https://avatars.githubusercontent.com/u/1815?v=4?s=100" width="100px;" alt="Stéphane Raimbault"/><br /><sub><b>Stéphane Raimbault</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=stephane" title="Code">💻</a> <a href="#plugin-stephane" title="Plugin/utility libraries">🔌</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/theoohoho"><img src="https://avatars.githubusercontent.com/u/31537466?v=4?s=100" width="100px;" alt="theoohoho"/><br /><sub><b>theoohoho</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=theoohoho" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://yogeshupadhyay.netlify.app/"><img src="https://avatars.githubusercontent.com/u/53992168?v=4?s=100" width="100px;" alt="Yogesh Upadhyay"/><br /><sub><b>Yogesh Upadhyay</b></sub></a><br /><a href="https://github.com/yezz123/authx/issues?q=author%3AYogeshUpdhyay" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/iftenet"><img src="https://avatars.githubusercontent.com/u/1397880?v=4?s=100" width="100px;" alt="Roman"/><br /><sub><b>Roman</b></sub></a><br /><a href="https://github.com/yezz123/authx/issues?q=author%3Aiftenet" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.linkedin.com/today/author/alobbs"><img src="https://avatars.githubusercontent.com/u/170559?v=4?s=100" width="100px;" alt="Alvaro Lopez Ortega"/><br /><sub><b>Alvaro Lopez Ortega</b></sub></a><br /><a href="https://github.com/yezz123/authx/commits?author=alobbs" title="Documentation">📖</a></td>
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

## Links 🔗

- [Homepage](https://authx.yezz.me/)
- [FAQ](https://authx.yezz.me/faq/)
- [Release - AuthX](https://authx.yezz.me/release/)
- [MIT License](https://authx.yezz.me/license/)
- [Code of Conduct](https://authx.yezz.me/code_of_conduct/)
- [Contributing](https://authx.yezz.me/contributing/)
- [Help - Sponsors](https://authx.yezz.me/help/)

## License 📄

This project is licensed under the terms of the MIT License.
