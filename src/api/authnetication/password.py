import bcrypt


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    :param password: plain password
    :return: hashed password
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password using bcrypt.

    :param plain_password: plain password
    :param hashed_password: hashed password
    :return: whether plain password matches hashed password
    """
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_byte_enc = hashed_password.encode("utf-8")
    return bcrypt.checkpw(
        password=password_byte_enc,
        hashed_password=hashed_password_byte_enc,
    )
