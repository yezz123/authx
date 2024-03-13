# Installation

## Getting Started

You can add AuthX to your FastAPI project in a few easy steps. First of all,
install the dependency:

### Default Dependency

<div class="termy">

```console
$ pip install authx

---> 100%
```

</div>

### Extra Dependencies

After installing the dependency, you can install the extra dependencies, which we have in the [`authx-extra`](https://github.com/yezz123/authx-extra) repository.

<div class="termy">

```console
$ pip install authx_extra

---> 100%
```

</div>

!!! warning
     You should install the extra dependency you are aiming to use, ex:

     - `authx_extra[cache]` for Redis support
     - `authx_extra[profiler]` for Pyinstruments Profiler support
     - `authx_extra[metrics]` for prometheus metrics support

### Development Dependencies

<div class="termy">

```console
$ git clone https://github.com/yezz123/authx.git

---> 100%

$ cd authx

$ bash scripts/install.sh
```

</div>
