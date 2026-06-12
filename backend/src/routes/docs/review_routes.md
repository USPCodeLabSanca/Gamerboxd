# 📡 Documentação das Rotas de Reviews

## Sumário

- [POST `/review/`](#post-review---criar-review)
- [PUT `/review/{old_review_game}`](#put-reviewold_review_game---editar-review)
- [DELETE `/review/{review_game}`](#delete-reviewreview_game---deletar-review)
- [GET `/review/{username}`](#get-reviewusername---listar-reviews-de-um-usuário)
- [GET `/review/{username}/{game}`](#get-reviewusernamegame---ver-review-de-um-usuário)
- [POST `/review/like/{username}/{game}`](#post-reviewlikeusernamegame---dar-like-em-review)
- [POST `/review/unlike/{username}/{game}`](#post-reviewunlikeusernamegame---remover-like-de-review)

---

## POST `/review/` — Criar review

Cria uma review para um jogo. Cada usuário pode ter apenas uma review por jogo. **Requer login**.

### Request Body

```json
{
  "game": 0,
  "rating_num": 0.0,
  "rating_text": "string",
  "is_private": true,
  "time_played": 0.0,
  "liked": true,
  "completed": true
}
```

| Campo         | Tipo    | Obrigatório | Regras                                         |
|---------------|---------|-------------|------------------------------------------------|
| `game`        | int     | ✅          | ID do jogo a ser avaliado                      |
| `rating_num`  | float   | ✅          | Nota numérica da avaliação                     |
| `rating_text` | string  | ✅          | Texto da review, máximo de 1000 caracteres     |
| `is_private`  | boolean | ✅          | Se `true`, a review só é visível ao criador    |
| `time_played` | float   | ✅          | Tempo jogado                                   |
| `liked`       | boolean | ✅          | Se o usuário gostou do jogo                    |
| `completed`   | boolean | ✅          | Se o usuário completou o jogo                  |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                                                    |
|--------|--------------------------------------------------------------------------|
| `400`  | Usuário já possui uma review desse jogo, texto acima de 1000 caracteres  |
| `401`  | Usuário não autenticado                                                  |
| `500`  | Erro interno ao salvar no banco                                          |

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
  "rating_text": "string",
  "is_private": true,
  "time_played": 0.0,
  "liked": true,
  "completed": true,
  "last_update": "string"
}
```

### Erros possíveis

| Status | Causa                                                                              |
|--------|------------------------------------------------------------------------------------|
| `400`  | Tentativa de alterar o jogo da review, review não encontrada, texto acima de 1000 caracteres |
| `401`  | Usuário não autenticado                                                            |
| `500`  | Erro interno ao atualizar no banco                                                 |

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

| Parâmetro | Tipo | Obrigatório | Padrão | Descrição                                      |
|-----------|------|-------------|--------|------------------------------------------------|
| `limit`   | int  | ❌          | `10`   | Quantidade de reviews retornadas (máximo: `20`) |

### Resposta de Sucesso — `200`

Retorna um array de reviews:

```json
[
  {
    "rating_num": 0.0,
    "rating_text": "string",
    "likes_count": 0,
    "liked": true,
    "game_name": "string",
    "created_at": "string"
  }
]
```

### Erros possíveis

| Status | Causa                                          |
|--------|------------------------------------------------|
| `400`  | `limit` acima de 20                            |
| `500`  | Reviews não encontradas ou erro interno        |

---

## GET `/review/{username}/{game}` — Ver review de um usuário

Retorna os detalhes completos da review pública de um usuário para um jogo específico. **Não requer login**.

### Path Parameters

| Parâmetro  | Tipo   | Descrição                        |
|------------|--------|----------------------------------|
| `username` | string | Username do autor da review      |
| `game`     | int    | ID do jogo da review             |

### Resposta de Sucesso — `200`

```json
{
  "username": "string",
  "rating_num": 0.0,
  "rating_text": "string",
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

| Status | Causa                                                  |
|--------|--------------------------------------------------------|
| `500`  | Review não encontrada, privada, jogo não existe, ou erro interno |

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

| Status | Causa                                        |
|--------|----------------------------------------------|
| `400`  | Usuário já deu like nessa review             |
| `401`  | Usuário não autenticado                      |
| `500`  | Review não encontrada ou erro interno        |

---

## POST `/review/unlike/{username}/{game}` — Remover like de review

Remove o like do usuário autenticado de uma review. **Requer login**.

### Path Parameters

| Parâmetro  | Tipo   | Descrição                                       |
|------------|--------|-------------------------------------------------|
| `username` | string | Username do autor da review                     |
| `game`     | int    | ID do jogo da review a ter o like removido      |

### Resposta de Sucesso — `202`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                        |
|--------|----------------------------------------------|
| `400`  | Usuário não havia dado like nessa review     |
| `401`  | Usuário não autenticado                      |
| `500`  | Review não encontrada ou erro interno        |

---

## 🔐 Autenticação

As rotas que requerem login dependem do cookie `access-token` enviado automaticamente pelo browser. Certifique-se de que as requisições são feitas com `credentials: 'include'` (fetch) ou `withCredentials: true` (axios).

```js
// Exemplo com fetch
fetch('/review/', {
  credentials: 'include'
})

// Exemplo com axios
axios.post('/review/', body, { withCredentials: true })
```

---