import asyncio
from typing import Optional
from unittest.mock import Mock, patch

import pytest

from authx._internal import _CallbackHandler


class DummyModel:
    def __init__(self, id: str):
        self.id = id


def test_callback_handler_initialization():
    handler = _CallbackHandler()
    assert handler._model is None
    assert handler.callback_get_model_instance is None
    assert handler.callback_is_token_in_blocklist is None


def test_set_and_check_callbacks():
    handler = _CallbackHandler()

    def model_callback(uid: str, **kwargs) -> Optional[DummyModel]:
        return DummyModel(uid) if uid else None

    def token_callback(token: str, **kwargs) -> bool:
        return token == "blocked"

    handler.set_callback_get_model_instance(model_callback)
    handler.set_callback_token_blocklist(token_callback)

    assert handler.is_model_callback_set
    assert handler.is_token_callback_set


@pytest.mark.asyncio
async def test_get_current_subject():
    handler = _CallbackHandler()

    def model_callback(uid: str, **kwargs) -> Optional[DummyModel]:
        return DummyModel(uid) if uid else None

    handler.set_callback_get_model_instance(model_callback)

    subject = await handler._get_current_subject("123")
    assert isinstance(subject, DummyModel)
    assert subject.id == "123"

    subject = await handler._get_current_subject("")
    assert subject is None


@pytest.mark.asyncio
async def test_is_token_in_blocklist():
    handler = _CallbackHandler()

    def token_callback(token: str, **kwargs) -> bool:
        return token == "blocked"

    handler.set_callback_token_blocklist(token_callback)

    assert await handler.is_token_in_blocklist("blocked")
    assert not await handler.is_token_in_blocklist("valid")
    assert not await handler.is_token_in_blocklist(None)


@pytest.mark.asyncio
async def test_callback_not_set_exceptions():
    handler = _CallbackHandler()

    with pytest.raises(AttributeError):
        await handler._get_current_subject("123")

    # Token blocklist check should not raise an exception when not set
    assert not await handler.is_token_in_blocklist("any_token")


def test_set_subject_getter_alias():
    handler = _CallbackHandler()

    def model_callback(uid: str, **kwargs) -> Optional[DummyModel]:
        return DummyModel(uid) if uid else None

    handler.set_subject_getter(model_callback)
    assert handler.callback_get_model_instance == model_callback


def test_set_token_blocklist_alias():
    handler = _CallbackHandler()

    def token_callback(token: str, **kwargs) -> bool:
        return token == "blocked"

    handler.set_token_blocklist(token_callback)
    assert handler.callback_is_token_in_blocklist == token_callback


@pytest.mark.asyncio
async def test_edge_case_empty_string_inputs():
    handler = _CallbackHandler()

    def model_callback(uid: str, **kwargs) -> Optional[DummyModel]:
        return DummyModel(uid) if uid else None

    def token_callback(token: str, **kwargs) -> bool:
        return bool(token and token.strip())

    handler.set_callback_get_model_instance(model_callback)
    handler.set_callback_token_blocklist(token_callback)

    assert await handler._get_current_subject("") is None
    assert not await handler.is_token_in_blocklist("")
    assert not await handler.is_token_in_blocklist("   ")


@pytest.mark.asyncio
async def test_edge_case_none_inputs():
    handler = _CallbackHandler()

    def model_callback(uid: str, **kwargs) -> Optional[DummyModel]:
        return DummyModel(uid) if uid else None

    def token_callback(token: str, **kwargs) -> bool:
        return bool(token)

    handler.set_callback_get_model_instance(model_callback)
    handler.set_callback_token_blocklist(token_callback)

    assert await handler._get_current_subject(None) is None
    assert not await handler.is_token_in_blocklist(None)


def model_callback(uid: str, **kwargs) -> Optional[DummyModel]:
    if "extra" in kwargs and kwargs["extra"] == "special":
        return DummyModel(f"special_{uid}")
    return DummyModel(uid)


