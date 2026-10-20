# 📡 Documentação das Rotas de Usuário

 
## Sumário
 
- [POST `/user`](#post-user---criar-conta)
- [GET `/user/`](#get-user---ver-minha-conta)
- [PUT `/user`](#put-user---editar-conta)
- [GET `/user/{user_id}`](#get-useruser_id---ver-conta-de-outro-usuário)
- [POST `/user/follow/{user_id}`](#post-userfollowuser_id---seguir-usuário)
- [DELETE `/user/follow/{user_id}`](#delete-userfollowuser_id---deixar-de-seguir-usuário)
- [GET `/user/follow/followers`](#get-userfollowfollowers---ver-os-seguidores-do-usuário)
- [GET `/user/follow/followeds`](#get-userfollowfolloweds---ver-os-seguidos-do-usuário)
- [DELETE `/user/`](#delete-user---deletar-conta)
- [POST `/user/block/{user_id}`](#post-userblockuser_id---bloquear-usuário)
- [DELETE `/user/block/{user_id}`](#delete-userblockuser_id---desbloquear-usuário)
- [GET `/user/block`](#get-userblock---ver-os-bloqueados-pelo-usuário)

---
 
## POST `/user` — Criar conta
 
Cria uma nova conta de usuário. Ao criar a conta, duas listas padrão são geradas automaticamente: **Favoritos** e **Completados**.
 
### Request Body
 
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
 
| Campo      | Tipo   | Obrigatório | Regras                                                                                 |
|------------|--------|-------------|----------------------------------------------------------------------------------------|
| `username` | string | ✅          | Entre 4 e 24 caractéres, não pode estar em uso                                         |
| `email`    | string | ✅          | Formato de e-mail válido, não pode estar em uso                                        |
| `password` | string | ✅          | Entre 8 e 64 caracteres, com ao menos: 1 maiúscula, 1 minúscula, 1 número e 1 símbolo  |

### Resposta de Sucesso — `200`
 
```json
{
  "message": "string",
  "id": "string"
}
```
 
Dois cookies `httponly` são definidos automaticamente na resposta:
 
| Cookie          | Descrição                          |
|-----------------|------------------------------------|
| `access-token`  | JWT de curta duração (10 minutos)  |
| `refresh-token` | JWT de longa duração (24 horas)    |
 
### Erros possíveis
 
| Status | Causa                                                             |
|--------|-------------------------------------------------------------------|
| `400`  | Username muito curto/longo, e-mail inválido, senha fora do padrão |
| `409`  | Username já em uso, e-mail já em uso                              |
| `500`  | Erro interno ao salvar no banco                                   |

---
 
## GET `/user/` — Ver minha conta
 
Retorna os dados completos do usuário autenticado. **Requer login**.
 
### Resposta de Sucesso — `200`
 
```json
{
  "user_id": "string",
  "username": "string",
  "pfp": "string | null",
  "email": "string",
  "bio": "string | null",
  "created_at": "string",
  "follows": {
    "follower_count": 0,
    "followers": [
      { "username": "string", "pfp": "string | null" }
    ],
    "following_count": 0,
    "followings": [
      { "username": "string", "pfp": "string | null" }
    ]
  },
  "lists": {
    "count": 0,
    "lists": [
      {
        "name": "string",
        "description": "string",
        "is_private": true,
        "creator": "string",
        "created_at": "string",
        "list_saves": 0
      }
    ]
  }
}
```
 
### Erros possíveis
 
| Status | Causa                              |
|--------|------------------------------------|
| `401`  | Usuário não autenticado            |
| `500`  | Erro interno ao buscar os dados    |
 
---
 
## PUT `/user` — Editar conta
 
Atualiza os dados do usuário autenticado. **Requer login**.
 
### Request Body
 
```json
{
  "username": "string",
  "pfp": "string | null",
  "email": "string",
  "bio": "string | null"
}
```
 
| Campo      | Tipo           | Obrigatório  | Padrão | Regras                                            |
|------------|----------------|--------------|--------|---------------------------------------------------|
| `username` | string         | ✅           | -      | Entre 4 e 24 caracteres, não pode estar em uso    |
| `email`    | string         | ✅           | -      | Formato de e-mail válido, não pode estar em uso   |
| `bio`      | string ou null | ❌           | null   | Até 280 caractéres, não pode ser só espaço vazios |
| `pfp`      | string ou null | ❌           | null   | URL/caminho da foto de perfil                     |
 
### Resposta de Sucesso — `200`
 
Retorna os dados completos atualizados do usuário

```json
{
  "username": "string",
  "pfp": "string | null",
  "email": "string",
  "bio": "string | null",
  "created_at": "string",
  "follows": {
    "follower_count": 0,
    "followers": [
      { "username": "string", "pfp": "string | null" }
    ],
    "following_count": 0,
    "followings": [
      { "username": "string", "pfp": "string | null" }
    ]
  },
  "lists": {
    "count": 0,
    "lists": [
      {
        "name": "string",
        "description": "string",
        "is_private": true,
        "creator": "string",
        "created_at": "string",
        "list_saves": 0
      }
    ]
  }
}
```
 
### Erros possíveis
 
| Status | Causa                                          |
|--------|------------------------------------------------|
| `400`  | Username muito curto/longo, e-mail inválido    |
| `401`  | Usuário não autenticado                        |
| `409`  | Username já em uso, e-mail já em uso           |
| `500`  | Erro interno ao atualizar os dados             |
 
---
 
## GET `/user/{user_id}` — Ver conta de outro usuário
 
Retorna os dados públicos de qualquer usuário pelo user_id. **Não requer login**.
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                        |
|------------|--------|----------------------------------|
| `user_id` | string | ID único do usuário a ser buscado |
 
### Resposta de Sucesso — `200`
 
Retorna os dados completos atualizados do usuário

```json
{
  "username": "string",
  "pfp": "string | null",
  "bio": "string | null",
  "created_at": "string",
  "follows": {
    "follower_count": 0,
    "followers": [
      { "username": "string", "pfp": "string | null" }
    ],
    "following_count": 0,
    "followings": [
      { "username": "string", "pfp": "string | null" }
    ]
  },
  "lists": {
    "count": 0,
    "lists": [
      {
        "name": "string",
        "description": "string",
        "is_private": true,
        "creator": "string",
        "created_at": "string",
        "list_saves": 0
      }
    ]
  }
}
```
 
### Erros possíveis
 
| Status | Causa                                                      |
|--------|------------------------------------------------------------|
| `403`  | Usuário está tentando ver a conta de alguém que o bloqueou |
| `404`  | Usuário alvo não encontrado                                |
| `500`  | Erro interno ao buscar os dados                            |
 
---
 
## POST `/user/follow/{user_id}` — Seguir usuário
 
Faz o usuário autenticado seguir outro usuário. **Requer login**.
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                         |
|------------|--------|-----------------------------------|
| `user_id` | string | ID único do usuário a ser seguido |
 
### Resposta de Sucesso — `200`
 
```json
{
  "message": "string"
}
```
 
### Erros possíveis
 
| Status | Causa                                                            |
|--------|------------------------------------------------------------------|
| `401`  | Usuário não autenticado                                          |
| `403`  | Usuário está tentando seguir a si mesmo ou alguém que o bloqueou |
| `404`  | Usuário a ser seguido não encontrado                             |
| `500`  | Erro interno ao buscar os dados                                  |   
 
---
 
## DELETE `/user/follow/{user_id}` — Deixar de seguir usuário
 
Faz o usuário autenticado deixar de seguir outro usuário. **Requer login**.
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                                    |
|------------|--------|----------------------------------------------|
| `user_id` | string | ID único do usuário a ser deixado de seguir  |
 
### Resposta de Sucesso — `200`
 
```json
{
  "message": "string"
}
```
 
### Erros possíveis
 
| Status | Causa                                          |
|--------|------------------------------------------------|
| `401`  | Usuário não autenticado                        |
| `404`  | Usuário a deixar de ser seguido não encontrado |
| `500`  | Erro interno ao buscar os dados                |


## GET `/user/follow/followers` — Ver os seguidores do usuário

Retorna os seguidores do usuário. **Requer login**.

### Query Parameters

| Parâmetro   | Tipo           | Obrigatório | Padrão | Descrição|
|-------------|----------------|-------------|--------|----------|
| `page_size` | inteiro        | ❌          | 10     | Número de itens por página|
| `cursor`    | string ou null | ❌          | null   | Cursor para buscar a próxima página|
| `search`    | string ou null | ❌          | null   | Parâmetro de busca por um termo específico|

### Resposta de Sucesso — `200`
 
```json
{
  "total": 0,
  "page_size": 0,
  "content": [
    {
      "user_id": "string",
      "username": "string",
      "pfp": "string | null"
    }
  ],
  "current_page": "string | null",
  "next_page": "string | null",
  "previous_page": "string | null"
}
```
 
### Erros possíveis
 
| Status | Causa                            |
|--------|----------------------------------|
| `401`  | Usuário não autenticado          |
| `500`  | Erro interno ao buscar os dados  |  

---

## GET `/user/follow/followeds` — Ver os seguidos do usuário

Retorna os seguidos do usuário. **Requer login**.

### Query Parameters

| Parâmetro   | Tipo           | Obrigatório | Padrão | Descrição|
|-------------|----------------|-------------|--------|----------|
| `page_size` | inteiro        | ❌          | 10     | Número de itens por página|
| `cursor`    | string ou null | ❌          | null   | Cursor para buscar a próxima página|
| `search`    | string ou null | ❌          | null   | Parâmetro de busca por um termo específico|

### Resposta de Sucesso — `200`
 
```json
{
  "total": 0,
  "page_size": 0,
  "content": [
    {
      "user_id": "string",
      "username": "string",
      "pfp": "string | null"
    }
  ],
  "current_page": "string | null",
  "next_page": "string | null",
  "previous_page": "string | null"
}
```
 
### Erros possíveis
 
| Status | Causa                            |
|--------|----------------------------------|
| `401`  | Usuário não autenticado          |
| `500`  | Erro interno ao buscar os dados  |  

---
 
## DELETE `/user/` — Deletar conta

Remove permanentemente a conta do usuário autenticado. **Requer login**.

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
| `500`  | Erro interno ao deletar a conta    |

---

## POST `/user/block/{user_id}` — Bloquear usuário

Faz o usuário autenticado bloquear outro usuário. **Requer login**.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                          |
|------------|--------|------------------------------------|
| `user_id` | string | ID único do usuário a ser bloqueado |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                       |
|--------|---------------------------------------------|
| `401`  | Usuário não autenticado                     |
| `403`  | Usuário está tentando bloquear a si mesmo   |
| `404`  | Usuário a ser bloqueado não encontrado      |
| `500`  | Usuário alvo não encontrado ou erro interno |

---

## DELETE `/user/block/{user_id}` — Desbloquear usuário

Faz o usuário autenticado desbloquear um usuário previamente bloqueado. **Requer login**.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                             |
|------------|--------|---------------------------------------|
| `user_id` | string | ID único do usuário a ser desbloqueado |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

### Erros possíveis

| Status | Causa                                       |
|--------|---------------------------------------------|
| `401`  | Usuário não autenticado                     |
| `404`  | Usuário a ser desbloqueado não encontrado   |
| `500`  | Erro interno ao buscar os dados             |

---

## GET `/user/block` — Ver os bloqueados pelo usuário

Retorna os bloqueados pelo usuário. **Requer login**.

### Query Parameters

| Parâmetro   | Tipo           | Obrigatório | Padrão | Descrição|
|-------------|----------------|-------------|--------|----------|
| `page_size` | inteiro        | ❌          | 10     | Número de itens por página|
| `cursor`    | string ou null | ❌          | null   | Cursor para buscar a próxima página|
| `search`    | string ou null | ❌          | null   | Parâmetro de busca por um termo específico|

### Resposta de Sucesso - `200`

```json
{
  "total": 0,
  "page_size": 0,
  "content": [
    {
      "username": "string",
      "pfp": "string | null",
      "user_id": "string"
    }
  ],
  "current_page": "string | null",
  "next_page": "string | null",
  "previous_page": "string | null"
}
```
 
### Erros possíveis
 
| Status | Causa                            |
|--------|----------------------------------|
| `401`  | Usuário não autenticado          |
| `500`  | Erro interno ao buscar os dados  |  

---
