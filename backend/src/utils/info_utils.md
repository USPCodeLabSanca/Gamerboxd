# 💪 src/utils

## 📈 Funções principais
- Definir funções e classes auxiliares que contribuem com a organização do código

## ⚙️ Tecnologias utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/tutorial/dependencies/)

## Os utils
No arquivo `src/utils/utils.py` está definido:
- O decorador `db_query` para as funções que operam no DB, envolvendo-as num try-except;
- A classe de enumeráveis RelationshipStatus, que define as possíveis relações entre usuário-usuário, usuário-review e usuário-lista;
- Algumas outras funções utilitárias simples, principalmente para coisas de SQL.

## Os errors
No arquivo `src/utils/errors.py` está definido:
- As mensagens de erro que mais se repetem o longo do código;
- A classe de exceção QueryError, que é invocada pelas rotas e serviços quando alguma coisa dá errado. No arquivo `src/main.py`, tem um exception handler para essa classe, o que significa que o FastAPI direciona todos os raise QueryError para este handler, e ele por sua vez retorna para o cliente o problema que ocorreu

## A paginação
No arquivo `src/utils/pagination.py` está definido:
- A classe `PageQuery`, que organiza os diferentes query parameters que devem estar presentes para que se realize a paginação por keyset.
- A classe `PageResult`, que contém os campos que retornam em uma página de dados nas rotas que usam paginação por keyset
- A classe de dados `PageClauses`, que ajuda as funções de paginação a filtrar os registros e a encontrar a posição de parada da última página.