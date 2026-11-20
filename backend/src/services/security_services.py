from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from email_validator import validate_email, EmailNotValidError
from fastapi import Response, Request
from jose import jwt
import math
import re

from ..models.schemas import ListNew, ListEdit, ReviewNew, ReviewEdit, UserNew, UserEdit
from .db_services import (
    DB_read_already_follows,
    DB_read_is_blocked,
    DB_read_game_basic,
    DB_read_user_column,
    DB_read_list_id,
    DB_read_list_name,
    DB_read_list_desc,
    DB_read_list_privacy,
    DB_read_review_id,
    DB_read_review_creator, 
    DB_read_review_privacy
)

from ..utils import errors as err
from ..utils.utils import RelationshipStatus


def passwords_match(stored_password: str, tested_password: str):
    """Testa se a senha que o usuário está tentando para logar é a mesma que ele cadastrou a criar a conta"""

    ph = PasswordHasher()
    try:
        ph.verify(stored_password, tested_password)

    except VerifyMismatchError:
        return False

    return True


def hash_password(password: str):
    """Passa a senha por um hash"""

    ph = PasswordHasher()
    return ph.hash(password)


def add_cookie(response: Response, jwt_config: dict, name: str, user_id: str):
    """Adiciona um cookie à resposta HTTP"""

    claims = {
        "sub": user_id,
        "exp": jwt_config[name + "_exp"],
        "iss": jwt_config["iss"],
        "aud": jwt_config["aud"]
    }
 
    key = jwt_config["key"]

    new_token = encode_token(key, claims)
    secure = jwt_config["secure"]

    response.set_cookie(
        name,
        new_token,
        secure=secure,
        httponly=True,
        samesite="strict",
        max_age = int(60 * jwt_config[name + "_exp"]) if "refresh" in name else None
    ) 

    return response 


def encode_token(key: str, claims: dict):
    """Cria um jwt para guardar nos cookies"""

    exp_time = datetime.now(tz=timezone.utc) + timedelta(minutes=claims.pop("exp", 10))
    exp_time_int = int(exp_time.timestamp())
    claims["exp"] = exp_time_int

    return jwt.encode(claims, key, algorithm="HS256")


def decode_token(token: str, key: str, issuer: str, audience: str):
    """Lê o que está num jwt"""

    return jwt.decode(
        token, 
        key,
        algorithms="HS256",
        issuer=issuer,
        audience=audience,
        options={
            "require_exp": True, 
            "verify_exp": False,
            "require_sub": True, 
            "require_iss": True,
            "require_aud": True,             
        },
    )


async def is_username_valid(conn, username: str, user_id: str = None):
    """Testa se um username ao criar ou editar é válido para entrar no DB"""

    username = username.strip()

    if (len(username) < 4) or (len(username) > 24):
        raise err.QueryError(400, "O username deve ter entre 4 e 24 caracteres!")
        
    user_id_exists = await DB_read_user_column(conn, column="id", username=username)

    if user_id_exists is not None:
        if (user_id_exists != user_id) or (user_id is None):
            raise err.QueryError(409, f'O username "{username}" já está sendo utilizado!')

    tokens = re.split(r'[._-]+', username)
    joined_tokens = "".join(tokens)

    if not joined_tokens.isalnum():
        raise err.QueryError(400, 'O username só pode conter Aa-Zz, 0-9, e os caractéres "-", "_", "."')

    return username


async def is_email_valid(conn, email: str, user_id: str = None):
    """Testa se um email ao criar ou editar é válido para entrar no DB"""

    email = email.strip()

    try:
        validate_email(email)

    except EmailNotValidError:
        raise err.QueryError(400, 'Email inválido!')

    email_exists = await DB_read_user_column(conn, "id", email = email)
    if (email_exists is not None) and (email_exists != user_id):
        raise err.QueryError(409, f'O email "{email}" já está sendo utilizado!')

    return email


def is_password_valid(password: str):
    """Testa se uma senha é segura o suficiente para entrar no DB"""

    if not ((len(password) < 65) and (len(password) > 7)):
        raise err.QueryError(400, "A senha deve conter entre 8 a 64 caracteres!")
    
    if not any(char.isdigit() for char in password):
        raise err.QueryError(400, "A senha deve conter pelo menos um número!")
    
    if not any(not char.isalnum() for char in password):
        raise err.QueryError(400, "A senha deve conter pelo menos um símbolo!")
    
    if not (any(char.isupper() for char in password) and any(char.islower() for char in password)):
        raise err.QueryError(400, "A senha deve conter pelo menos uma letra minúscula e uma letra maiúscula!")


