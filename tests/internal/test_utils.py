import datetime as date
from datetime import datetime
from datetime import timezone as datetimezone

import pytest
import pytz
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from pytz import timezone

from authx._internal._utils import (
    IST_time,
    beginning_of_day,
    days_after,
    days_ago,
    end_of_day,
    end_of_last_week,
    end_of_week,
    get_now,
    get_now_ts,
    get_uuid,
    hours_ago,
    is_today,
    is_tomorrow,
    is_yesterday,
    minutes_after,
    minutes_ago,
    months_after,
    months_ago,
    start_of_week,
    time_diff,
    to_UTC,
    to_UTC_without_tz,
    tz_from_iso,
    tz_now,
    years_ago,
)

utc = timezone("UTC")


@pytest.fixture
def sample_datetime():
    return datetime(2023, 5, 20, 12, 0, 0)


@pytest.fixture
def sample_datetime_with_tz():
    tz = pytz.timezone("America/New_York")
    return tz.localize(datetime(2023, 5, 20, 12, 0, 0))


@freeze_time("2023-07-01 12:00:00")
def test_util_get_now():
    assert isinstance(get_now(), date.datetime)
    assert get_now().tzinfo == date.timezone.utc
    assert get_now() == datetime(2023, 7, 1, 12, 0, 0, tzinfo=datetimezone.utc)


@freeze_time("2023-07-01 12:00:00")
def test_util_get_now_ts():
    assert isinstance(get_now_ts(), float)
    assert get_now_ts() == datetime(2023, 7, 1, 12, 0, 0, tzinfo=datetimezone.utc).timestamp()


def test_util_get_uuid():
    assert isinstance(get_uuid(), str)
    assert len(get_uuid()) == 36  # UUID4 is always 36 characters long


@freeze_time("2023-07-01 12:00:00")
def test_time_diff():
    dt1 = datetime(2023, 5, 20, 12, 0, 0)
    dt2 = datetime(2023, 5, 19, 12, 0, 0)
    assert time_diff(dt1, dt2) == relativedelta(days=1)


@freeze_time("2023-07-01 12:00:00")
def test_to_UTC(sample_datetime_with_tz):
    expected_result = datetime(2023, 5, 20, 16, 0, 0, tzinfo=utc)
    assert to_UTC(sample_datetime_with_tz) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_to_UTC_without_tz():
    event_timestamp = "2023-05-20 12:00:00.000"
    expected_result = "2023-05-20 12:00:00.000000"
    assert to_UTC_without_tz(event_timestamp) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_beginning_of_day(sample_datetime):
    expected_result = datetime(2023, 5, 20, 0, 0, 0)
    assert beginning_of_day(sample_datetime) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_end_of_day(sample_datetime):
    expected_result = datetime(2023, 5, 20, 23, 59, 59, 999999)
    assert end_of_day(sample_datetime) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_minutes_ago(sample_datetime):
    expected_result = datetime(2023, 5, 20, 11, 59, 0)
    assert minutes_ago(sample_datetime, minutes=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_minutes_after(sample_datetime):
    expected_result = datetime(2023, 5, 20, 12, 1, 0)
    assert minutes_after(sample_datetime, minutes=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_hours_ago(sample_datetime):
    expected_result = datetime(2023, 5, 20, 11, 0, 0)
    assert hours_ago(sample_datetime, hours=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_days_ago(sample_datetime):
    expected_result = datetime(2023, 5, 19, 12, 0, 0)
    assert days_ago(sample_datetime, days=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_months_ago(sample_datetime):
    expected_result = datetime(2023, 4, 20, 12, 0, 0)
    assert months_ago(sample_datetime, months=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_months_after(sample_datetime):
    expected_result = datetime(2023, 6, 20, 12, 0, 0)
    assert months_after(sample_datetime, months=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_years_ago(sample_datetime):
    expected_result = datetime(2022, 5, 20, 12, 0, 0)
    assert years_ago(sample_datetime, years=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_days_after(sample_datetime):
    expected_result = datetime(2023, 5, 21, 12, 0, 0)
    assert days_after(sample_datetime, days=1) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_is_today():
    assert is_today(datetime(2023, 7, 1, 12, 0, 0, tzinfo=datetimezone.utc)) is True
    assert is_today(datetime(2023, 7, 2, 12, 0, 0, tzinfo=datetimezone.utc)) is False


@freeze_time("2023-07-01 12:00:00")
def test_is_yesterday():
    assert is_yesterday(datetime(2023, 6, 30, 12, 0, 0, tzinfo=datetimezone.utc)) is True
    assert is_yesterday(datetime(2023, 7, 1, 12, 0, 0, tzinfo=datetimezone.utc)) is False


@freeze_time("2023-07-01 12:00:00")
def test_is_tomorrow():
    assert is_tomorrow(datetime(2023, 7, 2, 12, 0, 0, tzinfo=datetimezone.utc)) is True
    assert is_tomorrow(datetime(2023, 7, 1, 12, 0, 0, tzinfo=datetimezone.utc)) is False


@freeze_time("2023-07-01 12:00:00")
def test_IST_time():
    assert isinstance(IST_time(), datetime)


@freeze_time("2023-07-01 12:00:00")
def test_tz_now():
    assert isinstance(tz_now(), datetime)
    assert tz_now() == datetime(2023, 7, 1, 12, 0, 0, tzinfo=datetimezone.utc)


@freeze_time("2023-07-01 12:00:00")
def test_tz_from_iso():
    dt = "2023-05-20T12:00:00.000+0000"
    expected_result = datetime(2023, 5, 20, 12, 0, 0, tzinfo=utc)
    assert tz_from_iso(dt) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_start_of_week():
    dt = datetime(2023, 5, 20, 12, 0, 0)
    expected_result = datetime(2023, 5, 15, 12, 0, 0)
    assert start_of_week(dt) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_end_of_week():
    dt = datetime(2023, 5, 20, 12, 0, 0)
    expected_result = datetime(2023, 5, 21, 12, 0, 0)
    assert end_of_week(dt) == expected_result


@freeze_time("2023-07-01 12:00:00")
def test_end_of_last_week():
    dt = datetime(2023, 5, 20, 12, 0, 0)
    expected_result = datetime(2023, 5, 14, 12, 0, 0)
    assert end_of_last_week(dt) == expected_result
