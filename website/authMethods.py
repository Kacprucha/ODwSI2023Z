import re

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