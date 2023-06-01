import pytest

from authx import AuthXConfig
from authx.exceptions import BadConfigurationError


@pytest.fixture(scope="function")
def config() -> AuthXConfig:
    config = AuthXConfig()
    config.JWT_ALGORITHM = "HS256"
    config.JWT_SECRET_KEY = "4321J4OP3JIB12BJ4NKJF2EBJE2"
    config.JWT_TOKEN_LOCATION = ["headers", "cookies", "json", "query"]
    config.JWT_CSRF_METHODS = ["POST", "DELETE", "PUT"]
    config.JWT_REFRESH_CSRF_HEADER_NAME = "X-REFRESH-CSRF-TOKEN"
    return config


def test_bad_algorithm_config_exception():
    config = AuthXConfig()
    config.JWT_ALGORITHM = "BLAH"
    config.JWT_SECRET_KEY = "4321J4OP3JIB12BJ4NKJF2EBJE2"

    with pytest.raises(BadConfigurationError):
        config.private_key


def test_none_secret_config_exception():
    config = AuthXConfig()
    config.JWT_ALGORITHM = "HS256"
    config.JWT_SECRET_KEY = None

    with pytest.raises(BadConfigurationError):
        config.private_key


def test_config_symmetric_key():
    config = AuthXConfig()
    config.JWT_ALGORITHM = "HS256"
    config.JWT_SECRET_KEY = "SYMMETRIC_KEY"
    config.JWT_PUBLIC_KEY = "ASYMMETRIC_PUBLIC_KEY"
    config.JWT_PRIVATE_KEY = "ASYMMETRIC_PRIVATE_KEY"

    assert config.private_key == config.JWT_SECRET_KEY
    assert config.public_key == config.JWT_SECRET_KEY


def test_config_asymmetric_key():
    config = AuthXConfig()
    config.JWT_ALGORITHM = "RS256"
    config.JWT_SECRET_KEY = "SYMMETRIC_KEY"
    config.JWT_PUBLIC_KEY = "ASYMMETRIC_PUBLIC_KEY"
    config.JWT_PRIVATE_KEY = "ASYMMETRIC_PRIVATE_KEY"

    assert config.private_key == config.JWT_PRIVATE_KEY
    assert config.public_key == config.JWT_PUBLIC_KEY


def test_config_has_location():
    config = AuthXConfig()

    assert config.has_location("headers")
    assert config.has_location("headers")
    assert config.has_location("cookies") is False


def test_config__get_key():
    config = AuthXConfig()
    config.JWT_SECRET_KEY = "SECRET"
    config.JWT_ALGORITHM = "RS256"

    assert config._get_key("TEST") == "TEST"

    config.JWT_ALGORITHM = "HS256"
    assert config._get_key("TEST") == "SECRET"
