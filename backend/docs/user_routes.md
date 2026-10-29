# 📡 Documentação das Rotas de Usuário

 
## Sumário
 
- [POST `/users` — Criar conta](#post-users--criar-conta)
- [GET `/users/{user_id}` — Ver conta de um usuário](#get-usersuser_id--ver-conta-de-um-usuário)
- [PUT `/users` — Editar conta](#put-users--editar-conta)
- [DELETE `/users` — Deletar conta](#delete-users--deletar-conta)
- [POST `/users/follow/{user_id}` — Seguir usuário](#post-usersfollowuser_id--seguir-usuário)
- [DELETE `/users/follow/{user_id}` — Deixar de seguir usuário](#delete-usersfollowuser_id--deixar-de-seguir-usuário)
- [GET `/users/follow/followers/{user_id}` — Ver os seguidores do usuário](#get-usersfollowfollowersuser_id--ver-os-seguidores-do-usuário)
- [GET `/users/follow/followings/{user_id}` — Ver os seguidos do usuário](#get-usersfollowfollowingsuser_id--ver-os-seguidos-do-usuário)
- [POST `/users/block/{user_id}` — Bloquear usuário](#post-usersblockuser_id--bloquear-usuário)
- [DELETE `/users/block/{user_id}` — Desbloquear usuário](#delete-usersblockuser_id--desbloquear-usuário)
- [GET `/users/block` — Ver os bloqueados pelo usuário](#get-usersblock--ver-os-bloqueados-pelo-usuário)

---
 
## POST `/users` — Criar conta
 
Cria uma nova conta de usuário.

**Regras e comportamentos:**
- **Não requer login**.
- Ao criar a conta, duas listas padrão são geradas automaticamente: **Jogos Favoritos** e **Jogos Completados**. 
- Na resposta, são definidos automaticamente os dois [cookies padrão de autenticação](./routes.md#cookies-de-autenticação).
 
### Request Body
 
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
 
| Campo      | Tipo   | Obrigatório | Regras                                            |
|------------|--------|-------------| --------------------------------------------------|
| `username` | string | ✅          | Entre 4 e 24 caracteres, não pode estar em uso    |
| `email`    | string | ✅          | Formato de e-mail válido, não pode estar  |
| `password` | string | ✅          | Entre 8 e 64 caracteres, com ao menos: 1 maiúscula, 1 minúscula, 1 número e 1 símbolo |

### Resposta de Sucesso — `200`
 
```json
{"message":"Conta criada com sucesso!", "user_id": "string"}
```
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR (human readable)    | Causa                                                             |
|--------|------------------------|-------------------------------------------------------------------|
| `400`  | ✅                     | Username muito curto/longo, e-mail inválido, senha fora do padrão |
| `409`  | ✅                     | Username já em uso, e-mail já em uso                              |
| `422`  | ❌                     | Campo(s) do request body ausentes ou inválidos                    |
| `500`  | ❌                     | Erro interno                                                      |

--- 

## GET `/users/{user_id}` — Ver conta de um usuário
 
Retorna os dados de um usuário pelo user_id.

**Regras e comportamentos:**
- **Requer login**.
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                         |
|------------|--------|-----------------------------------|
| `user_id`  | string | ID único do usuário a ser buscado |
 
### Resposta de Sucesso — `200`
 
Retorna schema [**\_\_USER_FULL\_\_**](./routes.md#__user_full__).
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR     | Causa                                                        |
|--------|--------|--------------------------------------------------------------|
| `400`  | ✅     | Usuário está tentando ver a conta de alguém que ele bloqueou |
| `401`  | ✅     | Usuário não autenticado                                      |
| `404`  | ✅     | Usuário alvo não encontrado                                  |
| `433`  | ❌     | Usuário está tentando ver a conta de alguém que o bloqueou   |
| `500`  | ❌     | Erro interno                                                 |
 
---

## PUT `/users` — Editar conta
 
Atualiza os dados do usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.
- Até os campos inalterados precisam ser enviados.
 
### Request Body
 
```json
{
  "username": "string",
  "email": "string",
  "pfp": "string" | null,
  "banner": "string" | null,
  "bio": "string" | null
}
```
 
| Campo      | Tipo           | Obrigatório  | Regras                                            |
|------------|----------------|--------------|---------------------------------------------------|
| `username` | string,        | ✅           | Entre 4 e 24 caracteres, não pode estar em uso    |
| `email`    | string,        | ✅           | Formato de e-mail válido, não pode estar em uso   |
| `bio`      | string, null   | ✅           | Até 280 caracteres, não pode ser só espaço vazios |
| `pfp`      | string, null   | ✅           | Caminho da foto de perfil                         |
| `banner`   | string, null   | ✅           | Caminho do banner do perfil                       |
 

### Resposta de Sucesso — `200`
 
Retorna schema [**\_\_USER_FULL\_\_**](./routes.md#__user_full__).
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR     | Causa                                 |
|--------|--------|---------------------------------------|
| `400`  | ✅     | Username muito curto/longo, e-mail inválido, descrição muito longa ou apenas espaço vazio |
| `401`  | ✅     | Usuário não autenticado               |
| `409`  | ✅     | Username já em uso, e-mail já em uso  |
| `422`  | ❌     | Campo(s) do request body ausentes ou inválidos |
| `500`  | ❌     | Erro interno                          |
 
---
 
## DELETE `/users` — Deletar conta

Remove permanentemente a conta do usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.
- As listas criadas pelo autenticado são deletadas, logo removidas de todas as bibliotecas de usuários que as salvaram.
- As reviews escritas pelo autenticado são deletadas, logo os likes de outros usuários são removidos também.
- Os saves que o autenticado deu em listas criadas por outros usuários são deletados.
- Os likes que o autenticado deu em reviews criadas por outros usuários são deletados.
- Todos os relacionamentos do autenticado (seguidos, seguidores, bloqueios) são deletados.
- Os [cookies padrão de autenticação](./routes.md#cookies-de-autenticação) são deletados automaticamente na resposta.

### Resposta de Sucesso — `200`

```json
{"message" : "Conta deletada com sucesso!"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                           |
|--------|--------|---------------------------------|
| `401`  | ✅     | Usuário não autenticado         |
| `500`  | ❌     | Erro interno                    | 

---
 
## POST `/users/follow/{user_id}` — Seguir usuário
 
Faz o usuário autenticado seguir outro usuário. 

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado já seguir usuário alvo, a rota não irá levantar erro (idempotência).


### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                         |
|------------|--------|-----------------------------------|
| `user_id`  | string | ID único do usuário a ser seguido |
 
### Resposta de Sucesso — `200`
 
```json
{"message": "Conta seguida com sucesso!"}
```
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR     | Causa                                                            |
|--------|--------|------------------------------------------------------------------|
| `400`  | ✅     | Usuário está tentando seguir alguém que ele bloqueou             |
| `401`  | ✅     | Usuário não autenticado                                          |
| `403`  | ❌     | Usuário está tentando seguir a si mesmo                          |
| `404`  | ✅     | Usuário a ser seguido não encontrado                             |
| `433`  | ❌     | Usuário está tentando seguir alguém que o bloqueou               |
| `500`  | ❌     | Erro interno                                                     |   
 
---
 
## DELETE `/users/follow/{user_id}` — Deixar de seguir usuário
 
Faz o usuário autenticado deixar de seguir outro usuário. 

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado não seguir o usuário alvo, a rota não irá levantar erro (idempotência).
 
### Path Parameter
 
| Parâmetro  | Tipo   | Descrição                             |
|------------|--------|---------------------------------------|
| `user_id`  | string | ID único do usuário a ser desseguido  |
 
### Resposta de Sucesso — `200`
 
```json
{"message":"Conta desseguida com sucesso!"}
```
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR     | Causa                                     |
|--------|--------|-------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                   |
| `404`  | ✅     | Usuário a ser desseguido não encontrado   |
| `500`  | ❌     | Erro interno                              | 

---

## GET `/users/follow/followers/{user_id}` — Ver os seguidores do usuário

Busca de forma paginada os seguidores do usuário.

**Regras e comportamentos:**
- **Requer login**.
- Apenas o próprio dono da conta ou alguém que o dono da conta siga tem permissão para ver esses dados.
 

### Path Parameter

| Parâmetro  | Tipo   | Descrição                                                         |
|------------|--------|-------------------------------------------------------------------|
| `user_id`  | string | ID único do usuário sobre o qual se quer visualizar os seguidores |

### Query Parameters ([Paginação](./routes.md#rotas-paginadas))

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis usernames dos seguidores do usuário.
- order padrão é `!created_at`, que mostra os mais recentes seguidores do usuário. Os orders possíveis são: `["created_at", "!created_at", "username", "!username"]`.

### Resposta de Sucesso — `200`
 
Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas **\_\_USER\_\_**.
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR     | Causa                                                       |
|--------|--------|-------------------------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                                     |
| `403`  | ❌     | Usuário não é o dono da conta ou seguido pelo dono da conta |
| `404`  | ✅     | Usuário dono da conta não encontrado                        |
| `422`  | ❌     | Query parameters inválidos                                  |
| `500`  | ❌     | Erro interno                                                |  

---

## GET `/users/follow/followings/{user_id}` — Ver os seguidos do usuário

Busca de forma paginada os seguidos pelo usuário.

**Regras e comportamentos:**
- **Requer login**.
- Apenas o próprio dono da conta ou alguém que o dono da conta siga tem permissão para ver esses dados.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                                            |
|------------|--------|------------------------------------------------------|
| `user_id`  | string | ID único sobre o qual se quer visualizar os seguidos |

### Query Parameters ([Paginação](./routes.md#rotas-paginadas))

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis usernames dos seguidos pelo usuário.
- order padrão é `!created_at`, que mostra os mais recentes seguidos pelo usuário. Os orders possíveis são: `["created_at", "!created_at", "username", "!username"]`.

### Resposta de Sucesso — `200`
 
Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas **\_\_USER\_\_**.
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR     | Causa                                                       |
|--------|--------|-------------------------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                                     |
| `403`  | ❌     | Usuário não é o dono da conta ou seguido pelo dono da conta |
| `404`  | ✅     | Usuário dono da conta não encontrado                        |
| `422`  | ❌     | Query parameters inválidos                                  |
| `500`  | ❌     | Erro interno                                                |

---

## POST `/users/block/{user_id}` — Bloquear usuário

Faz o usuário autenticado bloquear outro usuário.

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado já tiver bloqueado o usuário alvo, a rota não irá levantar erro (idempotência).
- Se o autenticado seguia o usuário alvo, ele irá deixar de seguir.
- Se o usuário alvo seguia o autenticado, ele irá deixar de seguir.
- Se o autenticado tiver salvado alguma lista do usuário alvo, ele irá deixar de salvar.
- Se o usuário alvo tiver salvado alguma lista do autenticado, ele irá deixar de salvar.
- Se o autenticado tiver dado like em alguma review do usuário alvo, o like será removido.
- Se o usuário alvo tiver dado like em alguma review do autenticado, o like será removido.

### Path Parameter

| Parâmetro  | Tipo   | Descrição                           |
|------------|--------|-------------------------------------|
| `user_id`  | string | ID único do usuário a ser bloqueado |

### Resposta de Sucesso — `200`

```json
{"message":"Conta bloqueada com sucesso!"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                                       |
|--------|--------|---------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                     |
| `403`  | ❌     | Usuário está tentando bloquear a si mesmo   |
| `404`  | ✅     | Usuário a ser bloqueado não encontrado      |
| `500`  | ❌     | Erro interno                                |

---

## DELETE `/users/block/{user_id}` — Desbloquear usuário

Faz o usuário autenticado desbloquear um usuário.

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado não tiver bloqueado o usuário alvo, a rota não irá levantar erro (idempotência).


### Path Parameter

| Parâmetro  | Tipo   | Descrição                             |
|------------|--------|---------------------------------------|
| `user_id`  | string | ID único do usuário a ser desbloqueado|

### Resposta de Sucesso — `200`

```json
{"message":"Conta desbloqueada com sucesso!"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                                       |
|--------|--------|---------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                     |
| `404`  | ✅     | Usuário a ser desbloqueado não encontrado   |
| `500`  | ❌     | Erro interno                                |

---

## GET `/users/block` — Ver os bloqueados pelo usuário

Busca de forma paginada os bloqueados pelo usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.

### Query Parameters ([Paginação](./routes.md#rotas-paginadas))

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis usernames dos bloqueados pelo usuário.
- order padrão é `!created_at`, que mostra os mais recentes bloqueados pelo usuário. Os orders possíveis são: `["created_at", "!created_at", "username", "!username"]`.

### Resposta de Sucesso — `200`
 
Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas **\_\_USER\_\_**.
 
### [Erros](./routes.md#erros) possíveis
 
| Status | HR     | Causa                           |
|--------|--------|---------------------------------|
| `401`  | ✅     | Usuário não autenticado         |
| `422`  | ❌     | Query parameters inválidos      |
| `500`  | ❌     | Erro interno                    |

---