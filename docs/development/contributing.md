---
hide:
  - navigation
---

First, you might want to see the basic ways to
[help AuthX and get help](../faq/help.md)

## Developing

If you already cloned the repository and you know that you need to deep dive
into the code, here is a guideline to set up your environment:

### Virtual environment with `uv`

You can create a virtual environment in a directory using Python's [`uv`](https://github.com/astral-sh/uv)
module:

<div class="termy">

```console
pip install uv

uv venv
```

</div>

That will create a directory `.venv` with the python binaries and then you will
be able to install packages for that isolated environment.

### Activate the environment

Activate the new environment with:

=== "Linux, macOS"

    <div class="termy">

    ```console
    $ source ./.venv/bin/activate
    ```

    </div>

=== "Windows PowerShell"

    <div class="termy">

    ```console
    $ .\.venv\Scripts\Activate.ps1
    ```

    </div>

=== "Windows Bash"

    Or if you use Bash for Windows (e.g. <a href="https://gitforwindows.org/" class="external-link" target="_blank">Git Bash</a>):

    <div class="termy">

    ```console
    $ source ./.venv/Scripts/activate
    ```

    </div>

To check it worked, use:

=== "Linux, macOS, Windows Bash"

    <div class="termy">

    ```console
    $ which pip
    ```

    </div>

=== "Windows PowerShell"

    <div class="termy">

    ```console
    $ Get-Command pip
    ```

    </div>

If it shows the `pip` binary at `venv/bin/pip` then it worked. 🎉

!!! tip

    Every time you install a new package with `pip` under that environment,
    activate the environment again.

    This makes sure that if you use a terminal program installed by that package (like `pre-commit`), you use the one from your local environment and not any other that could be installed globally.

### pip

After activating the environment as described above, Now lets install all the package that you need to develop authx:

<div class="termy">

```console
$ uv pip install -r requirements/all.txt

---> 100%
```

</div>

It will install all the dependencies in your local environment.

#### Including

The Dependencies file contains all the dependencies that you need to develop
AuthX, which are:

- The Base Dependencies - the ones that are needed to run AuthX.
  [See Installation](../get-started/installation.md).

### Format

For Providing a good and consistent experience, we recommend using
[pre-commit](https://pre-commit.com/) - a tool that runs a set of checks before
you commit your code.

#### Git Hooks

First you need to install the [pre-commit](https://pre-commit.com/) tool, which
is installed before with the Dev Dependencies.

Now, install the pre-commit hooks in your `.git/hooks/` directory:

<div class="termy">

```console
$ pre-commit install
```

</div>

This one will provide a linting check before you commit your code.

#### Including

The `.pre-commit-config.yaml` contains the following configuration with the
linting packages.

- `pre-commit-hooks` - Some out-of-the-box hooks for pre-commit.
- `ruff-pre-commit` - A tool to check Python code for errors.
- `black` - A tool to format Python code.
- `pyupgrade` - A tool to upgrade Python syntax.

## Documentation

First, make sure you set up your environment as described above, that will
install all the requirements.

The documentation uses
<a href="https://www.mkdocs.org/" class="external-link" target="_blank">MkDocs</a>.

All the documentation is in Markdown format in the directory `./docs`.

### Including

To Build AuthX Documentation we need the following packages, which are:

- `mkdocs` - The tool that builds the documentation.
- `mkdocs-material` - The theme that AuthX uses.
- `mkdocs-markdownextradata-plugin` - The plugin that allows to add extra data
  to the documentation.

### Translations

Help with translations is VERY MUCH appreciated! And it can't be done without
the help from the community. 🌎 🚀

Here are the steps to help with translations.

#### Tips and guideline

- Check the currently
  <a href="https://github.com/yezz123/AuthX/pulls" class="external-link" target="_blank">existing
  pull requests</a> for your language and add reviews requesting changes or
  approving them.

!!! tip You can

      <a href="https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/commenting-on-a-pull-request" class="external-link" target="_blank">add
      comments with change suggestions</a> to existing pull requests.

      Check the docs about <a href="https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-request-reviews" class="external-link" target="_blank">adding a pull request review</a> to approve it or request changes.

- Check in the
  <a href="https://github.com/yezz123/AuthX/issues" class="external-link" target="_blank">issues</a>
  to see if there's one coordinating translations for your language.

- Add a single pull request per page translated. That will make it much easier
  for others to review it.

For the languages I don't speak, I'll wait for several others to review the
translation before merging.

- You can also check if there are translations for your language and add a
  review to them, that will help me know that the translation is correct and I
  can merge it.

- Use the same Python examples and only translate the text in the docs. You
  don't have to change anything for this to work.

- Use the same images, file names, and links. You don't have to change anything
  for it to work.

- To check the 2-letter code for the language you want to translate you can use
  the table
  <a href="https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes" class="external-link" target="_blank">List
  of ISO 639-1 codes</a>.

## Testing

all the dependencies that you need to test AuthX, which are:

### Including

- `pytest` - The tool that runs the tests.
- `pytest-asyncio` - The plugin that runs the tests in the background.
- `requests` - The library that makes the requests to the AuthX API.
- `HTTPX` - A fully featured HTTP client for Python 3

and other dependencies that are needed to run the tests.

### Generate a Test Report

As we know, the tests are very important to make sure that AuthX works as
expected, that why i provide a multi test for and functions to provide a good
test.

If you want to generate the test report:

<div class="termy">

```console
$ bash scripts/test.sh
```

</div>
