# Backend do Gamerboxd

## ⚙️ Principais Tecnologias Utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/)
- [asyncpg (Python)](https://magicstack.github.io/asyncpg/current/)
- [Postgresql](https://www.postgresql.org/docs/current/)

## 📝 Como Rodar

### Criando o ambiente virtual
1. Entre na pastao backend: `cd /backend`
2. Crie o ambiente virtual com `python3 -m venv .venv`
3. Ative o ambiente no terminal com `source .venv/bin/activate`
4. Selecione o interpretador de python do .venv
5. Uma vez dentro do ambiente virtual, instale as bibliotecas utilizadas no projeto com `pip install -r requirements.txt`
6. Para desativar o ambiente, use no terminal `deactivate`

### Instalando o pgadmin
1. Siga as instruções no site https://www.pgadmin.org/download/ para baixar o aplicativo do pgadmin
2. Rode o comando `sudo apt install postgresql postgresql-contrib` para baixar as funcionalidades do postgres no seu computador
3. Para acertar a senha do seu postgres rode o comando `sudo -i -u postgres psql`
4. Deve aparecer uma mensagem assim `postgres=#` no inicio da linha
5. Para colocar a senha, digite `\password postgres`
6. Insira a senha
7. Para sair do modo `postgres=#`, use o comando `\q`
8. Coloque a senha que você definiu no campo `VM_PASS` do `.env`
9. Abra o app do pgadmin
10. Clique em criar um novo servidor
11. O nome do seu novo servidor não importa
12. Abra a aba connection, o hostname é `localhost`, a port é `5432`, o username é `postgres` e a password é a que você definiu nos comandos acima.


### Instanciando as enviroment variables

1. Na pasta `/backend`, crie o arquivo `.env` e atribua as variáveis de ambiente do banco de dados conforme o arquivo `.env.example` mostra

### Rodando o app

1. Vá para a pasta do backend `cd /backend`
2. Caso não esteja ativado, ative o ambiente virtual no terminal `source .venv/bin/activate`
3. Vá para a pasta do código fonte `cd /src`
4. Rode o programa com o comando `fastapi dev`


### Rodando os testes

1. Abra o terminal
2. Vá para a pasta do backend `cd /backend`
3. Abra uma segunda aba no terminal. Se necessário, vá até a pasta do backend nessa nova aba também
4. Ative a venv (`source .venv/bin/activate`) em ambas as abas
5. Em uma das abas, vá para pasta do código fonte (`cd /src`) e rode a aplicação (`fastapi dev`)
6. Na outra aba, vá para a pasta de testes (`cd /src`) e rode o pytest (`pytest`)

Outros comandos mais específicos para rodar os testes:

| Comando                  | Descrição                                                                                     |
|--------------------------|-----------------------------------------------------------------------------------------------|
| `pytest test_*`          | Rodar algum conjunto específico de testes, * pode ser auth, lists, reviews, security ou users |
| `pytest -v`              | Rodar testes em modo verbose (mais descritivo caso uma falha aconteça)                        |
| `pytest -m "not rawg"`   | Rodar apenas os testes que não dependem da API de jogos RAWG                                  |
| `pytest -m "not pagination"`   | Rodar apenas os testes que não são de paginação (testes mais lentos)                    |


