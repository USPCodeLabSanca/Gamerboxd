# 💪 src/utils

## 📈 Funções principais
- Definir funções auxiliares que contribuem com a organização do código

## ⚙️ Tecnologias utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/tutorial/dependencies/)

## As dependências
- No arquivo `src/utils/dependencies.py` estão algumas funções que são muito utilizadas nos endpoints. O FastAPI recomenda que estas funções muito repetidas se tornem dependências que serão chamadas pelo próprio FastAPI quando passadas como "callback" para a função Depends() antes de entrar na rota. 
Essas funções acessam, direta ou indiretamente, valores que foram guardados no app.state durante o lifespan_config (`src/config/lifespan.py`), então um benefício de deixá-las como dependência é que o FastAPI já injeta a requisição (request) nelas, o que torna mais fácil o acesso ao app.state.

## Os utils
- No arquivo `src/utils/utils.py` há uma classe de excessão que facilita o tratamento de erros dentro das rotas e um decorador para os serviços que mexem no BD que envolve as funções num try-except