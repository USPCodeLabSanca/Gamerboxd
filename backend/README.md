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


### Rodando o projeto

1. Na pasta `/src`, crie o arquivo `.env` e atribua as variáveis de ambiente do banco de dados conforme o arquivo `.env.example` mostra
2. Rode o programa com o comando `fastapi dev`


