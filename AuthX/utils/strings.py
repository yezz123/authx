import hashlib
import hmac

from passlib.pwd import genword


def create_random_string(length: int = 256) -> str:
    # TODO: Add more characters
    return genword(length=length)


def sign_string(s: str, key: str) -> str:
    # TODO: Add more characters
    return hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()


def hash_string(s: str) -> str:
    # TODO: Add more algorithms
    return hashlib.sha256(s.encode()).hexdigest()


def check_signature(s: str, signature: str, key: str) -> bool:
    # TODO: Check if signature is valid
    return signature == hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()