def is_bio_valid(bio: str | None):
    """Testa se a bio do usuário segue a regras de negócio do modelo"""

    if bio is not None:
        bio = bio.strip()

        if len(bio) > 280:
            raise err.QueryError(400, "A bio não pode ter mais que 280 caracteres!")

        if len(bio) == 0:
            raise err.QueryError(400, "A bio não pode ser apenas espaço vazio!")

    return bio


async def is_user_insertion_valid(conn, user: UserNew):
    """Testa se uma conta de usuário ao criar é válida para entrar no DB"""

    user.username = await is_username_valid(conn, user.username)
    user.email = await is_email_valid(conn, user.email)
    is_password_valid(user.password)
        
    return user


async def is_user_update_valid(conn, user: UserEdit, user_id: str):
    """Testa se uma conta de usuário ao editar é válida para entrar no DB"""

    user.username = await is_username_valid(conn, user.username, user_id)
    user.bio = is_bio_valid(user.bio)

    return user


async def is_list_insertion_valid(conn, user_id: str, list_in: ListNew):
    """Testa se uma lista ao criar é válida para entrar no DB"""

    name = list_in.name.strip()

    # Usuário está tentando criar uma lista nova com um nome que já está em uso
    if await DB_read_list_id(conn, name, user_id) is not None:
        raise err.QueryError(409, f'Você já possui uma lista com o nome "{list_in.name}"!')

    return _basic_list_checks(list_in)


async def is_list_update_valid(conn, user_id: str, list_in: ListEdit, list_id: str):
    """Testa se uma lista ao editar é válida para entrar no DB"""

    name = list_in.name.strip()
    desc = list_in.description.strip() if list_in.description is not None else None

    current_list_name = await DB_read_list_name(conn, list_id)
    current_list_desc = await DB_read_list_desc(conn, list_id)

    if current_list_name in ("Jogos Completados", "Jogos Favoritos"): 
        if (name != current_list_name) or (desc != current_list_desc):
            raise err.QueryError(435, "Não é possível alterar esses detalhes dessa lista!")

    list_id_exists = await DB_read_list_id(conn, list_in.name, user_id)

    # Usuário está tentando editar uma lista e trocando o nome para um nome já em uso
    if list_id_exists is not None and (list_id_exists != list_id):
        raise err.QueryError(409, f'Você já possui uma lista com o nome "{list_in.name}"!')
      
    return _basic_list_checks(list_in)



def _basic_list_checks(list_in: ListNew | ListEdit):
    """Valida as regras mais simples de campos da lista"""

    name = list_in.name.strip()
    desc = list_in.description.strip() if list_in.description is not None else None

    if len(name) > 45:
        raise err.QueryError(400, "O nome da lista não pode exceder 45 caracteres!")

    if len(name) == 0:
        raise err.QueryError(400, "O nome da lista não pode ser apenas espaço vazio!")

    if desc is not None:
        if len(desc) > 300:
            raise err.QueryError(400, "A descrição da lista não pode exceder 300 caracteres!")

        if len(desc) == 0:
            raise err.QueryError(400, "A descrição da lista não pode ser apenas espaço vazio!")

    if list_in.privacy not in (RelationshipStatus.ANY, RelationshipStatus.FOLLOWED, RelationshipStatus.OWNER):
        raise err.QueryError(422, "A privacidade da lista não é um dos valores válidos!")

    list_in.name = name
    list_in.description = desc        
    return list_in


async def is_review_insertion_valid(conn, review: ReviewNew, user_id: str):
    """Testa se uma review ao criar é válida para entrar no DB"""

    if await DB_read_review_id(conn, user_id, review.game_id) is not None:
        raise err.QueryError(409, "Você já possui uma review desse jogo!")

    if await DB_read_game_basic(conn, review.game_id) is None:
        raise err.QueryError(404, err.GAME_NOT_FOUND_MSG)

    return _basic_review_checks(review)


async def is_review_update_valid(conn, review: ReviewEdit, review_id: str, user_id: str):
    """Testa se uma review ao editar é válida para entrar no DB"""

    reviewer_id = await DB_read_review_creator(conn, review_id)

    if reviewer_id != user_id:
        raise err.QueryError(403, err.LACK_OF_REVIEW_OWNERSHIP_MSG)
    
    return _basic_review_checks(review)


