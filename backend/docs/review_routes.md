# 📡 Documentação das Rotas de Reviews


## Sumário
- [POST `/reviews` — Criar review](#post-reviews--criar-review)
- [GET `/reviews/{review_id}` — Ver em detalhe a review de um usuário](#get-reviewsreview_id--ver-em-detalhe-a-review-de-um-usuário)
- [GET `/reviews/created/{user_id}` — Listar reviews de um usuário](#get-reviewscreateduser_id--listar-reviews-de-um-usuário)
- [PUT `/reviews/{review_id}` — Editar review](#put-reviewsreview_id--editar-review)
- [DELETE `/reviews/{review_id}` — Deletar review](#delete-reviewsreview_id--deletar-review)
- [POST `/reviews/like/{review_id}` — Dar like em review](#post-reviewslikereview_id--dar-like-em-review)
- [DELETE `/reviews/like/{review_id}` — Remover like de review](#delete-reviewslikereview_id--remover-like-de-review)
- [GET `/reviews/like/users/{review_id}` — Ver quem deu like na review](#get-reviewslikeusersreview_id--ver-quem-deu-like-na-review)
- [GET `/reviews/like/reviews` — Ver as reviews para as quais um usuário deu like](#get-reviewslikereviews--ver-as-reviews-para-as-quais-um-usuário-deu-like)
---

## POST `/reviews` — Criar review

Cria uma review para um jogo.

**Regras e comportamentos:**
- **Requer login**.
- Cada usuário pode ter apenas uma review para cada jogo.
- Se o usuário marcou que gostou do game (`liked = true`), o game vai ser automaticamente inserido na lista de **Jogos Favoritos** dele.
- Se o usuário marcou que completou o game (`completed = true`), o game vai ser automaticamente inserido na lista de **Jogos Completados** dele.

### Request Body

```json
{
  "game_id": 0,
  "rating_num": 0.0,
  "rating_text": "string" | null,
  "privacy": 0,
  "time_played": 0 | null, 
  "liked": true,
  "completed": true
}
```

| Campo         | Tipo            | Obrigatório | Padrão  | Descrição/Regras                               |
|---------------|-----------------|-------------|---------|------------------------------------------------|
| `game_id`     | int             | ✅          | -       | ID do jogo a ser avaliado                      |
| `rating_num`  | float           | ✅          | -       | Nota numérica da avaliação. Entre 0 e 5, múltiplo de 0.5 |
| `rating_text` | string, null    | ❌          | null    | Texto da review, máximo de 300 caracteres      |
| `privacy`     | int             | ✅          | -       | Deve ser um dos valores dispostos na seção de privacidade |
| `time_played` | int, null       | ❌          | null    | Tempo jogado em horas                          |
| `liked`       | bool            | ✅          | -       | Se o usuário gostou do jogo                    |
| `completed`   | bool            | ✅          | -       | Se o usuário completou o jogo                  |

### Resposta de Sucesso — `200`

```json
{"message":"Review criada com sucesso!", "review_id": "string"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR (human readable)    | Causa                                      |
|--------|------------------------|--------------------------------------------|
| `400`  | ✅                     | Texto acima de 300 caracteres              |
| `401`  | ✅                     | Usuário não autenticado                    |
| `404`  | ✅                     | Game não encontrado (game_id inválido)     |
| `409`  | ✅                     | Usuário já possui uma review desse jogo    |
| `422`  | ❌                     | Campo(s) do request body ausentes ou inválidos  |
| `500`  | ❌                     | Erro interno                               |

---


## GET `/reviews/{review_id}` — Ver em detalhe a review de um usuário

Retorna os detalhes completos de uma review. 

**Regras e comportamentos:**
- **Não requer login**.


### Path Parameters

| Parâmetro    | Tipo   | Descrição                   |
|--------------|--------|-----------------------------|
| `review_id`  | string | ID único da review buscada  |

### Resposta de Sucesso — `200`

Retorna schema [**\_\_REVIEW_FULL\_\_**](./routes.md#__review_full__)

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                                                      |
|--------|--------|------------------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou o autor da review que ele está buscando   |
| `403`  | ❌     | A review é "privada demais" para o usuário                 |
| `404`  | ✅     | Review não encontrada                                      |
| `433`  | ❌     | Usuário está bloqueado pelo autor da review                |
| `500`  | ❌     | Erro interno                                               |

---

## GET `/reviews/created/{user_id}` — Listar reviews de um usuário

Busca de forma paginada uma lista das reviews do usuário.

**Regras e comportamentos:**
- **Não requer login**.
- As reviews que são muito privadas para o usuário que está buscando não serão enviadas no content, e nem contarão para o total.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                        |
|------------|--------|----------------------------------|
| `user_id`  | string | ID único do autor das reviews    |

### Query Parameters ([Paginação](./routes.md#rotas-paginadas))

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis titulos dos games que o usuário deve ter avaliado.
- order padrão é `-created_at`, que mostra as mais recém criadas reviews. Os orders possíveis são: `["created_at", "-created_at", "title", "-title", "updated_at", "-updated_at"]`.

### Resposta de Sucesso — `200`

Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas [**\_\_REVIEW\_\_**](./routes.md#__review__). 

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                                                      |
|--------|--------|------------------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou o autor das reviews que ele está buscando |
| `404`  | ✅     | Usuário autor das reviews não encontrado                   |
| `422`  | ❌     | Query parameters inválidos                                 |
| `433`  | ❌     | Usuário está bloqueado pelo autor das reviews              |
| `500`  | ❌     | Erro interno                                               |

---

## PUT `/reviews/{review_id}` — Editar review

Atualiza a review do usuário autenticado para um jogo.

**Regras e comportamentos:**
- **Requer login**.
- Se o parâmetro `liked` ou `completed` mudar em relação à review original, o game será incluído ou removido das listas **Jogos Favoritos** ou **Jogos Completados** para refletir essa mudança.
- Se a privacidade da review subir, todos os usuários que deram like na review e estiverem abaixo dessa nova privacidade terão a review removida do seu histórico de likes.
- Até os campos inalterados precisam ser enviados.

### Path Parameter

| Parâmetro   | Tipo    | Descrição                            |
|-------------|---------|--------------------------------------|
| `review_id` | string  | ID único da review a ser editada     |

### Request Body

```json
{
  "rating_num": 0.0,
  "rating_text": "string" | null,
  "privacy": 0,
  "time_played": 0 | null, 
  "liked": true,
  "completed": true
}
```

| Campo         | Tipo               | Obrigatório | Descrição/Regras                               |
|---------------|--------------------|-------------|------------------------------------------------|
| `rating_num`  | float              | ✅          | Nota numérica da avaliação. Entre 0 e 5, múltiplo de 0.5 | 
| `rating_text` | string, null       | ✅          | Texto da review, máximo de 300 caracteres      |
| `privacy`     | int                | ✅          | Deve ser um dos valores dispostos na seção de privacidade |
| `time_played` | int, null          | ✅          | Tempo jogado em horas                          |
| `liked`       | bool               | ✅          | Se o usuário gostou do jogo                    |
| `completed`   | bool               | ✅          | Se o usuário completou o jogo                  |

### Resposta de Sucesso — `200`

Retorna schema [**\_\_REVIEW\_\_**](./routes.md#__review_full__)

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                                          |
|--------|--------|------------------------------------------------|
| `400`  | ✅     | Texto acima de 280 caracteres                  |
| `401`  | ✅     | Usuário não autenticado                        |
| `403`  | ❌     | Falta de propriedade da review                 |
| `404`  | ✅     | Review não encontrada                          |
| `422`  | ❌     | Campo(s) do request body ausentes ou inválidos |
| `500`  | ❌     | Erro interno                                   |

---

## DELETE `/reviews/{review_id}` — Deletar review

Deleta a review do usuário autenticado para um jogo.

**Regras e comportamentos:**
- **Requer login**.
- Caso o usuário tivesse marcado que gostou ou completou na review original, o game será removido das listas **Jogos Favoritos** ou **Jogos Completados**, respectivamente. 
- Os likes da review serão deletados também.


### Path Parameter

| Parâmetro     | Tipo    | Descrição                              |
|---------------|---------|----------------------------------------|
| `review_id`   | string  | ID único da review que será deletada   |

### Resposta de Sucesso — `200`

```json
{"message":"Review deletada com sucesso!"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                          |
|--------|--------|--------------------------------|
| `401`  | ✅     | Usuário não autenticado        |
| `403`  | ❌     | Falta de propriedade da review |
| `404`  | ✅     | Review não encontrada          |
| `500`  | ❌     | Erro interno                   |

---

## POST `/reviews/like/{review_id}` — Dar like em review

Dá like na review de um usuário.

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado já tiver dado like na review, a rota não irá incluir novamente no DB, mas também não irá levantar erro (idempotência).
- É possível dar like na sua própria review.

### Path Parameters

| Parâmetro    | Tipo   | Descrição                           |
|--------------|--------|-------------------------------------|
| `review_id`  | string | ID único da review a ser curtida    |

### Resposta de Sucesso — `200`

```json
{"message": "Like adicionado com sucesso!"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                                                      |
|--------|--------|------------------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou o autor da review que ele está curtindo   |
| `401`  | ✅     | Usuário não autenticado                                    |
| `403`  | ❌     | A review é "privada demais" para o usuário                 |
| `404`  | ✅     | Review não encontrada                                      |
| `433`  | ❌     | Usuário está bloqueado pelo autor da review                |
| `500`  | ❌     | Erro interno                                               |

---

## DELETE `/reviews/like/{review_id}` — Remover like de review

Remove o like do usuário autenticado de uma review.

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado não tiver dado like na review, a rota não irá levantar erro (idempotência).

### Path Parameters

| Parâmetro    | Tipo   | Descrição                           |
|--------------|--------|-------------------------------------|
| `review_id`  | string | ID único da review a ser descurtida |

### Resposta de Sucesso — `200`

```json
{"message": "Like removido com sucesso!"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                     |
|--------|--------|---------------------------|
| `401`  | ✅     | Usuário não autenticado   |
| `404`  | ✅     | Review não encontrada     |
| `500`  | ❌     | Erro interno              |

---

## GET `/reviews/like/users/{review_id}` — Ver quem deu like na review

Busca de forma paginada os usuários que deram like em uma review específica.

**Regras e comportamentos:**
- **Não requer login**.

### Path Parameters

| Parâmetro    | Tipo   | Descrição                                        |
|--------------|--------|--------------------------------------------------|
| `review_id`  | string | ID único da review que está vendo quem curtiu    |

### Query Parameters ([Paginação](./routes.md#rotas-paginadas))

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis usernames de usuários que deram like na review.
- order padrão é `-created_at`, que mostra os usuários que deram like mais recentemente. Os orders possíveis são: `["created_at", "-created_at", "username", "-username"]`.

### Resposta de Sucesso — `200`

Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas **\_\_USER\_\_**.

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                                                                  |
|--------|--------|------------------------------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou o autor da review que ele está tentando ver os likes  |
| `403`  | ❌     | A review é "privada demais" para o usuário                             |
| `404`  | ✅     | Review não encontrada                                                  |
| `422`  | ❌     | Query parameters inválidos                                             |
| `433`  | ❌     | Usuário está bloqueado pelo autor da review                            |
| `500`  | ❌     | Erro interno                                                           |

---

## GET `/reviews/like/reviews` — Ver as reviews para as quais um usuário deu like

Busca de forma paginada as reviews para qual o usuário autenticado deu like.

**Regras e comportamentos:**
- **Requer login**.

### Query Parameters ([Paginação](./routes.md#rotas-paginadas))

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis titulos dos games que o usuário deve ter avaliado.
- order padrão é `-created_at`, que mostra as mais recém curtidas reviews do usuário. Os orders possíveis são: `["created_at", "-created_at", "title", "-title", "updated_at", "-updated_at"]`.


### Resposta de Sucesso — `200`

Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas [**\_\_REVIEW\_\_**](./routes.md#__review__).


### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                      |
|--------|--------|----------------------------|
| `401`  | ✅     | Usuário não autenticado    |
| `422`  | ❌     | Query parameters inválidos |
| `500`  | ❌     | Erro interno               |