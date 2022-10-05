from typing import Callable

import pytz

from authx.core.time import end_of_day, end_of_week, tz_now, utc
from authx.models.cache import HTTPCache


class HTTPExpiry:
    @staticmethod
    async def get_ttl(
        ttl_in_seconds: int = None,
        end_of_day: bool = True,
        end_of_week: bool = None,
        ttl_func: Callable = None,
        tz: pytz.timezone = utc,
    ) -> int:
        """Return the seconds till expiry of cache. Defaults to one day"""
        tz = HTTPCache.tz or tz

        if ttl_func:
            return await ttl_func()

        if ttl_in_seconds:
            return ttl_in_seconds

        if end_of_day:
            return await HTTPExpiry.expires_end_of_day(tz=tz)

        return await HTTPExpiry.expires_end_of_week(tz=tz) if end_of_week else 86400

    @staticmethod
    async def expires_end_of_week(tz=utc) -> int:
        """Returns the seconds till expiry at the end of the week"""
        now = tz_now()
        local_time = now.astimezone(tz=tz)
        eow = end_of_week(dt=local_time)
        return int((eow - local_time).total_seconds())

    @staticmethod
    async def expires_end_of_day(tz=utc) -> int:
        """Returns the seconds till expiry at the end of the day"""
        now = tz_now()
        local_time = now.astimezone(tz=tz)
        eod = end_of_day(dt=local_time)
        return int((eod - local_time).total_seconds())
