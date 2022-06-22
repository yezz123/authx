import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from authx import ProfilerMiddleware

app = FastAPI(
    title="AuthX Profiler Middleware",
    description="AuthX Profiler Middleware",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_tags=["AuthX Profiler Middleware"],
)

app.add_middleware(ProfilerMiddleware)


@app.get("/test")
async def profiling():
    return JSONResponse({"Ping Pong": "Hello World!"})


if __name__ == "__main__":
    app_name = os.path.basename(__file__).replace(".py", "")
    uvicorn.run(app=f"{app_name}:app", host="0.0.0.0", port=8080, workers=1)