def token_callback(token: str, **kwargs) -> bool:
    return "block_all" in kwargs and kwargs["block_all"]


@pytest.fixture
def handler():
    handler = _CallbackHandler()
    handler.set_callback_get_model_instance(model_callback)
    handler.set_callback_token_blocklist(token_callback)
    return handler


@pytest.mark.asyncio
async def test_edge_case_kwargs_passing_special(handler):
    assert (await handler._get_current_subject("123", extra="special")).id == "special_123"


@pytest.mark.asyncio
async def test_edge_case_kwargs_passing_normal(handler):
    assert (await handler._get_current_subject("123")).id == "123"


@pytest.mark.asyncio
async def test_token_in_blocklist(handler):
    assert await handler.is_token_in_blocklist("any_token", block_all=True)


@pytest.mark.asyncio
async def test_token_not_in_blocklist(handler):
    assert not await handler.is_token_in_blocklist("any_token", block_all=False)


def test_edge_case_model_with_handler():
    class ModelWithHandler:
        def __init__(self):
            self.handler = _CallbackHandler(self)

    model = ModelWithHandler()
    assert model.handler._model == model


def test_check_model_callback_is_set():
    handler = _CallbackHandler()

    # Test when callback is not set
    with pytest.raises(AttributeError):
        handler._check_model_callback_is_set()

    assert handler._check_model_callback_is_set(ignore_errors=True) == False

    # Set the callback
    handler.set_callback_get_model_instance(lambda uid, **kwargs: None)

    # Test when callback is set
    assert handler._check_model_callback_is_set() == True
    assert handler._check_model_callback_is_set(ignore_errors=True) == True


def test_check_token_callback_is_set():
    handler = _CallbackHandler()

    # Test when callback is not set
    with pytest.raises(AttributeError):
        handler._check_token_callback_is_set()

    assert handler._check_token_callback_is_set(ignore_errors=True) == False

    # Set the callback
    handler.set_callback_token_blocklist(lambda token, **kwargs: False)

    # Test when callback is set
    assert handler._check_token_callback_is_set() == True
    assert handler._check_token_callback_is_set(ignore_errors=True) == True


def complex_callback(token, **kwargs):
    if token == "blocked":
        return True
    elif token == "none":
        return None
    else:
        return False


@pytest.mark.asyncio
async def test_is_token_in_blocklist_detailed():
    handler = _CallbackHandler()

    # Test when callback is not set
    assert not await handler.is_token_in_blocklist("token")

    # Set a callback that always returns True
    handler.set_callback_token_blocklist(lambda token, **kwargs: True)
    assert await handler.is_token_in_blocklist("token")

    # Set a callback that always returns False
    handler.set_callback_token_blocklist(lambda token, **kwargs: False)
    assert not await handler.is_token_in_blocklist("token")

    # Set a callback that returns None
    handler.set_callback_token_blocklist(lambda token, **kwargs: None)
    assert not await handler.is_token_in_blocklist("token")

    handler.set_callback_token_blocklist(complex_callback)
    assert await handler.is_token_in_blocklist("blocked")
    assert not await handler.is_token_in_blocklist("none")
    assert not await handler.is_token_in_blocklist("allowed")


@pytest.mark.asyncio
async def test_is_token_in_blocklist_none_callback():
    handler = _CallbackHandler()

    # Set the callback to None explicitly
    handler.callback_is_token_in_blocklist = None

    # The method should return False when the callback is None
    assert not await handler.is_token_in_blocklist("any_token")

    mock_callback = Mock(return_value=True)
    handler.callback_is_token_in_blocklist = mock_callback

    # The method should return True and the mock should be called
    assert await handler.is_token_in_blocklist("any_token")
    mock_callback.assert_called_once_with("any_token")

    # Reset the mock and set the callback to None again
    mock_callback.reset_mock()
    handler.callback_is_token_in_blocklist = None

    # The method should return False and the mock should not be called
    assert not await handler.is_token_in_blocklist("any_token")
    mock_callback.assert_not_called()