def _basic_review_checks(review: ReviewNew | ReviewEdit):
    """Valida as regras mais simples de campos da review"""

    if review.rating_text is not None:
        review.rating_text = review.rating_text.strip()

        if len(review.rating_text) > 300:
            raise err.QueryError(400, "O texto da review não pode exceder 300 caracteres!")

        if len(review.rating_text) == 0:
            raise err.QueryError(400, "O texto da review não pode ser apenas espaço vazio!")

    if not 0 <= review.rating_num <= 5.0:
        raise err.QueryError(422, "A avaliação numérica da review tem que estar entre 0 e 5, com step de 0.5!")
    
    remainder = review.rating_num % 0.5

    if not (math.isclose(remainder % 0.5, 0.0, abs_tol=1e-9) or math.isclose(remainder % 0.5, 0.5, abs_tol=1e-9)):
        raise err.QueryError(422, "A avaliação numérica da review tem que estar entre 0 e 5, com step de 0.5!")

    review.rating_num = round(review.rating_num*2)/2

    if review.time_played is not None and review.time_played < 0:
        raise err.QueryError(400, "O tempo de jogo não pode ser negativo!")

    if review.privacy not in (RelationshipStatus.ANY, RelationshipStatus.FOLLOWED, RelationshipStatus.OWNER):
        raise err.QueryError(422, "A privacidade da review não é um dos valores válidos!")
       
    return review


async def classify_relationship(conn, atv: str | None, pas: str):
    """Classifica o relacionamente de 2 usuários"""

    if atv is None:
        return RelationshipStatus.ANY

    if atv == pas:
        return RelationshipStatus.OWNER

    atv_follows_pas, pas_follows_atv = await DB_read_already_follows(conn, atv, pas), await DB_read_already_follows(conn, pas, atv)

    follow_relationship = atv_follows_pas + 2*pas_follows_atv

    if follow_relationship > 0:
        return RelationshipStatus(10*follow_relationship)
    
    atv_blocked_pas, pas_blocked_atv = await DB_read_is_blocked(conn, atv, pas), await DB_read_is_blocked(conn, pas, atv)

    block_relationship = atv_blocked_pas + 2*pas_blocked_atv

    if block_relationship > 0:
        return RelationshipStatus(-10*block_relationship)

    else:
        return RelationshipStatus.ANY


def resolve_user_clearence(rel: int, uncleared_rels: dict = {}):
    """Verifica se a relação entre 2 usuários é motivo para levantar erro"""

    basic_uncleared_relationships = {
        RelationshipStatus.BLOCKED: (433, err.BLOCKED_BY_USER_MSG),
        RelationshipStatus.BLOCKER: (400, err.USER_BLOCKED_OTHER_MSG)
    }

    total_uncleared_rels = uncleared_rels | basic_uncleared_relationships

    if rel in total_uncleared_rels.keys():
        raise err.QueryError(*total_uncleared_rels[rel])


async def resolve_list_clearence(conn, list_id: str | None, user_id_atv: str | None, user_id_creator: str, uncleared_rels: dict = {}):
    """Verifica se a relação entre 2 usuários ou se a camada de privacidade de uma lista é motivo para levantar erro"""

    list_privacy = await DB_read_list_privacy(conn, list_id) if list_id is not None else None
    rel = await classify_relationship(conn, user_id_atv, user_id_creator)

    if (list_privacy is not None) and (0 <= rel < list_privacy):
        raise err.QueryError(403, err.PRIVATE_LIST_MSG)

    basic_uncleared_relationships = {
        RelationshipStatus.BLOCKED: (433, err.BLOCKED_BY_LIST_OWNER_MSG),
        RelationshipStatus.BLOCKER: (400, err.USER_BLOCKED_LIST_OWNER_MSG)
    } 

    total_uncleared_rels = uncleared_rels | basic_uncleared_relationships

    if rel in total_uncleared_rels.keys():
        raise err.QueryError(*total_uncleared_rels[rel])

    return rel


async def resolve_review_clearence(conn, review_id: str | None, user_id_atv: str | None, user_id_creator: str, uncleared_rels: dict = {}):
    """Verifica se a relação entre 2 usuários ou se a camada de privacidade de uma review é motivo para levantar erro"""

    rel = await classify_relationship(conn, user_id_atv, user_id_creator)
    review_privacy = await DB_read_review_privacy(conn, review_id) if review_id is not None else None

    if (review_privacy is not None) and (0 <= rel < review_privacy):
        raise err.QueryError(403, err.PRIVATE_REVIEW_MSG)

    basic_uncleared_relationships = {
        RelationshipStatus.BLOCKED: (433, err.BLOCKED_BY_REVIEW_OWNER_MSG),
        RelationshipStatus.BLOCKER: (400, err.USER_BLOCKED_REVIEW_OWNER_MSG)
    }

    total_uncleared_rels = uncleared_rels | basic_uncleared_relationships

    if rel in total_uncleared_rels.keys():
        raise err.QueryError(*total_uncleared_rels[rel])


