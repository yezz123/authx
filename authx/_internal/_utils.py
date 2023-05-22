import datetime as date
import uuid
from datetime import datetime, timedelta
from datetime import timezone as tz

import pytz
from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta
from pytz import timezone

from authx.types import Numeric

RESERVED_CLAIMS = {
    "fresh",
    "csrf",
    "iat",
    "exp",
    "iss",
    "aud",
    "type",
    "jti",
    "nbf",
    "sub",
}

utc = timezone("UTC")


def get_now() -> date.datetime:
    """Returns the current UTC datetime

    Returns:
        datetime.datetime: Current datetime (UTC)
    """
    return date.datetime.now(tz=date.timezone.utc)


def get_now_ts() -> Numeric:
    """Returns the current UTC datetime as timestamp (float)

    Returns:
        Numeric: Current datetime (UTC)
    """
    return get_now().timestamp()


def get_uuid() -> str:
    """Generates a Universe Unique Identifier v4 (UUIDv4)

    Returns:
        str: unique identifier
    """
    return str(uuid.uuid4())


def time_diff(dt1: datetime, dt2: datetime) -> relativedelta:
    return relativedelta(dt1, dt2)


def to_UTC(event_timestamp: datetime, tz: pytz.timezone = utc):
    if isinstance(event_timestamp, datetime):
        dt = event_timestamp
    else:
        dt = dateutil_parser.parse(event_timestamp)

    return dt.astimezone(tz)


def to_UTC_without_tz(event_timestamp: str, format: str = "%Y-%m-%d %H:%M:%S.%f"):
    dt = datetime.strptime(event_timestamp, format)
    return dt.astimezone(tz.utc).strftime(format)


def beginning_of_day(dt: datetime):
    dt = dt.replace(minute=0, hour=0, second=0, microsecond=0)
    return dt


def end_of_day(dt: datetime):
    dt = dt.replace(minute=59, hour=23, second=59, microsecond=999999)
    return dt


def minutes_ago(dt: datetime, days: int = 0, hours: int = 0, minutes: int = 1, seconds: int = 0):
    return dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def minutes_after(dt: datetime, days: int = 0, hours: int = 0, minutes: int = 1, seconds: int = 0):
    return dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def hours_ago(dt: datetime, days: int = 0, hours: int = 1, minutes: int = 0, seconds: int = 0):
    return dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def days_ago(dt: datetime, days: int = 1, hours: int = 0, minutes: int = 0, seconds: int = 0):
    past = dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if dt.tzinfo:
        past = past.replace(tzinfo=dt.tzinfo)
    return past


def months_ago(dt: datetime, months: int = 1):
    return dt - relativedelta(months=months)


def months_after(dt: datetime, months: int = 1):
    return dt + relativedelta(months=months)


def years_ago(dt: datetime, years: int = 1):
    past = dt - relativedelta(years=years)
    if dt.tzinfo:
        past = past.replace(tzinfo=past.tzinfo)
    return past


def days_after(dt: datetime, days: int = 1, hours: int = 0, minutes: int = 0, seconds: int = 0):
    future = dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if dt.tzinfo:
        future = future.replace(tzinfo=dt.tzinfo)
    return future


def is_today(dt: datetime):
    return dt.astimezone(utc).day == datetime.now().astimezone(utc).day


def is_yesterday(dt: datetime):
    return dt.astimezone(utc).day == days_ago(datetime.now().astimezone(utc)).day


def is_tomorrow(dt: datetime):
    return dt.astimezone(utc).day == days_after(datetime.now().astimezone(utc)).day


def IST_time():
    return datetime.now().astimezone(utc)


def tz_now(tz: pytz = utc):
    dt = datetime.now(tz.utc)
    return dt.replace(tzinfo=tz)


def tz_from_iso(dt: str, to_tz: pytz = utc, format="%Y-%m-%dT%H:%M:%S.%f%z") -> datetime:
    date_time = datetime.strptime(dt, format)
    return date_time.astimezone(to_tz)


def start_of_week(dt: str, to_tz: pytz = utc) -> datetime:
    day_of_the_week = dt.weekday()
    return days_ago(dt=dt, days=day_of_the_week)


def end_of_week(dt: str, to_tz: pytz = utc) -> datetime:
    _start_of_week = start_of_week(dt=dt, to_tz=to_tz)
    return days_after(dt=_start_of_week, days=6)


def end_of_last_week(dt: str, to_tz: pytz = utc):
    _end_of_current_week = end_of_week(dt=dt, to_tz=to_tz)
    return days_ago(dt=_end_of_current_week, days=7)
