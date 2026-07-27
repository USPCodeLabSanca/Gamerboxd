# 🗂️ src/models/tables.py
### Última atualização: 27/07/26

## 📈 Função principal
Definir as entidades, os atributos e os relacionamentos utilizados no banco de dados do Gamerboxd.

## ⚙️ Tecnologias utilizadas
- [Postgresql](https://www.postgresql.org/docs/current/)
- [asyncpg](https://magicstack.github.io/asyncpg/current/)

## 📊 Diagrama de funcionamento
Utilizamos o [dbdiagram.io](https://dbdiagram.io/d/gamerboxd-69e7bbe7d80a958d1ca0428c) para esquematizar as tabelas do banco de dados do Gamerboxd.

## Construção das tabelas
As tabelas são construidas a partir de uma função assíncrona que recebe uma conexão de uma connection pool, criada no src/config/lifespan_config. Com esta conexão, as tabelas podem ser criadas a partir das especificações expressas no diagrama acima.

## Exemplo de tabela
```python
#/models/tables.py
from asyncpg import PostgresError

TABLES = {
    "Employees":
    ''' 
        CREATE TABLE IF NOT EXISTS Employees (
            employee_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(25) UNIQUE NOT NULL,
            email VARCHAR(256) UNIQUE NOT NULL,
        )   
    ''',

    "Jobs":
    '''
        CREATE TABLE IF NOT EXISTS Jobs (
            job_id INTEGER PRIMARY KEY,
            job_name VARCHAR(50) NOT NULL,
            salary FLOAT NOT NULL,
        )
    ''',

    "EmployeeJob":
    '''
        CREATE TABLE IF NOT EXISTS EmployeeJob (
            employee VARCHAR(36) REFERENCES Employees(employee_id) ON DELETE CASCADE,
            job INTERGER REFERENCES Jobs(job_id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (employee, job)
        )
    ''',
}

async def create_tables(conn):
    try:
        async with conn.transaction():
            for key, value in TABLES.items():
                await conn.execute(value)

    except PostgresError as e:
        raise RuntimeError(e)

```

