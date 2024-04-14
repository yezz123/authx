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
     Once you install the extra dependency you are aiming to use, ex:

     - for `cache` you will have Redis installed as a dependency.
     - for `profiler` you will have Pyinstruments Profiler installed as a dependency.
     - for `metrics` you will have Prometheus installed as a dependency.

### Development Dependencies

<div class="termy">

```console
$ git clone https://github.com/yezz123/authx.git

---> 100%

$ cd authx

$ bash scripts/install.sh
```

</div>
