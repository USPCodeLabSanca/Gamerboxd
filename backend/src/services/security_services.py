import bcrypt
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
from jose import jwt

from models.schemas import ListIn, List, ReviewIn
from services.db_services import DB_read_user_column, DB_read_user_lists, DB_read_user_game_review, DB_read_user_blockeds, DB_read_user_follows
from utils.utils import QueryError


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


async def is_user_valid(user, conn, user_id):
    username = user.username.strip()

    if (len(username) < 4) or (len(username) > 24):
        raise QueryError(400, "O username deve ter entre 4 e 24 caracteres!")
        
    username_exists = await DB_read_user_column(conn=conn, column="id", username=username)

    if (username_exists is not None) and (username_exists != user_id):
        raise QueryError(409, f'O username "{username}" já está sendo utilizado!')

    user.username = username
    
    email = user.email.strip()

    try:
        validate_email(email)

    except EmailNotValidError:
        raise QueryError(400, 'Email inválido!')

    email_exists = await DB_read_user_column(conn, "id", email = email)
    if (email_exists is not None) and (email_exists != user_id):
        raise QueryError(409, f'O email "{email}" já está sendo utilizado!')

    user.email = email
    
    if hasattr(user, "password"):
        password = user.password

        if not ((len(password) < 65) and (len(password) > 7)):
            raise QueryError(400, "A senha deve conter entre 8 a 64 caractéres!")
        
        if not any(char.isdigit() for char in password):
            raise QueryError(400, "A senha deve conter pelo menos um número!")
        
        if not any(not char.isalnum() for char in password):
            raise QueryError(400, "A senha deve conter pelo menos um símbolo!")
        
        if not (any(char.isupper() for char in password) and any(char.islower() for char in password)):
            raise QueryError(400, "A senha deve conter pelo menos uma letra minúscula e uma letra maiúscula!")

    if hasattr(user, "bio"):
        bio = user.bio

        if bio is not None:

            if len(bio) > 280:
                raise QueryError(400, "A bio não pode ter mais que 280 caractéres!")

            bio_stripped = bio.strip()

            if len(bio_stripped) == 0:
                raise QueryError(400, "A bio não pode ser apenas espaço vazio!")
        
    return user


async def is_list_valid(conn, user_id: str, list: ListIn):
    
    # Limpar espaços extras
    for key, value in list:
        if isinstance(value, str) and value is not None:
            value = value.strip()

    # Verificar se já existe lista com esse nome
    user_lists = await DB_read_user_lists(conn, user_id)

    # Verificar se o usuário não possui uma lista com esse nome
    if any([ul.name == list.name for ul in user_lists.lists]):
        raise QueryError(400, f"Você já possui uma lista com o nome {list.name}")

    # Verificar tamanhos máximos 
    if len(list.name) > 60:
        raise QueryError(400, "O nome da lista não pode exceder 60 caractéres")

    if len(list.description) > 300:
        raise QueryError(400, "A descrição da lista não pode exceder 300 caractéres")
    
    list_with_creator = List(
        name=list.name,
        description=list.description,
        is_private= list.is_private,
        creator=user_id
    )
    
    return list_with_creator


async def is_blocked(conn, user_id_blocker: str, user_id_blocked: str):
    blockeds = await DB_read_user_blockeds(conn, user_id_blocker)
    return any([user_id_blocked == b["blocked"] for b in blockeds])


async def already_follows(conn, user_id_follower:str, username_followed:str):
    followings = await DB_read_user_follows(conn, user_id_follower)

    for f in followings.followings:
        if username_followed == f.username:
            return True
        
    return False


async def is_review_insertion_valid(conn, review: ReviewIn, user_id: str):

    user_review = await DB_read_user_game_review(conn, review.game, user_id)

    if user_review is not None:
        raise QueryError(400, "Você já possui uma review desse jogo!")

    if review.rating_text > 1000:
        raise QueryError(400, "O texto da review não pode exceder 1000 caracteres")
    
    return review


async def is_review_update_valid(conn, review: ReviewIn, old_game: int, user_id: str):

    if review.game != old_game:
        raise QueryError(400, "O jogo não pode ser alterado!")

    user_review = await DB_read_user_game_review(conn, review.game, user_id)

    if user_review is None:
        raise QueryError(400, "Você não possui uma review com esse jogo!")
    
    if review.rating_text > 1000:
        raise QueryError(400, "O texto da review não pode exceder 1000 caracteres")
    
    return review

