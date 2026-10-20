from pydantic import BaseModel

from .user import User
from .game import GameOverview


class Review(BaseModel):
    """Dados básicos de uma review"""
    rating_num: float                       # Avaliação numérica do game
    rating_text: str | None = None          # Texto de avaliação do game
    liked: bool                             # Se o usuário gostou do game ou não
    privacy: int                            # Privacidade da review


class ReviewIn(Review):
    """Dados para criação/edição de uma review"""
    game_id: int                            # Id do game avaliado
    time_played: float | None = None        # Quanto tempo o usuário jogou este jogo (se ele souber)
    completed: bool                         # Se o usuário zerou ou não o game    


class ReviewOutOverview(Review):
    """Dados de saída básicos sobre uma review"""
    review_id: str                          # Id da review  
    reviewer: User                          # Dados do criador da review              
    likes_count: int                        # Quantos likes a review tem
    game: GameOverview                      # Dados básicos sobre o game    
    created_at: str                         # Data de criação
    rel: int | None = None                  # Relacionamento de quem está vendo a lista com a lista


class ReviewOutComplete(ReviewOutOverview):
    """Dados de saída completos sobre uma review"""                      
    tag_count: int = 0                      # Quantas tags o usuário atribuiu a review
    tags: list[str] = []                    # Uma lista de tags que o usuário deu para esse jogo
    completed: bool                         # Se o usuário completou o game ou não
    time_played: float | None = None        # Quanto tempo o usuário jogou aquele game             
    updated_at: str                         # Data de ultima atualização da review
    rel: int | None = None                  # Relacionamento de quem está vendo a lista com a lista


class ReviewLike(BaseModel):
    """Dados sobre o like de uma review"""
    review_id: str
    user_id: str