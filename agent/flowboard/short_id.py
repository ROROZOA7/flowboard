import secrets
import string

_ALPHABET = string.digits + "abcdefghijklmnopqrstuvwxyz"


def generate_short_id(length: int = 4) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
