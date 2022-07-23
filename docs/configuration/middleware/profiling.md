## Idea

Profiling is a technique to figure out how time is spent in a program. With
these statistics, we can find the “hot spot” of a program and think about ways
of improvement. Sometimes, a hot spot in an unexpected location may also hint at
a bug in the program.

> Pyinstrument is a Python profiler. A profiler is a tool to help you optimize
> your code - make it faster.

## Profile a web request in FastAPI

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

## AuthX's Support

With AuthX the abstract of profiling is easy, it's just about calling the
`ProfilerMiddleware` 's class and calling it in
`add_middleware(ProfilerMiddleware)` func that FastAPI provides.

### Example

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

## References

- [Profiling Python Code](https://machinelearningmastery.com/profiling-python-code/)
- [profile-a-web-request-in-fastapi](https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi)
