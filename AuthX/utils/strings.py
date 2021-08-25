import hashlib
import hmac

from passlib.pwd import genword


def create_random_string(length: int = 256) -> str:
    return genword(length=length)


def sign_string(s: str, key: str) -> str:
    return hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()


def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def check_signature(s: str, signature: str, key: str) -> bool:
    return signature == hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()
