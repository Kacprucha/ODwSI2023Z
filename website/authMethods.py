from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidKey
import re
import secrets
import string

PAPPER = b'papper'

def is_str_complex(password):
    # Check if the password has at least 8 characters
    if len(password) < 8:
        return False

    # Check if the password has at least one number
    if not any(char.isdigit() for char in password):
        return False

    # Check if the password has at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    # Check if the password has at least one capital letter
    if not any(char.isupper() for char in password):
        return False

    # If all conditions are met, return True
    return True

def hash_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,
        salt=salt+PAPPER,
        length=32,
        backend=default_backend()
    )
    password_h = kdf.derive(password.encode('utf-8'))
    return password_h

def verify_password(password, hashed_password, salt):
    result = True
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,
        salt=salt+PAPPER,
        length=32,
        backend=default_backend()
    )

    try:
        kdf.verify(password.encode('utf-8'), hashed_password)
    except InvalidKey as e:
        result = False
    else:
        result = True
    
    return result

def generate_random_salt(length):
    random_numbers = [secrets.randbelow(256) for _ in range(length)]
    random_bytes = bytes(random_numbers)
    return random_bytes

def generate_code(length):
    return str(''.join(secrets.choice('0123456789') for _ in range(length)))