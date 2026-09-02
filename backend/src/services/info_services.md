# 💪 src/services

## 📈 Funções principais
- Definir as diferentes ações que podem ser realizados no banco de dados
- Estabelecer verificações de segurança
- Conectar com a RAWG API 

## ⚙️ Tecnologias utilizadas
- [Asyncpg (Python, "Postgresql")](https://magicstack.github.io/asyncpg/current/)
- [jose (Python)](https://youtube.com/playlist?list=PLpdAy0tYrnKy3TvpCT-x7kGqMQ5grk1Xq&si=QLnk9gcBu543ayPL)
- [RAWG Api](https://api.rawg.io/docs/)

## Alguns padrões/convenções do código existente
- Para facilitar a leitura de qual método CRUD elas realizam, as funções na pasta `src/services/db_services` todas começam com algum dos seguintes prefixos:
    - DB_create_
    - DB_read_
    - DB_update_
    - DB_delete_

- As funções na pasta `src/services/db_services` todas possuem o decorador **@db_query**, o qual envolve a função num try-except para evitar repetição de código.
    