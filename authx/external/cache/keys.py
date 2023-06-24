from typing import Any, List, Optional

from authx._internal import HTTPCache


class HTTPKeys:
    @staticmethod
    async def generate_key(
        key: str, config: HTTPCache, obj: Optional[Any] = None, obj_attr: Optional[str] = None
    ) -> str:
        """Converts a raw key passed by the user to a key with an parameter passed by the user and associates a namespace"""

        _key = (
            key.format(
                getattr(obj, obj_attr),
            )
            if obj
            else key
        )

        return await HTTPKeys.generate_namespaced_key(key=_key, config=config)

    @staticmethod
    async def generate_keys(
        keys: List[str], config: HTTPCache, obj: Optional[Any] = None, obj_attr: Optional[str] = None
    ) -> List[str]:
        """Converts a list of raw keys passed by the user to a list of namespaced keys with an optional parameter if passed"""
        return [await HTTPKeys.generate_key(key=k, config=config, obj=obj, obj_attr=obj_attr) for k in keys]

    @staticmethod
    async def generate_namespaced_key(key: str, config: HTTPCache) -> str:
        """Adds a namespace to the key"""
        return f"{config.namespace}:{key}".replace(" ", "")
