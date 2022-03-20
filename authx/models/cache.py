import redis
from pytz import timezone

from authx.core.time import utc
from authx.utils.logger import log_debug


class HTTPCache:
    redis_url: str
    namespace: str
    tz: timezone

    @classmethod
    def init(
        cls,
        redis_url: str,
        tz: timezone = utc,
        namespace: str = "httpcache",
    ):
        cls.redis_url = redis_url
        cls.namespace = namespace
        cls.tz = tz
        cls.redis_client = redis.Redis.from_url(redis_url)
        log_debug(msg=f"PING: {cls.redis_client.ping()}", loc=f"{__name__}")
        return cls

    @classmethod
    def __str__(cls):
        return f"<HTTPCache redis_url={cls.redis_url}, namespace={cls.namespace} client={cls.redis_client}"
