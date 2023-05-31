import pytest

from authx import AuthX


@pytest.fixture(scope="function")
def authx():
    return AuthX()


def test_is_model_callback_set(authx: AuthX):
    def fake_model_handler(uid: str):
        return {"foo": "bar"}

    assert authx._check_model_callback_is_set(ignore_errors=True) is False
    with pytest.raises(AttributeError):
        authx._check_model_callback_is_set(ignore_errors=False)

    assert authx.is_model_callback_set is False
    authx.set_callback_get_model_instance(fake_model_handler)
    assert authx.is_model_callback_set is True
    assert authx._check_model_callback_is_set(ignore_errors=True) is True


def test_is_token_callback_set(authx: AuthX):
    def fake_token_handler(token: str):
        return True

    assert authx._check_token_callback_is_set(ignore_errors=True) is False
    with pytest.raises(AttributeError):
        authx._check_token_callback_is_set(ignore_errors=False)

    assert authx.is_token_callback_set is False
    authx.set_callback_token_blocklist(fake_token_handler)
    assert authx.is_token_callback_set is True
    assert authx._check_token_callback_is_set(ignore_errors=True) is True


def test_is_token_in_blocklist(authx: AuthX):
    @authx.set_callback_token_blocklist
    def fake_token_handler(token: str):
        return token.startswith("A")

    assert authx.is_token_callback_set is True

    assert authx.is_token_in_blocklist("Aloha") is True
    assert authx.is_token_in_blocklist("meh") is False


def test_get_current_subject(authx: AuthX):
    DB = {
        "a": {"username": "a"},
    }

    @authx.set_callback_get_model_instance
    def fake_model_handler(uid: str):
        return DB.get(uid)

    assert authx.is_model_callback_set is True

    assert authx._get_current_subject("a") == {"username": "a"}
    assert authx._get_current_subject("Meh") is None
