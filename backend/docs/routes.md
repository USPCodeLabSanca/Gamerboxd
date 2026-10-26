# 📡 Documentação das Rotas

## Sumário
- [Rotas paginadas](#rotas-paginadas)
- [Schemas padrão](#schemas-padrão)
- [Privacies e rels dos schemas](#privacies-e-rels-dos-schemas)
- [Cookies de autenticação](#cookies-de-autenticação)
- [Erros](#erros)


## Rotas paginadas
 
As rotas (menos a de buscar games!) que retornam vários dados de uma vez estão paginadas pelo método de cursores (ou keyset). Paginação por cursor é uma técnica de consulta em bancos de dados que utiliza o valor de um registro anterior (como um ID ou data) como ponto de referência para buscar os próximos dados.

### Query parameters

Os query parameters para definir uma página de busca (**\_\_PAGE_QUERY\_\_**) são:

| Parâmetro   | Tipo           | Obrigatório | Padrão | Descrição                                  |
|-------------|----------------|-------------|--------|--------------------------------------------|
| `page_size` | int            | ❌          | 10     | Número de itens por página                 |
| `cursor`    | string ou null | ❌          | null   | Cursor para buscar a próxima página        |
| `search`    | string ou null | ❌          | null   | Parâmetro de busca por um termo específico |
| `order`     | string ou null | ❌          | null   | Qual ordenação de dados usar               |

Algumas regras e noções para se atentar são:
- **page_size**: Tem que ser um inteiro entre 1 e 50.

- **cursor**: Para a primeira busca, o cursor vai como null, pois o ponto de referência dos dados é zero. Para buscas subsequentes, ele vai ser uma string gerada e devolvida completamente pelo backend.

- **search**: Cada rota vai ter um "propósito" diferente para o search. Por exemplo, na rota de buscar os seguidores de um usuário, o search vai ser o username de um usuário. Já na rota de buscar as listas criadas de alguém, o search vai ser o nome da lista.

- **order**: Quando o valor de order for null, cada rota tem um valor padrão que irá assumir. Além disso, cada rota vai ter seu próprio conjunto de ordenações aceitáveis. Por exemplo, para ordenar uma rota que busca listas, tem 6 ordens possíveis: pelo nome da lista alfabeticamente, pela data de criação da lista, pela data de última atualização da lista e o inverso de cada uma dessas. Já para uma rota que busca quem o usuário bloqueou, há apenas 4 ordens possíveis: pelo username dos usuários bloqueados alfabeticamente, pela data em que esses bloqueios foram estabelecidos e o inverso dessas. Por padrão, as ordens estão todas em modo crescente, o que siginifica que alfabeticamente para strings e do mais antigo primeiro para rotas de data. Para alterar o modo, é só colocar um "-" na frente do order. Exemplo: `/lists/game/d70d80d?page_size=30&order=created_at` retorna os games de uma lista mostrando primeiro os games adicionados há mais tempo, e `/lists/game/d70d80d?page_size=30&order=-created_at` retorna os mesmos games daquela lista, porém enviando primeiro os games mais recém adicionados.


### Response body

O json de resposta de uma rota paginada vai seguir o seguinte padrão:

```json
__PAGE_RESULT__ = {
    "total": 0,
    "page_len": 0,
    "current_url": "string",
    "next_url": "string" | null, 
    "content": [
        __SCHEMA__
    ]
}
```

- **total**: Quantidade total de registros que correspondem com a busca. Ao passar por todas as páginas, terá se cobrido essa quantidade de registros.

- **page_len**: Quantidade de registros nessa página. Note que ele vai ser um valor **menor ou igual** ao page_size dos query parameters porque se a divisão entre o total de registros e o tamanho de página requisitado pelo frontend não for exata, claramente a última página vai ser um pouco menor.

- **current_url**: URL exata da busca que você fez para ter conseguido aquela página.

- **next_url**: URL exata da busca que você precisa fazer para conseguir a próxima página. O cursor e todos os outros query parameter que haviam sido enviados para a primeira página já estão embutidos nela.

- **content**: Uma lista dos registros buscados. Cada rota paginada vai ter seu próprio schema de dados que compõe a lista. Por exemplo, se a rota é para buscar listas, os elementos do content vão conter dados de lista, se a rota é para buscar seguidos pelo usuário, os elementos do content vão conter dados de usuário.

---

## Schemas padrão

Alguns schemas vão se repetir bastante ao longo da documentação, então fica aqui a definição deles:


- #### \_\_USER\_\_
  
```json
{
    "user_id": "string",        // Id único do usuário
    "username": "string",       // Username do usuário
    "pfp": "string" | null,     // Caminho para a foto de perfil, null se não houver
}
```
- #### \_\_USER_FULL\_\_
  
```json
{
    "user_id": "string",        // Id único do usuário
    "username": "string",       // Username do usuário
    "pfp": "string" | null,     // Caminho para a foto de perfil, null se não houver,
    "banner": "string" | null,  // Banner do perfil, null se não houver
    "bio": "string" | null,     // Bio do perfil, null se não houver
    "follower_count": 0,        // Quantas pessoas seguem o dono da conta
    "following_count": 0,       // Quantas pessoas o dono da conta segue
    "rel": 0,                   // Relacionamento entre o usuário visualizador e o dono da conta
    "created_at": "string",     // Data de criação da conta (padrão dd/mm/yyyy)

    // Listas de favoritos e completados (não muito privadas para o usuário visualizador)
    "lists": [ 
    {
        "list_id": "string",  // Id único da lista
        "name": "string",     // Nome da lista

        // Vai enviar até quatro games que pertencem a lista, só para preencher a tela do usuário
        "games": [ __GAME__ ],
    }
    ]
}
```

- #### \_\_LIST\_\_
  
```json
{
    "list_id": "string",                // Id único da lista
    "name": "string",                   // Nome da lista
    "creator": __USER__,                // Dados básicos do autor da lista
    "saves_count": 0,             // Quantos usuários salvaram a lista, contando o save automatico do autor
    "cover_picture": "string" | null,   // Url para a imagem de algum game que pertence a lista
    "rel": 0                            // Relacionamento entre o usuário visualizador e a lista
}
```
- #### \_\_LIST_FULL\_\_
  
```json
{
    "list_id": "string",                // Id único da lista
    "name": "string",                   // Nome da lista
    "description": "string" | null,     // Descrição textual da lista, null se não houver
    "privacy": 0,                       // Privacidade da lista
    "creator": __USER__,                // Dados básicos do autor da lista
    "saves_count": 0,                   // Quantos usuários salvaram a lista contando o save automatico do autor
    "games_count": 0,                   // Quantos games pertencem a lista
    "cover_picture": "string" | null,   // URL para uma imagem de jogo que pertence à lista, null se a lista for vazia
    "rel": 0,                           // Relacionamento do usuário visualizador com a lista
    "created_at": "string",             // Data de criação da lista (padrão dd/mm/yyyy)
    "updated_at": "string"              // Data da última atualização da lista (padrão dd/mm/yyyy)
}

```
- #### \_\_GAME\_\_
  
```json
{
    "game_id": 0,                        // Id único do game
    "title": "string",                   // Título do game
    "picture": "string" | null,          // URL para uma imagem do jogo, null se a API não nos informar
    "year": "string" | null,             // Ano de lançamento do jogo, null se a API não nos informar
}
```
- #### \_\_GAME_FULL\_\_
  
```json
{
    "game_id": 0,                     // Id único do game
    "title": "string",                // Título do game
    "picture": "string" | null,       // URL para uma imagem do jogo, null se a API não nos informar
    "year": "string" | null,          // Ano de lançamento do jogo, null se a API não nos informar
    "gamerboxd_rating": 0.0 | null,   // Rating considerando todas reviews sobre, ou null se não tiver reviews ainda
    "like_count": 0,                  // Quantas reviews marcaram liked = True
    "completed_count": 0,             // Quantas reviews marcaram completed = True
    "review_count": 0                 // Quantas reviews existem sobre o jogo, incluindo privadas
}
```
- #### \_\_REVIEW\_\_
  
```json
{
    "review_id": "string",            // Id único da review
    "reviewer": __USER__,             // Dados básicos do usuário avaliador
    "game": __GAME__,                 // Dados básicos do game avaliado
    "rating_num": 0.0,                // Avaliação numérica, entre 0 e 5, com incremento de 0.5
    "rating_text": "string" | null,   // Avaliação textual, null se não houver   
    "liked": true,                    // Se o autor curtiu ou não o game
    "privacy": 0,                     // Privacidade da review
    "like_count": 0,                  // Quantos likes a review tem (conta o like do próprio autor, se ele tiver curtido)
    "created_at": "string",           // Data de criação da review (padrão dd/mm/yyyy)
    "rel": 0                          // Relacionamento entre o usuário visualizador e a review
}
```
- #### \_\_REVIEW_FULL\_\_
  
```json
{
    "review_id": "string",           // Id único da review
    "reviewer": __USER__,            // Dados básicos do usuário avaliador
    "game": __GAME__,                // Dados básicos do game avaliado
    "rating_num": 0.0,               // Avaliação numérica, entre 0 e 5, com incremento de 0.5
    "rating_text": "string" | null,  // Avaliação textual, null se não houver   
    "time_played": 0 | null,         // Tempo jogado em horas   
    "privacy": 0,                    // Privacidade da review
    "liked": true,                   // Se o autor curtiu ou não o game
    "completed": true,               // Se o autor completou ou não o game
    "like_count": 0,                 // Quantos likes a review recebeu (conta o like do próprio autor, se ele tiver curtido)
    "tag_count": 0,                  // Não implementado ainda!
    "tags": ["string"],              // Não implementado ainda!
    "created_at": "string",          // Data de criação da review (padrão dd/mm/yyyy)
    "updated_at": "string",          // Data da última atualização da review (padrão dd/mm/yyyy)
    "rel": 0                         // Relacionamento entre o usuário visualizador e a review
}
```

--- 

## Privacies e rels dos schemas

Os níveis de privacidade para uma **lista** ou para uma **review** são:

| Nível      | Valor  | Definição                                                                           |
|------------|--------|-------------------------------------------------------------------------------------|
| `ANY`      |  0     | Qualquer usuário (ressalvas para questões de bloqueio) pode ver a lista ou a review |
| `FOLLOWED` |  20    | Qualquer usuário seguido pelo autor pode ver a lista ou a review                    |
| `OWNER`    |  40    | Apenas o autor pode ver a lista ou a review                                         |

Os rels possíveis para um **usuário** são:

| Nível           | Valor  | Definição                                       |
|-----------------|--------|-------------------------------------------------|
| `ANY`           |  0     | O usuário não tem relação com o usuário buscado |
| `FOLLOWER`      |  10    | O usuário segue o usuário buscado               |
| `FOLLOWED`      |  20    | O usuário é seguido pelo usuário buscado        |
| `MUTUAL_FOLLOW` |  30    | O usuário é seguido e segue o usuário buscado   |
| `OWNER`         |  40    | O usuário é o próprio usuário buscado           |

Os rels possíveis para uma **lista** são:

| Nível     | Valor  | Definição                                  |
|-----------|--------|--------------------------------------------|
| `ANY`     |  0     | O usuário não salvou e não é dono da lista |
| `OWNER`   |  40    | O usuário é o autor da lista               |
| `SAVED`   |  50    | O usuário salvou a lista                   |

Similarmente, os rels possíveis para uma **review** são:

| Nível          | Valor  | Definição                                          |
|----------------|--------|----------------------------------------------------|
| `ANY`          |  0     | O usuário não deu like e não é autor da review     |
| `OWNER`        |  40    | O usuário é o autor da review                      |
| `LIKED`        |  50    | O usuário já deu like na review                    |
| `OWNER_LIKED`  |  90    | O usuário é o autor da review e deu like na review |


**Para todas as rotas que não requerem login, se um usuário não estiver logado, ele é considerado como `ANY`.**

---

## Cookies de autenticação

Os dois cookies de autenticação sobre os quais o backend opera são:

| Cookie          | Descrição                         | SameSite   | Secure | HttpOnly | 
|-----------------|-----------------------------------|------------|--------|----------|
| `access-token`  | JWT de curta duração (10 minutos) | `'strict'` | `True` |  `True`  |
| `refresh-token` | JWT de longa duração (12 horas)   | `'strict'` | `True` |  `True`  |

Sempre incluam esses cookies para qualquer chamada ao backend, até nas que não precisam de login!

Enquanto o refresh-token está válido, o access-token é automaticamente renovado. Após as 12h, o usuário terá que fazer login de novo.

---

## Erros

Todo erro descrito como `erros possíveis` ao longo das documentações das rotas voltará seguindo o seguinte schema:

```json
{"message": "string"}
```

O HR (human readable) denota se a mensagem de erro pode ser mostrada ao usuário para explicar o problema que ocorreu. Caso não, é melhor mostrar uma tela padrão de erro.