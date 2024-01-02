from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidKey
from dotenv import load_dotenv
import re
import secrets
import string
import os

load_dotenv()
papper = os.getenv("PAPPER").encode('utf-8')

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

def defense_againts_sql_attack(input_string):
    sql_keywords = ['OR', 'UNION', 'DROP']
    
    # Check if has a forbidden symbols
    if re.search(r"[`;=-]", input_string):
        return False
    
    # Check if there is a space in string
    if input_string.find(' ') != -1:
        return False
    
    # Check if there is a forbiden word in input
    for keyword in sql_keywords:
        if keyword in input_string.upper():
            return False
    
    return True

def defense_againts_sql_attack_allow_space(input_string):
    sql_keywords = ['OR', 'UNION', 'DROP']
    
    # Check if has a forbidden symbols
    if re.search(r"[`;=-]", input_string):
        return False
    
    # Check if there is a forbiden word in input
    words = input_string.upper().split()
    for word in words:
        if word in sql_keywords:
            return False
    
    return True

def hash_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,
        salt=salt+papper,
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
        salt=salt+papper,
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