@pytest.mark.asyncio
async def test_is_token_in_blocklist_callback_execution():
    handler = _CallbackHandler()

    with patch.object(handler, "_check_token_callback_is_set", return_value=True):
        # Test when callback is None
        handler.callback_is_token_in_blocklist = None
        assert not await handler.is_token_in_blocklist("test_token")

        # Test when callback returns True
        mock_callback = Mock(return_value=True)
        handler.callback_is_token_in_blocklist = mock_callback
        assert await handler.is_token_in_blocklist("test_token")
        mock_callback.assert_called_once_with("test_token")

        # Test when callback returns False
        mock_callback = Mock(return_value=False)
        handler.callback_is_token_in_blocklist = mock_callback
        assert not await handler.is_token_in_blocklist("test_token")
        mock_callback.assert_called_once_with("test_token")

        # Test with kwargs
        mock_callback = Mock(return_value=True)
        handler.callback_is_token_in_blocklist = mock_callback
        assert await handler.is_token_in_blocklist("test_token", extra="param")
        mock_callback.assert_called_once_with("test_token", extra="param")


@pytest.mark.asyncio
async def test_async_model_callback():
    handler = _CallbackHandler()

    async def async_get_model(uid: str, **kwargs) -> Optional[DummyModel]:
        if not uid:
            return None
        await asyncio.sleep(0.001)
        if "prefix" in kwargs:
            return DummyModel(f"{kwargs['prefix']}_{uid}")
        return DummyModel(uid)

    handler.set_callback_get_model_instance(async_get_model)

    subject = await handler._get_current_subject("u001")
    assert isinstance(subject, DummyModel)
    assert subject.id == "u001"

    subject = await handler._get_current_subject("u002", prefix="admin")
    assert subject.id == "admin_u002"

    assert await handler._get_current_subject("") is None
    assert await handler._get_current_subject(None) is None


@pytest.mark.asyncio
async def test_async_token_blocklist_callback():
    handler = _CallbackHandler()

    async def async_is_blocked(token: str, **kwargs) -> bool:
        await asyncio.sleep(0.001)

        if token in ("black1", "black2"):
            return True

        if "force_block" in kwargs and kwargs["force_block"]:
            return True

        return False

    handler.set_callback_token_blocklist(async_is_blocked)

    assert await handler.is_token_in_blocklist("black1") is True
    assert await handler.is_token_in_blocklist("normal") is False
    assert await handler.is_token_in_blocklist("xyz", force_block=True) is True
    assert await handler.is_token_in_blocklist(None) is False
    assert await handler.is_token_in_blocklist("") is False


@pytest.mark.asyncio
async def test_mixed_sync_and_async_callbacks():
    handler = _CallbackHandler()

    def sync_get_model(uid: str, **_) -> Optional[DummyModel]:
        return DummyModel(f"sync_{uid}") if uid else None

    async def async_check_token(token: str, **_) -> bool:
        await asyncio.sleep(0.0001)
        return token.startswith("bad_")

    handler.set_callback_get_model_instance(sync_get_model)
    handler.set_callback_token_blocklist(async_check_token)

    subject = await handler._get_current_subject("alice")
    assert subject.id == "sync_alice"

    assert await handler.is_token_in_blocklist("bad_123") is True
    assert await handler.is_token_in_blocklist("good_token") is False


@pytest.mark.asyncio
async def test_async_callback_raises_exception():
    handler = _CallbackHandler()

    async def bad_model_callback(uid: str, **_):
        if uid == "error":
            raise ValueError("Database connection failed")
        return DummyModel(uid)

    handler.set_callback_get_model_instance(bad_model_callback)

    subject = await handler._get_current_subject("ok")
    assert subject.id == "ok"

    with pytest.raises(ValueError, match="Database connection failed"):
        await handler._get_current_subject("error")
