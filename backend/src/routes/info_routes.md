# 🛣️ src/routes

## 📈 Funções principais
- Definir os procedimentos realizados quando chamadas são feitas a urls específicas do backend

## ⚙️ Tecnologias utilizadas
- [FastAPI (Python)](https://fastapi.tiangolo.com/)

## Construção dos endpoints/rotas/controllers
Dentro de cada arquivo de rotas, é instanciado um roteador **`xyz_router = APIRouter(prefix="/xyzs", tags=["xyz"])`**, que é basicamente o conjunto de todas as rotas pertinentes ao assunto XYZ.

Cada endpoint é contruido a partir de uma função que recebe um decorador **`@xyz_router.ação("/path")`** que determina que tipo de **ação** ela faz (post, get, put, patch, delete) e qual o **path** da url para chegar nesse endpoint (relativo à url do roteador!). 

As funções de rota recebem como parâmetro:

### Path parameters
Path parameters ficam dentro da url do endpoint, separado por /, com o propósito principal de identificar sobre o que/quem a ação está atuando. Por exemplo, temos a rota para seguir usuários `POST /users/follow/{user_id}`; user_id é um path parameter que identifica qual usuário se pretende seguir.

### Query parameters
Query paremeters ficam após a url do endpoint, separado por ?, para o primeiro query parameter e &, para os subsequentes query parameters, com o propósito principal de filtrar, ordenar ou paginar os recursos sobre os quais a ação está atuando. Por exemplo, temos a rota para buscar games `GET /games?search=str&page_size=10`; seacrh é um query parameter que representa a busca do usuário por games relacionados a um titulo específico e page_size é um outro query parameter que diz respeito a quantos games o frontend quer que envie.

### Request_body
O request_body é um conjunto de pares chave-valor, enviados separadamente da url, quando se é necessário enviar muitas informações de uma vez só. Nas rotas, eles são definidos por **schemas** (dispostos em `src/models/schemas`), sendo necessário declarar qual schema que está sendo utilizado para cada rota.

### Dependências
Dependências são funções utilitárias que se repetem muito ao longo das rotas, principalmente para **validar dados de entrada** (como os 3 parâmetros abordados anteriormente) e para **recuperar variáveis de enviroment**. O FastAPI recomenda passar estas como callbacks para a função **Depends** na declaração da rota, pois dessa forma elas serão executadas antes mesmo de entrar no endpoint, evitando assim a necessidade de ficar chamando as funções dentro de cada uma das rotas.
Como mencionado antes, muitas das dependências acessam, direta ou indiretamente, variáveis de enviroment que foram guardadas no app.state durante o lifespan_config (`src/config/lifespan.py`), então um benefício de deixá-las como dependência é que acessar essas variáveis por meio da requisão (request) se torna mais limpo.

As duas depêndencias mais importantes até agora são a **`get_conn`** e a **`require_login`**:

- **get_conn()** gera uma conexão necessária para manipular o nosso banco de dados
- **require_login()** verifica se o usuário está logado, e se tiver, retorna o user_id dele, caso não, envia um erro pro usuário que pediu. Essa dependência deve ser utilizada em endpoints onde é necessário estar logado, como por exemplo, na hora de escrever um review, ou seguir/bloquear outro usuário.

Essas e outras dependências estão dispostas em `src/routes/dependencies.py`.

## Alguns padrões/convenções do código existente
- **Quando um endpoint funcionar como esperado**, retorne um objeto **`JSONResponse`** com um dicionário que pode:
    - enviar uma **mensagem** falando que a operação deu certo
    - enviar um **schema** (use o método `.model_dump()` depois do schema) contendo os dados que foram pedidos à nossa API

- **Quando um endpoint encontrar algum erro**, dê um **`raise err.QueryError(código_de_erro, string_descrevendo_o_erro)`**. Note que no arquivo `src/utils/errors.py` tem várias strings de erro comuns já expostas, então é sempre bom olhar lá primeiro para ver se o seu erro já está documententado.