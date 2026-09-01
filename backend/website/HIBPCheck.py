import requests
import hashlib

BASE_API = 'https://api.pwnedpasswords.com/range/'


def hashMode(password):
    digest = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    return beenPwned(prefix, suffix)


def beenPwned(prefix, suffix) -> str:
    try:
        r = requests.get(BASE_API+prefix, timeout=5)
        if r.status_code != 200:
            return "unknown"
        linesR = [line.split(":")[0] for line in r.text.splitlines()]
        if suffix in linesR:
            return "compromised"
        return "clean"
    except requests.exceptions.RequestException:
        return "unknown"
