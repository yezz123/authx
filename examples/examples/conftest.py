# This file ensures pytest loads and configures itself before any test imports

# This conftest.py file exists to help pytest properly set up assertion rewriting
# before test modules import modules that need to be rewritten (like anyio).


def pytest_configure(config):
    """Configure pytest."""
    # This hook is called after the config object has been created but before
    # pytest imports any test modules. It's a good place to add additional
    # configuration if needed.
    pass
