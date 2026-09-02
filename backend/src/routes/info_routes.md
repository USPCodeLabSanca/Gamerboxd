# 🛣️ src/routes

## 📈 Funções principais
- Definir os procedimentos realizados quando chamadas são feitas a urls específicas do backend

## ⚙️ Tecnologias utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/)

## Construção dos endpoints/rotas/controllers
Dentro de cada arquivo de rotas, é instanciado um roteador **`xyz_router = APIRouter(prefix="/xyz", tags=["xyz"])`**, que é basicamente o conjunto de todas as rotas pertinentes ao assunto XYZ.

Cada endpoint é contruido a partir de uma função que recebe um decorador **`@xyz_router.ação("/path")`** que determina que tipo de **ação** ela faz: post, get, put, delete, e qual o **path** da url para chegar nesse endpoint (relativo à url do roteador!). 

Na maioria dos casos, a função vai receber um **schema** (que é definido em /models/schemas) como parâmetro, sendo necessário declarar qual schema que está sendo utilizado.

As funções também podem receber dependências, que são parâmetros que vem internamente de outras funções. As duas depêndencias mais importantes até agora são a **`get_conn()`** e a **`require_login()`**:

- **get_conn()** gera uma conexão necessária para manipular o nosso banco de dados
- **require_login()** verifica se o usuário está logado, e se tiver, retorna o user_id dele, caso não, envia um erro pro usuário que pediu. Essa dependência deve ser utilizada em endpoints onde é necessário estar logado, como por exemplo, na hora de escrever um review, ou seguir/bloquear outro usário


## Alguns padrões/convenções do código existente
- **Quando um endpoint funcionar como esperado**, retorne um objeto **`JSONResponse`** com um dicionário que pode:
    - enviar uma **mensagem** falando que a operação deu certo
    - enviar um **schema** (use o método `.model_dump()` depois do schema) contendo os dados que foram pedidos à nossa API

- **Quando um endpoint encontrar algum erro**, dê um **`raise QueryError(código_de_erro, string_descrevendo_o_erro)`**.

- Se você estiver importando uma biblioteca que realiza uma tarefa muito específica, a funcionalidade que você está escrevendo que depende dessa importação provavelmente deveria ser isolada em uma função em um dos arquivos da pasta src/services. **Os arquivos da pasta src/routes devem apenas contruir a ordem lógica dos serviços que ficam nos arquivos da pasta src/services**.