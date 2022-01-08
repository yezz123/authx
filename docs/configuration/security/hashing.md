# Password Hashing

The HMAC is an algorithm that generates a hash of the message using a cryptographic hash function and a secret cryptographic key. It can be used to check data for integrity and authenticity.

The Python hashlib module is an interface for hashing messages easily. This contains numerous methods which will handle hashing any raw message in an encrypted format. The core purpose of this module is to use a hash function on a string, and encrypt it so that it is very difficult to decrypt it.

I Provide Some functions to help you hash your passwords.

- Create Random Strings:

```py
def create_random_string(length: int = 256) -> str:
    return genword(length=length)
```

- Sign Strings:

```py
def sign_string(s: str, key: str) -> str:
    return hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()
```

- Hash Strings:

```py
def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()
```

- Check Signatures:

```py
def check_signature(s: str, signature: str, key: str) -> bool:
    return signature == hmac.new(key.encode(), s.encode(), hashlib.sha256).hexdigest()
```
