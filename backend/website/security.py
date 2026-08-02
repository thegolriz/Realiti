from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_ph = PasswordHasher()

DUMMY_HASH = _ph.hash("dummy-password-for-timing")


def hash_password(password):
    return _ph.hash(password)


def verify_password(stored_hash, password):
    try:
        return _ph.verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(stored_hash):
    return _ph.check_needs_rehash(stored_hash)
