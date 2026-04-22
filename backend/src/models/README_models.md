# 🗂️ /models 

## 📈 Função principal
Definir as entidades, os atributos e os relacionamentos destes utilizados no banco de dados do Gamerboxd.

## ⚙️ Tecnologias utilizadas
- [Postgresql](https://www.postgresql.org/docs/current/)
- [asyncpg (Python)](https://magicstack.github.io/asyncpg/current/)

## 📊 Diagrama de funcionamento
Utilizamos o [dbdiagram.io](https://dbdiagram.io/d/gamerboxd-69e7bbe7d80a958d1ca0428c) para esquematizar as tabelas do banco de dados do Gamerboxd.

## Construção das tabelas
Cada tabela é construida a partir de uma função assíncrona que recebe uma conexão de uma connection pool, criada no main.py. Com esta conexão, as tabelas podem ser criadas a partir das especificações expressas no diagrama:

```
#/models/tables

from asyncpg import PostgresError
from utils.db import DB_Result

async def create_table_employees(conn):

    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS employees(
                id INTEGER PRIMARY KEY,
                name VARCHAR(50),
                email TEXT UNIQUE,
                department TEXT REFERENCES departments(dept_id) ON DELETE CASCADE,
                employee_code TEXT NOT NULL,
                is_intern BOOL DEFAULT FALSE,
                age CONSTRAINT valid_age CHECK (age >= 16 AND age <= 100)
                created_at TIMESTAMPTZ DEFAULT now(),

                UNIQUE (department, employee_code)
                )
            ''')

    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")

```

