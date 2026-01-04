# Installation

## Install AuthX

=== "pip"
    ```bash
    pip install authx
    ```

=== "uv"
    ```bash
    uv add authx
    ```

=== "poetry"
    ```bash
    poetry add authx
    ```

## Verify Installation

```python
import authx
print(authx.__version__)
```

## Quick Start

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        return {"access_token": auth.create_access_token(uid=username)}
    raise HTTPException(401, detail="Invalid credentials")


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Hello World"}
```

Run it:

```bash
uvicorn main:app --reload
```

## Extra Features

Install [`authx-extra`](https://github.com/yezz123/authx-extra) for additional features:

```bash
pip install authx-extra
```

This adds:

- **Redis cache** - Session storage and caching
- **Profiler** - Performance monitoring with pyinstrument
- **Metrics** - Prometheus metrics collection

## Requirements

- Python 3.9+
- FastAPI
- Pydantic 2.0+
