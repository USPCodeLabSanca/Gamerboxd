# Backend do Gamerboxd

## ⚙️ Tecnologias Utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/)
- [asyncpg (Python)](https://magicstack.github.io/asyncpg/current/)
- [Postgresql](https://www.postgresql.org/docs/current/)

## 📝 Como Rodar

### Criando o ambiente virtual
1. Entre na pasta do código fonte: `cd /backend`
2. Crie o ambiente virtual com `python3 -m venv .venv`
3. Ative o ambiente no terminal com `source .venv/bin/activate`
4. Selecione o interpretador de python do .venv
5. Uma vez dentro do ambiente virtual, instale as bibliotecas utilizadas no projeto com `pip install -r requirements.txt`
6. Para desativar o ambiente, use no terminal `deactivate`

### Rodando o projeto (ainda não funciona!)

1. Na pasta `/src`, crie o arquivo `.env` e atribua as variáveis de ambiente do banco de dados conforme o arquivo `.env.example` mostra
2. Rode o programa com o comando `fastapi dev`


