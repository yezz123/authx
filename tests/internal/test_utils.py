import datetime

from authx._internal import get_now, get_now_ts, get_uuid


def test_util_get_now():
    assert isinstance(get_now(), datetime.datetime)
    assert get_now().tzinfo == datetime.timezone.utc


def test_util_get_now_ts():
    assert isinstance(get_now_ts(), float)


def test_util_get_uuid():
    assert isinstance(get_uuid(), str)
    assert len(get_uuid()) >= 1
