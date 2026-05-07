# 💪 src/services

## 📈 Função principal
Definir as diferentes ações que podem ser utilizadas pelas chamadas ao backend

## ⚙️ Tecnologias utilizadas
- Várias bibliotecas do Python

## Construção dos services
Dentro de cada arquivo de serviços, haverá várias funções que realizam alguma ação. Os parâmetros que cada função recebe é bem flexível e depende do que ela precisa para agir. As funções no arquivo `src/services/db_services.py` todas recebem a conexão com o banco de dados (conn) para realizar a operação necessária.

## Alguns padrões/convenções do código existente
- Para facilitar a leitura de qual método CRUD elas realizam, as funções no arquivo `src/services/db_services.py` todas começam com algum dos seguintes prefixos:
    - DB_create_
    - DB_read_
    - DB_update_
    - DB_delete_

- As funções no arquivo `src/services/db_services.py` todas retornam um **`DB_Result`**, que é o padrão para informar o controller o resultado da ação no banco de dados.

## Exemplos de serviço
``` 
#/services/db_services.py

async def DB_create_order(conn, user_id: str, price: float, item: str):

    order_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Orders(order_id, customer, price, item)
            VALUES($1, $2, $3)
        ''', order_id, user_id, price, item)
        
    except Exception as e:
        return DB_Result(success=False, error=e)
    
    else:
        return DB_Result(success=True, message="Pedido criado com sucesso!", obj=order_id)

```     