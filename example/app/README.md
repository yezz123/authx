# AuthX - Example

AuthX is a library for building authentication and authorization systems, using FastAPI & Starlette Dependency

In this example, we will use AuthX to build a simple authentication and authorization system, with multiple routes.

## Setup

- Setup the virtual environment

```bash
virtualenv venv && source venv/bin/activate
```

- Install requirements

```bash
pip install -r requirements.txt
```

- Configure your Environments variables

```bash
cp .env.sample .env
```

__Note__: If the pre-added configuration doesn't fit you, you could change it manually.

- Now you could run the Project locally

```bash
uvicorn main:app --reload
```

### Docker Usage

If you would like to not setup everything locally and run the project on Docker, you can use the following commands:

```shell
# Build the image
make build

# Run the server
make start
```
