# 🛣️ src/routes

## 📈 Função principal
Definir o que acontece quando é feita uma chamada a uma url específica do backend

## ⚙️ Tecnologias utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/)

## Construção dos endpoints/rotas/controllers
Dentro de cada arquivo de rotas, é instanciado um roteador **`XYZ_router = InferringRouter(prefix = "/XYZ", tags = ["XYZ"])`**, que é basicamente o conjunto de todas as rotas pertinentes ao assunto XYZ.

Cada endpoint é contruido a partir de uma classe que recebe um decorador **`@cbv(XYZ_router)`**. Dentro desta classe, deve haver uma função que chama os serviços necessários para atingir a funcionalidade desejada do endopoint. 

Esta função precisa de um decorador **`XYZ_router.ação("\path")`** que determina que tipo de **ação** ela faz: post, get, put, delete, e qual o **path** da url para chegar nesse endpoint. 

Na maioria dos casos, a função vai receber um **schema** (que é definido em /models/schemas.py) como parâmetro, sendo necessário declarar qual schema que está sendo utilizado.

As funções também podem receber dependências, que são parâmetros que vem internamente de outras funções. As duas depêndencias mais importantes até agora são a **`get_conn()`** e a **`require_login()`**:

- **get_conn()** gera uma conexão necessária para manipular o nosso banco de dados
- **require_login()** verifica se o usuário está logado, e se tiver, retorna o user_id dele, caso não, envia um erro pro usuário que pediu. Essa dependência deve ser utilizada em endpoints onde é necessário estar logado, como por exemplo, na hora de escrever um review, ou seguir/bloquear outro usário


## Alguns padrões/convenções do código existente
- **Quando um endpoint funcionar como esperado**, retorne um objeto **`JSONResponse`**, onde o primeiro parâmetro é um dicionário que pode:
    - enviar uma **mensagem** falando que a operação deu certo
    - enviar um **schema** (use o método `.model_dump()` depois do schema) contendo os dados que foram pedidos à nossa API

- ... e o segundo parâmetro é o código de retorno da operação (por exemplo: status.HTTP_202_ACCEPTED)

- **Quando um endpoint encontrar algum erro**, dê um **`raise HTTPException(código_de_erro, detail= string_que_descreve_o_erro)`**.

- **Quando você utilizar um serviço relacionado ao banco de dados**, guarde o resultado desse serviço em uma variável que termina em **`_result`**. Isso porque os serviços do banco de dados sempre retornam um QueryResult (definido em src/utils/db.py), no qual você terá que antes verificar se a operação deu certo `(if not _result.success: raise...)` antes de acessar qual foi o resultado de verdade da sua requisição ao banco de dados `(variable = _result.obj)`

- As classes tem nome **`FuncionalidadeController`**

- Se você estiver importando uma biblioteca que realiza uma tarefa muito específica, a funcionalidade que você está escrevendo que depende dessa importação provavelmente deveria ser isolada em uma função em um dos arquivos da pasta src/services. **Os arquivos da pasta src/routes devem apenas contruir a ordem lógica dos serviços que ficam nos arquivos da pasta src/services**.

## Exemplos de endpoints
``` 
#/routes/order_routes.py

from models.schemas import Order
from services.security_services import encrypt_order_payment
from services.db_services import DB_create_order
from utils.dependencies import get_conn, require_login

order_router = InferringRouter(prefix="/order", tags=["order"])

@cbv(order_router)
class NewOrderController:

    @order_router.post("/new")
    async def new_order(order: Order, conn = Depends(get_conn), user_id = Depends(require_login))

        order_result = await DB_create_order(conn, user_id, order.price, order.item)

        if order_result.succes:
            order_number = order_result.obj

            return JSONResponse(
                {"message": f"O pedido {order_number} foi processado com sucesso!"},
                status.HTTP_202_ACCEPTED
            )

        else:
            raise HTTPException(500, detail = str(order_result.error))

@cbv(order_router)
class ViewOrderController:

    @order_router.get("/view")
    async def view_order(order: Order, conn = Depends(get_conn), user_id = Depends(require_login))

        order_result = await DB_read_order(conn, user_id, order.number)

        if order_result.succes:
            # suponha que view_order é um schema
            view_order = order_result.obj

            return JSONResponse(
                view_order.model_dump(),
                status.HTTP_202_ACCEPTED
            )

        else:
            raise HTTPException(500, detail = str(order_result.error))

```     