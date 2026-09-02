# ⚙️ src/config/lifespan.py


## 📈 Funções principais
- Instanciar o banco de dados e estabelecer o pool de conexões com ele;
- Estabelecer o pool de conexões externas para o uso da API;
- Armazenar as chaves importantes do .env no app para que elas fiquem facilmente acessível para as rotas e os serviços, 

## ⚙️ Tecnologias utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/advanced/events/#lifespan)
- [Asyncpg (Python, "Postgresql")](https://magicstack.github.io/asyncpg/current/)
- [aiohttp (Python)](https://docs.aiohttp.org/en/stable/)

## A classe LifespanConfig
A classe LifespanConfig contém a rotina de inicializar e de encerrar o backend. No método `__call__`, que é a função que estabelece esse ciclo de vida do programa, tudo antes do yield é realizado antes do nosso servidor ser ativado, e tudo depois do yield é realizado após.