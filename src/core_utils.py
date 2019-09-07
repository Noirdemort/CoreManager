import re
import os
from hashlib import sha3_512


def is_invalid_email(mail):
    if re.match("[^@]+@[^@]+\.[^@]+", mail) != None:
        return False
    return True


def random_salt():
    iv = os.urandom(64)
    return str(int.from_bytes(iv, byteorder="big"))


def secure_hash(key, salt):
    hash = sha3_512((key + salt).encode())
    return hash.hexdigest()


def console_input(xs):
    replies = []
    for i in xs:
        za = input(i).strip()
        replies.append(za)
    return replies
