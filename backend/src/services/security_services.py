import bcrypt
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from jose import jwt

from services.db_services import DB_read_user_column


def passwords_match(stored_password, tested_password):
    tested_password_bytes = tested_password.encode('utf-8')
    stored_password_bytes = stored_password.encode('utf-8')

    return bcrypt.checkpw(tested_password_bytes, stored_password_bytes)


def encrypt_password(password: str):
    password_bytes = password.encode('utf-8')
    encrypted_password_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return encrypted_password_bytes.decode('utf-8')


def encode_token(user_id, exp_in_minutes, key):
    exp_time = datetime.now(tz=timezone.utc) + timedelta(minutes=exp_in_minutes)
    exp_time_int = int(exp_time.timestamp())

    claims = {"sub": user_id, "exp": exp_time_int}
    token = jwt.encode(claims, key, algorithm="HS256")

    return token


def decode_token(cookies, token_name, key):
    return jwt.decode(cookies[token_name], key, algorithms=["HS256"], options={"verify_exp": False})


async def is_username_valid(username: str, conn):
        username = username.strip()

        username_length = len(username)
        username_has_right_length = (username_length) < 25 and (username_length > 3)

        if not username_has_right_length:
            raise HTTPException(400, detail="O username deve ter entre 4 e 24 caracteres")
            
        username_exists_result = await DB_read_user_column(conn, "username", username = username)

        if not username_exists_result.success:
            raise HTTPException(500, detail=str(username_exists_result.error))

        if username_exists_result.obj:
            raise HTTPException(409, detail=f'O username "{username}" já está sendo utilizado')

        return username


async def is_email_valid(email: str, conn):
    email = email.strip()

    try:
        validate_email(email)

    except EmailNotValidError:
        raise HTTPException(400, detail="Email inválido")

    email_exists_result = await DB_read_user_column(conn, "email", email = email)
    
    if not email_exists_result.success:
        raise HTTPException(500, detail=str(email_exists_result.error))

    
    if email_exists_result.obj:
        raise HTTPException(409, detail="Este email já está atrelado a outra conta")


    return email


def is_password_valid(password: str):
        password = password.strip()
        password_length = len(password)

        pwd_has_right_length = (password_length) < 65 and (password_length > 7)
        pwd_has_number = any(char.isdigit() for char in password)
        pwd_has_special = any(not char.isalnum() for char in password)
        pwd_has_capital = any(char.isupper() for char in password)
        pwd_has_lower = any(char.islower() for char in password)
        
        if not all([pwd_has_capital, pwd_has_lower, pwd_has_number, pwd_has_special, pwd_has_right_length]):
            raise HTTPException(409, detail="A senha deve conter entre 8 a 64 caractéres, com pelo menos uma letra minúscula, uma letra maiúscula, um número e um símbol")
            
        return password