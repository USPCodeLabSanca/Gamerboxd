# 📡 Documentação das Rotas de Reviews


## Sumário

- [POST `/review/`](#post-review---criar-review)
- [PUT `/review/{old_review_game}`](#put-reviewold_review_game---editar-review)
- [DELETE `/review/{review_game}`](#delete-reviewreview_game---deletar-review)
- [GET `/review/{username}`](#get-reviewusername---listar-reviews-de-um-usuário)
- [GET `/review/{username}/{game}`](#get-reviewusernamegame---ver-review-de-um-usuário)
- [POST `/review/like/{username}/{game}`](#post-reviewlikeusernamegame---dar-like-em-review)
- [DELETE `/review/like/{username}/{game}`](#delete-reviewlikeusernamegame---remover-like-de-review)

---

## POST `/review/` — Criar review

Cria uma review para um jogo. Cada usuário pode ter apenas uma review por jogo. **Requer login**.

### Request Body

```json
{
  "game": 0,
  "rating_num": 0.0,
  "rating_text": "string | null",
  "is_private": true,
  "time_played": 0.0,
  "liked": true,
  "completed": true
}
```

| Campo         | Tipo            | Obrigatório | Padrão  | Descrição/Regras                               |
|---------------|-----------------|-------------|---------|------------------------------------------------|
| `game`        | int             | ✅          | -       | ID do jogo a ser avaliado                      |
| `rating_num`  | float           | ✅          | -       | Nota numérica da avaliação                     |
| `rating_text` | string ou null  | ❌          | null    | Texto da review, máximo de 1000 caracteres     |
| `is_private`  | boolean         | ✅          | -       | Se `true`, a review só é visível ao criador    |
| `time_played` | float           | ✅          | -       | Tempo jogado                                   |
| `liked`       | boolean         | ✅          | -       | Se o usuário gostou do jogo                    |
| `completed`   | boolean         | ✅          | -       | Se o usuário completou o jogo                  |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                    |
|--------|------------------------------------------|
| `400`  | Texto acima de 1000 caracteres           |
| `401`  | Usuário não autenticado                  |
| `409`  | Usuário já possui uma review desse jogo  |
| `500`  | Erro interno ao salvar no banco          |

---

## PUT `/review/{old_review_game}` — Editar review

Atualiza a review do usuário autenticado para um jogo. O campo `game` não pode ser alterado. **Requer login**.

### Path Parameter

| Parâmetro         | Tipo | Descrição                                  |
|-------------------|------|--------------------------------------------|
| `old_review_game` | int  | ID do jogo cuja review será atualizada     |

### Request Body

Mesmo formato do [POST `/review/`](#post-review---criar-review). O campo `game` deve ser idêntico ao `old_review_game` do path.

### Resposta de Sucesso — `200`

```json
{
  "game": 0,
  "rating_num": 0.0,
  "rating_text": "string | null",
  "is_private": true,
  "time_played": 0.0,
  "liked": true,
  "completed": true,
  "last_update": "string"
}
```

### Erros possíveis

| Status | Causa                                                                 |
|--------|-----------------------------------------------------------------------|
| `400`  | Tentativa de alterar o jogo da review, texto acima de 1000 caracteres |
| `401`  | Usuário não autenticado                                               |
| `404`  | Review a ser alterada não encontrada                                  |
| `500`  | Erro interno ao atualizar no banco                                    |

---

## DELETE `/review/{review_game}` — Deletar review

Remove a review do usuário autenticado para um jogo. **Requer login**.

### Path Parameter

| Parâmetro     | Tipo | Descrição                              |
|---------------|------|----------------------------------------|
| `review_game` | int  | ID do jogo cuja review será deletada   |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                              |
|--------|------------------------------------|
| `401`  | Usuário não autenticado            |
| `500`  | Erro interno ao deletar no banco   |

---

## GET `/review/{username}` — Listar reviews de um usuário

Retorna uma lista das reviews públicas mais recentes de um usuário. **Não requer login**.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                        |
|------------|--------|----------------------------------|
| `username` | string | Username do autor das reviews    |

### Query Parameters

| Parâmetro | Tipo | Obrigatório | Padrão | Descrição                                       |
|-----------|------|-------------|--------|-------------------------------------------------|
| `limit`   | int  | ❌          | `10`   | Quantidade de reviews retornadas (máximo: `20`) |

### Resposta de Sucesso — `200`

Retorna um array de reviews:

```json
[
  {
    "rating_num": 0.0,
    "rating_text": "string | null",
    "likes_count": 0,
    "liked": true,
    "game_name": "string",
    "created_at": "string"
  }
]
```

### Erros possíveis

| Status | Causa                                                                     |
|--------|---------------------------------------------------------------------------|
| `400`  | `limit` acima de 20                                                       |
| `403`  | Ususário está tentando ver as reviews escritas por alguém que o bloqueou  |
| `404`  | Usuário alvo não encontrado                                               |  
| `500`  | Erro interno ao buscar dados no banco                                     |

---

## GET `/review/{username}/{game}` — Ver review de um usuário

Retorna os detalhes completos da review pública de um usuário para um jogo específico. **Não requer login**.

### Path Parameters

| Parâmetro  | Tipo   | Descrição                   |
|------------|--------|-----------------------------|
| `username` | string | Username do autor da review |
| `game`     | int    | ID do jogo da review        |

### Resposta de Sucesso — `200`

```json
{
  "username": "string",
  "rating_num": 0.0,
  "rating_text": "string | null",
  "time_played": 0.0,
  "completed": true,
  "tag_count": 0,
  "tags": ["string"],
  "likes_count": 0,
  "liked": true,
  "game_name": "string",
  "created_at": "string",
  "last_update": "string"
}
```

### Erros possíveis

| Status | Causa                                  |
|--------|----------------------------------------|
| `404`  | Review não encontrada ou privada       |
| `500`  | Erro interno ao buscar dados no banco  |

---

## POST `/review/like/{username}/{game}` — Dar like em review

Dá like na review pública de outro usuário para um jogo. **Requer login**.

### Path Parameters

| Parâmetro  | Tipo   | Descrição                           |
|------------|--------|-------------------------------------|
| `username` | string | Username do autor da review         |
| `game`     | int    | ID do jogo da review a ser curtida  |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                                                           |
|--------|---------------------------------------------------------------------------------|
| `401`  | Usuário não autenticado                                                         |
| `403`  | Usuário está tentando dar like em uma review escrita por alguém que o bloqueou  |
| `404`  | Review não encontrada ou privada, usuário alvo não encontrado                   |
| `409`  | Usuário já deu like nessa review                                                |
| `500`  | Erro interno ao adicionar dados no banco                                        |

---

## DELETE `/review/like/{username}/{game}` — Remover like de review

Remove o like do usuário autenticado de uma review. **Requer login**.

### Path Parameters

| Parâmetro  | Tipo   | Descrição                                   |
|------------|--------|---------------------------------------------|
| `username` | string | Username do autor da review                 |
| `game`     | int    | ID do jogo da review a ter o like removido  |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                    |
|--------|------------------------------------------|
| `401`  | Usuário não autenticado                  |
| `404`  | Review não encontrada ou privada         |
| `409`  | Usuário não havia dado like nessa review |
| `500`  | Erro interno ao remover dados no banco   |
