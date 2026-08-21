# 📡 Documentação das Rotas de Usuário
 
## Sumário
 
- [POST `/user/`](#post-user---criar-conta)
- [GET `/user/`](#get-user---ver-minha-conta)
- [PUT `/user/`](#put-user---editar-conta)
- [GET `/user/view/{username}`](#get-userview-username---ver-conta-de-outro-usuário)
- [POST `/user/follow/{username}`](#post-userfollow-username---seguir-usuário)
- [POST `/user/unfollow/{username}`](#post-userunfollow-username---deixar-de-seguir-usuário)
- [DELETE `/user/`](#delete-user---deletar-conta)
- [POST `/user/block/{username}`](#post-userblockusername---bloquear-usuário)
- [POST `/user/unblock/{username}`](#post-userunblockusername---desbloquear-usuário)

---
 
## POST `/user/` — Criar conta
 
Cria uma nova conta de usuário. Ao criar a conta, duas listas padrão são geradas automaticamente: **Favoritos** e **Completados**.
 
### Request Body
 
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
 
| Campo      | Tipo            | Obrigatório | Regras |
|------------|-----------------|-------------|--------|
| `username` | string          | ✅          | Entre 4 e 24 caractéres, não pode estar em uso |
| `email`    | string          | ✅          | Formato de e-mail válido, não pode estar em uso|
| `password` | string          | ✅          | Entre 8 e 64 caracteres, com ao menos: 1 maiúscula, 1 minúscula, 1 número e 1 símbolo|

### Resposta de Sucesso — `200`
 
```json
{
  "message": "string"
}
```
 
Dois cookies `httponly` são definidos automaticamente na resposta:
 
| Cookie          | Descrição                          |
|-----------------|------------------------------------|
| `access-token`  | JWT de curta duração (10 minutos)  |
| `refresh-token` | JWT de longa duração (24 horas)    |
 
### Erros possíveis
 
| Status | Causa                                                            |
|--------|------------------------------------------------------------------|
| `400`  | Username muito curto/longo ou já em uso, e-mail inválido ou já em uso, senha fora do padrão |
| `500`  | Erro interno ao salvar no banco                                  |
 
---
 
## GET `/user/` — Ver minha conta
 
Retorna os dados completos do usuário autenticado. **Requer login**.
 
### Resposta de Sucesso — `200`
 
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
 
| Status | Causa                              |
|--------|------------------------------------|
| `401`  | Usuário não autenticado            |
| `500`  | Erro interno ao buscar os dados    |
 
---
 
## PUT `/user/` — Editar conta
 
Atualiza os dados do usuário autenticado. **Requer login**.
 
### Request Body
 
```json
{
  "username": "string",
  "email": "string",
  "bio": "string",
  "pfp": "string | null"
}
```
 
| Campo      | Tipo           | Obrigatório | Regras                                          |
|------------|----------------|-------------|-------------------------------------------------|
| `username` | string         | ✅           | Entre 4 e 24 caracteres                         |
| `email`    | string         | ✅           | Formato de e-mail válido, não pode estar em uso |
| `bio`      | string         | ✅           | Texto livre de biografia                        |
| `pfp`      | string ou null | ✅           | URL/caminho da foto de perfil                   |
 
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
 
| Status | Causa                                                  |
|--------|--------------------------------------------------------|
| `400`  | Username inválido, e-mail inválido ou já em uso        |
| `401`  | Usuário não autenticado                                |
| `500`  | Erro interno ao atualizar os dados                     |
 
---
 
## GET `/user/view/{username}` — Ver conta de outro usuário
 
Retorna os dados públicos de qualquer usuário pelo username. **Não requer login**.
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                        |
|------------|--------|----------------------------------|
| `username` | string | Username do usuário a ser buscado |
 
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
 
| Status | Causa                          |
|--------|--------------------------------|
| `500`  | Usuário não encontrado ou erro interno |
 
---
 
## POST `/user/follow/{username}` — Seguir usuário
 
Faz o usuário autenticado seguir outro usuário. **Requer login**.
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                         |
|------------|--------|-----------------------------------|
| `username` | string | Username do usuário a ser seguido |
 
### Resposta de Sucesso — `200`
 
```json
{
  "message": "string"
}
```
 
### Erros possíveis
 
| Status | Causa                                     |
|--------|-------------------------------------------|
| `401`  | Usuário não autenticado                   |
| `500`  | Usuário alvo não encontrado ou erro interno |
 
---
 
## POST `/user/unfollow/{username}` — Deixar de seguir usuário
 
Faz o usuário autenticado deixar de seguir outro usuário. **Requer login**.
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                                    |
|------------|--------|----------------------------------------------|
| `username` | string | Username do usuário a ser deixado de seguir  |
 
### Resposta de Sucesso — `200`
 
```json
{
  "message": "string"
}
```
 
### Erros possíveis
 
| Status | Causa                                        |
|--------|----------------------------------------------|
| `401`  | Usuário não autenticado                      |
| `500`  | Usuário alvo não encontrado ou erro interno  |
 
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

## POST `/user/block/{username}` — Bloquear usuário

Faz o usuário autenticado bloquear outro usuário. **Requer login**.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                          |
|------------|--------|------------------------------------|
| `username` | string | Username do usuário a ser bloqueado |

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
| `500`  | Usuário alvo não encontrado ou erro interno |

---

## POST `/user/unblock/{username}` — Desbloquear usuário

Faz o usuário autenticado desbloquear um usuário previamente bloqueado. **Requer login**.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                             |
|------------|--------|---------------------------------------|
| `username` | string | Username do usuário a ser desbloqueado |

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
| `500`  | Usuário alvo não encontrado ou erro interno |

---

## 🔐 Autenticação
 
As rotas que requerem login dependem do cookie `access-token` enviado automaticamente pelo browser. Certifique-se de que as requisições são feitas com `credentials: 'include'` (fetch) ou `withCredentials: true` (axios).
 
```js
// Exemplo com fetch
fetch('/user/', {
  credentials: 'include'
})
 
// Exemplo com axios
axios.get('/user/', { withCredentials: true })
```
 
---