import bcrypt
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
from jose import jwt

from models.schemas import ListIn, ReviewIn, UserIn
from services.db_services import DB_read_user_column, DB_read_list_name_taken, DB_read_user_game_review, DB_read_user_blockeds, DB_read_user_followeds
from utils import *


def passwords_match(stored_password, tested_password):
    """Testa se a senha que o usuário está tentando para logar é a mesma que ele cadastrou a criar a conta"""

    tested_password_bytes = tested_password.encode('utf-8')
    stored_password_bytes = stored_password.encode('utf-8')

    return bcrypt.checkpw(tested_password_bytes, stored_password_bytes)


def encrypt_password(password: str):
    """Encripta a senha"""

    password_bytes = password.encode('utf-8')
    encrypted_password_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return encrypted_password_bytes.decode('utf-8')


def encode_token(user_id, exp_in_minutes, key):
    """Cria os jwt para guardar nos cookies"""

    exp_time = datetime.now(tz=timezone.utc) + timedelta(minutes=exp_in_minutes)
    exp_time_int = int(exp_time.timestamp())

    claims = {"sub": user_id, "exp": exp_time_int}
    token = jwt.encode(claims, key, algorithm="HS256")

    return token


def decode_token(cookies, token_name, key):
    """Lê o que está num jwt"""

    return jwt.decode(cookies[token_name], key, algorithms=["HS256"], options={"verify_exp": False})


async def is_user_valid(conn, user: UserIn, user_id: str = None):
    """Testa se uma conta de usuário ao criar ou editar é válida para entrar no BD"""

    username = user.username.strip()

    if (len(username) < 4) or (len(username) > 24):
        raise UserError("O username deve ter entre 4 e 24 caracteres!")
        
    
    user_id_exists = await DB_read_user_column(conn=conn, column="id", username=user.username)

    if user_id_exists is not None:
        if ((user_id is not None) and (user_id_exists != user_id)) or (user_id is None):
            raise ConflictError(f'O username "{username}" já está sendo utilizado!')

    user.username = username
    
    email = user.email.strip()

    try:
        validate_email(email)

    except EmailNotValidError:
        raise UserError('Email inválido!')

    email_exists = await DB_read_user_column(conn, "id", email = email)
    if (email_exists is not None) and (email_exists != user_id):
        raise ConflictError(f'O email "{email}" já está sendo utilizado!')

    user.email = email
    
    if hasattr(user, "password"):
        password = user.password

        if not ((len(password) < 65) and (len(password) > 7)):
            raise UserError("A senha deve conter entre 8 a 64 caractéres!")
        
        if not any(char.isdigit() for char in password):
            raise UserError("A senha deve conter pelo menos um número!")
        
        if not any(not char.isalnum() for char in password):
            raise UserError("A senha deve conter pelo menos um símbolo!")
        
        if not (any(char.isupper() for char in password) and any(char.islower() for char in password)):
            raise UserError("A senha deve conter pelo menos uma letra minúscula e uma letra maiúscula!")

    if hasattr(user, "bio"):
        bio = user.bio

        if bio is not None:

            if len(bio) > 280:
                raise UserError("A bio não pode ter mais que 280 caractéres!")

            bio_stripped = bio.strip()

            if len(bio_stripped) == 0:
                raise UserError("A bio não pode ser apenas espaço vazio!")
        
    return user


async def is_list_valid(conn, user_id: str, list_in: ListIn, list_id: str | None = None):
    """Testa se uma lista ao criar ou editar é válida para entrar no BD"""

    name = list_in.name.strip()
    list_id_exists = await DB_read_list_name_taken(conn, list_in.name, user_id)

    if list_id_exists is not None:
        # Usuário está tentando criar uma lista nova com um nome que já está em uso
        if list_id is None:
            raise ConflictError(f'O usuário já possui uma lista com o nome "{list_in.name}"!')

        # Usuário está tentando editar uma lista e trocando o nome para um nome já em uso
        # sem ser o antigo da lista a ser editada
        if (list_id is not None) and (list_id_exists != list_id): 
            raise ConflictError(f'O usuário já possui uma lista com o nome "{list_in.name}"!')

    if len(name) > 45:
        raise UserError("O nome da lista não pode exceder 45 caractéres!")

    if len(name) == 0:
        raise UserError("O nome da lista não pode ser apenas espaço vazio!")

    list_in.name = name

    if list_in.description is not None:
        description = list_in.description.strip()

        if len(description) > 300:
            raise UserError("A descrição da lista não pode exceder 300 caractéres!")

        if len(description) == 0:
            raise UserError("A descrição da lista não pode ser apenas espaço vazio!")

        list_in.description = description
        
    return ListIn(
        name=list_in.name,
        description=list_in.description,
        is_private=list_in.is_private
    )


async def is_blocked(conn, user_id_blocker: str, user_id_blocked: str) -> bool:
    """Testa se um usuário foi bloqueado por outro"""

    mock_page = PageQuery(page_size=100)
    blocked_page = await DB_read_user_blockeds(conn, user_id_blocker, mock_page)
    if any([user_id_blocked == b.user_id for b in blocked_page.content]):
        return True

    mock_page.cursor = blocked_page.next_page
    while mock_page.cursor != None:
        blocked_page = await DB_read_user_blockeds(conn, user_id_blocker, mock_page)
        if any([user_id_blocked == b.user_id for b in blocked_page.content]):
            return True
        mock_page.cursor = blocked_page.next_page

    return False


async def already_follows(conn, user_id_follower:str, user_id_followed: str):
    """Testa se um usuário segue outro"""

    mock_page = PageQuery(page_size=100)
    followings_page = await DB_read_user_followeds(conn, user_id_follower, mock_page)

    if any([user_id_followed == f.user_id for f in followings_page.content]):
        return True
    mock_page.cursor = followings_page.next_page

    while mock_page.cursor != None:
        followings_page = await DB_read_user_followeds(conn, user_id_follower, mock_page)
        if any([user_id_followed == f.user_id for f in followings_page.content]):
            return True
        mock_page.cursor = followings_page.next_page

    return False     


async def is_review_insertion_valid(conn, review: ReviewIn, user_id: str):
    """Testa se uma review ao criar é válida para entrar no BD"""

    user_review = await DB_read_user_game_review(conn, review.game, user_id)

    if user_review is not None:
        raise ConflictError("Você já possui uma review desse jogo!")

    if review.rating_text is not None and len(review.rating_text) > 300:
        raise UserError("O texto da review não pode exceder 300 caracteres")
    
    return review


async def is_review_update_valid(conn, review: ReviewIn, old_game: int, user_id: str):
    """Testa se uma review ao editar é válida para entrar no BD"""

    if review.game != old_game:
        raise UserError("O jogo não pode ser alterado!")

    user_review = await DB_read_user_game_review(conn, review.game, user_id)

    if user_review is None:
        raise NotFoundError("Review antiga não encontrada!")
    
    if review.rating_text is not None and len(review.rating_text) > 300:
        raise UserError("O texto da review não pode exceder 300 caractéres")
    
    return review

