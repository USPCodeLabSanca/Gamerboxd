import bcrypt
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from jose import jwt

from models.schemas import ListIn, List, ReviewIn, ReviewLike
from services.db_services import DB_read_user_column, DB_read_user_lists, DB_read_user_game_review, DB_read_review_like


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
            raise HTTPException(400, detail=f'O username "{username}" já está sendo utilizado')

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
        raise HTTPException(400, detail="Este email já está atrelado a outra conta")


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


async def is_list_valid(conn, user_id: str, list: ListIn):
    
    # Limpar espaços extras
    for key, value in list:
        if isinstance(value, str) and value is not None:
            value = value.strip()

    # Verificar se já existe lista com esse nome
    user_lists_result = await DB_read_user_lists(conn, user_id)

    if not user_lists_result.success:
        raise HTTPException(500, detail= str(user_lists_result.error))
    
    user_lists = user_lists_result.obj

    for ul in user_lists.lists:
        if ul.name == list.name:
            raise HTTPException(400, detail=f"Você já possui uma lista com o nome {list.name}")

    # Verificar tamanhos máximos 
    if len(list.name) > 60:
        raise HTTPException(500, detail = f"O nome da lista não pode exceder 60 caracteres")
    
    if len(list.description) > 350:
        raise HTTPException(500, detail = f"A descrição da lista não pode exceder 350 caracteres")
    
    list_with_creator = List(name=list.name,
                            description=list.description,
                            is_private= list.is_private,
                            creator=user_id
                        )
    
    return list_with_creator

async def is_review_insertion_valid(conn, review: ReviewIn, user_id: str):
    user_review_result = await DB_read_user_game_review(conn, review.game, user_id)

    if not user_review_result.success:
        raise HTTPException(500, detail=str(user_review_result.error))
    
    if user_review_result.obj is not None:
        raise HTTPException(400, detail="Você já possui uma review desse jogo!")
    
    if len(review.rating_text) > 1000:
        raise HTTPException(400, detail = "O texto da review não pode exceder 1000 caracteres")
    
    return review

async def is_review_update_valid(conn, review: ReviewIn, old_game: int, user_id: str):

    if review.game != old_game:
        raise HTTPException(400, detail = "O jogo não pode ser alterado!")

    user_review_result = await DB_read_user_game_review(conn, review.game, user_id)

    if not user_review_result.success:
        raise HTTPException(500, detail=str(user_review_result.error))
    
    if user_review_result.obj is None:
        raise HTTPException(400, detail="Você não possui uma review com esse jogo!")
    
    if len(review.rating_text) > 1000:
        raise HTTPException(400, detail = "O texto da review não pode exceder 1000 caracteres")
    
    return review

async def is_liked(conn, review_id: str, user_id: str):
    like_result = await DB_read_review_like(conn, review_id, user_id)

    if not like_result.success:
        raise HTTPException(500, detail=str(like_result.error))
    
    return like_result.obj