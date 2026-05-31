# 📡 Documentação das Rotas de Listas


## Sumário

- [POST `/list/`](#post-list---criar-lista)
- [GET `/list/{list_name}`](#get-listlist_name---ver-minha-lista)
- [GET `/list/{list_creator}/{list_name}`](#get-listlist_creatorlist_name---ver-lista-de-outro-usuário)
- [PUT `/list/{old_list_name}`](#put-listold_list_name---editar-lista)
- [DELETE `/list/{list_name}`](#delete-listlist_name---deletar-lista)
- [POST `/list/save/{list_creator}/{list_name}`](#post-listsavelist_creatorlist_name---salvar-lista)
- [POST `/list/unsave/{list_creator}/{list_name}`](#post-listunsavelist_creatorlist_name---remover-lista-salva)
- [POST `/list/add/{list_name}/{game_id}`](#post-listaddlist_namegame_id---adicionar-jogo-à-lista)
- [POST `/list/rem/{list_name}/{game_id}`](#post-listremlist_namegame_id---remover-jogo-da-lista)

---

## POST `/list/` — Criar lista

Cria uma nova lista para o usuário autenticado. Ao ser criada, a lista é automaticamente salva para o criador. **Requer login**.

### Request Body

```json
{
  "name": "string",
  "description": "string",
  "is_private": true
}
```

| Campo         | Tipo    | Obrigatório | Regras                                        |
|---------------|---------|-------------|-----------------------------------------------|
| `name`        | string  | ✅           | Máximo de 60 caracteres, único por usuário    |
| `description` | string  | ✅           | Máximo de 300 caracteres                      |
| `is_private`  | boolean | ✅           | Se `true`, a lista só é visível ao criador    |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                                        |
|--------|--------------------------------------------------------------|
| `400`  | Usuário já possui uma lista com esse nome, nome ou descrição acima do limite de caracteres |
| `401`  | Usuário não autenticado                                      |
| `500`  | Erro interno ao salvar no banco                              |

---

## GET `/list/{list_name}` — Ver minha lista

Retorna os dados completos de uma lista feita pelo usuário autenticado. **Requer login**.

### Path Parameter

| Parâmetro   | Tipo   | Descrição                      |
|-------------|--------|--------------------------------|
| `list_name` | string | Nome da lista a ser buscada    |

### Resposta de Sucesso — `200`

```json
{
  "name": "string",
  "description": "string",
  "is_private": true,
  "creator": "string",
  "created_at": "string",
  "list_saves": 0,
  "games": [
    {
      "game_id": 0,
      "name": "string",
      "picture": "string | null",
      "year": 0
    }
  ]
}
```

### Erros possíveis

| Status | Causa                              |
|--------|------------------------------------|
| `400`  | Lista não encontrada               |
| `401`  | Usuário não autenticado            |
| `500`  | Erro interno ao buscar os dados    |

---

## GET `/list/{list_creator}/{list_name}` — Ver lista de outro usuário

Retorna os dados completos de uma lista pública de qualquer usuário. **Não requer login**.

### Path Parameters

| Parâmetro      | Tipo   | Descrição                        |
|----------------|--------|----------------------------------|
| `list_creator` | string | Username do dono da lista        |
| `list_name`    | string | Nome da lista a ser buscada      |

### Resposta de Sucesso — `200`

Mesmo formato do [GET `/list/{list_name}`](#get-listlist_name---ver-minha-lista).

### Erros possíveis

| Status | Causa                                                      |
|--------|------------------------------------------------------------|
| `400`  | Usuário não encontrado, lista não encontrada ou privada    |
| `500`  | Erro interno ao buscar os dados                            |

---

## PUT `/list/{old_list_name}` — Editar lista

Atualiza os dados de uma lista do usuário autenticado. **Requer login**.

### Path Parameter

| Parâmetro       | Tipo   | Descrição                        |
|-----------------|--------|----------------------------------|
| `old_list_name` | string | Nome atual da lista a ser editada |

### Request Body

Mesmo formato do [POST `/list/`](#post-list---criar-lista).

### Resposta de Sucesso — `200`

Retorna os dados completos da lista atualizada:

```json
{
  "name": "string",
  "description": "string",
  "is_private": true,
  "creator": "string",
  "created_at": "string",
  "list_saves": 0
}
```

### Erros possíveis

| Status | Causa                                                        |
|--------|--------------------------------------------------------------|
| `400`  | Novo nome já está em uso, nome ou descrição acima do limite  |
| `401`  | Usuário não autenticado                                      |
| `500`  | Erro interno ao atualizar no banco                           |

---

## DELETE `/list/{list_name}` — Deletar lista

Remove uma lista do usuário autenticado. **Requer login**.

### Path Parameter

| Parâmetro   | Tipo   | Descrição                      |
|-------------|--------|--------------------------------|
| `list_name` | string | Nome da lista a ser deletada   |

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

## POST `/list/save/{list_creator}/{list_name}` — Salvar lista

Salva a lista pública de outro usuário na biblioteca do autenticado. **Requer login**.

### Path Parameters

| Parâmetro      | Tipo   | Descrição                      |
|----------------|--------|--------------------------------|
| `list_creator` | string | Username do dono da lista      |
| `list_name`    | string | Nome da lista a ser salva      |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                                   |
|--------|---------------------------------------------------------|
| `400`  | Usuário não encontrado, lista não encontrada ou privada |
| `401`  | Usuário não autenticado                                 |
| `500`  | Erro interno ao salvar                                  |

---

## POST `/list/unsave/{list_creator}/{list_name}` — Remover lista salva

Remove uma lista previamente salva da biblioteca do usuário autenticado. **Requer login**.

### Path Parameters

| Parâmetro      | Tipo   | Descrição                            |
|----------------|--------|--------------------------------------|
| `list_creator` | string | Username do dono da lista            |
| `list_name`    | string | Nome da lista a ser removida         |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                                   |
|--------|---------------------------------------------------------|
| `400`  | Usuário não encontrado, lista não encontrada ou privada |
| `401`  | Usuário não autenticado                                 |
| `500`  | Erro interno ao remover                                 |

---

## POST `/list/add/{list_name}/{game_id}` — Adicionar jogo à lista

Adiciona um jogo a uma lista do usuário autenticado. **Requer login**.

### Path Parameters

| Parâmetro   | Tipo   | Descrição                                  |
|-------------|--------|--------------------------------------------|
| `list_name` | string | Nome da lista que receberá o jogo          |
| `game_id`   | int    | ID do jogo a ser adicionado                |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                              |
|--------|------------------------------------|
| `400`  | Lista não encontrada               |
| `401`  | Usuário não autenticado            |
| `500`  | Erro interno ao adicionar o jogo   |

---

## POST `/list/rem/{list_name}/{game_id}` — Remover jogo da lista

Remove um jogo de uma lista do usuário autenticado. **Requer login**.

### Path Parameters

| Parâmetro   | Tipo   | Descrição                                  |
|-------------|--------|--------------------------------------------|
| `list_name` | string | Nome da lista da qual o jogo será removido |
| `game_id`   | int    | ID do jogo a ser removido                  |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                              |
|--------|------------------------------------|
| `400`  | Lista não encontrada               |
| `401`  | Usuário não autenticado            |
| `500`  | Erro interno ao remover o jogo     |

---

## 🔐 Autenticação

As rotas que requerem login dependem do cookie `access-token` enviado automaticamente pelo browser. Certifique-se de que as requisições são feitas com `credentials: 'include'` (fetch) ou `withCredentials: true` (axios).

```js
// Exemplo com fetch
fetch('/list/', {
  credentials: 'include'
})

// Exemplo com axios
axios.post('/list/', body, { withCredentials: true })
```

---