# 📡 Documentação das Rotas de Listas


## Sumário

- [POST `/list/`](#post-list---criar-lista)
- [GET `/list/{list_name}`](#get-listlist_name---ver-minha-lista)
- [GET `/list/{list_creator}/{list_name}`](#get-listlist_creatorlist_name---ver-lista-de-outro-usuário)
- [PUT `/list/{old_list_name}`](#put-listold_list_name---editar-lista)
- [DELETE `/list/{list_name}`](#delete-listlist_name---deletar-lista)
- [POST `/list/save/{list_creator}/{list_name}`](#post-listsavelist_creatorlist_name---salvar-lista)
- [DELETE `/list/save/{list_creator}/{list_name}`](#delete-listsavelist_creatorlist_name---remover-lista-salva)
- [POST `/list/game/{list_name}/{game_id}`](#post-listgamelist_namegame_id---adicionar-jogo-à-lista)
- [DELETE `/list/game/{list_name}/{game_id}`](#delete-listgamelist_namegame_id---remover-jogo-da-lista)

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

| Campo         | Tipo    | Obrigatório | Padrão | Regras                                        |
|---------------|---------|-------------|--------|-----------------------------------------------|
| `name`        | string  | ✅          | —      | Máximo de 60 caracteres, único por usuário    |
| `description` | string  | ❌          | `null` | Máximo de 300 caracteres                      |
| `is_private`  | boolean | ❌          | `true` | Se `true`, a lista só é visível ao criador    |

### Resposta de Sucesso — `200`

```json
{
  "message": "Lista criada com sucesso!",
  "id": 1
}
```

### Erros possíveis

| Status | Causa                                               |
|--------|-----------------------------------------------------|
| `400`  | Nome ou descrição acima do limite de caractéres     |
| `401`  | Usuário não autenticado                             |
| `409`  | Usuário já possui uma lista com esse nome           |
| `500`  | Erro interno ao salvar no banco                     |      

---

## GET `/list/{list_id}` — Ver minha lista

Retorna os dados completos de uma lista feita pelo usuário autenticado, incluindo suas listas privadas. **Login opcional**.

### Path Parameter

| Parâmetro   | Tipo   | Descrição                        |
|-------------|--------|----------------------------------|
| `list_id`   | string | ID único da lista a ser buscada  |

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
      "year": 0,
      "like_count": 0,
      "gamerboxd_rating": 0.0
    }
  ]
}
```

### Erros possíveis

| Status | Causa                              |
|--------|------------------------------------|
| `401`  | Usuário não autenticado            |
| `404`  | Lista não encontrada               |
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

| Status | Causa                                                        |
|--------|--------------------------------------------------------------|
| `403`  | Usuário está tentando ver uma lista de alguém que o bloqueou |
| `404`  | Usuário não encontrado, lista não encontrada ou privada      |
| `500`  | Erro interno ao buscar os dados                              |

---

## PUT `/list/{list_id}` — Editar lista

Atualiza os dados de uma lista do usuário autenticado. **Requer login**.

### Path Parameter

| Parâmetro       | Tipo   | Descrição                         |
|-----------------|--------|-----------------------------------|
| `list_id`       | string | ID da lista a ser editada         |

### Request Body

Mesmo formato do [POST `/list/`](#post-list---criar-lista).

### Resposta de Sucesso — `200`

Retorna os dados completos da lista atualizada, incluindo os jogos:

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
      "year": 0,
      "like_count": 0,
      "gamerboxd_rating": 0.0
    }
  ]
}
```

### Erros possíveis

| Status | Causa                                |
|--------|--------------------------------------|
| `400`  | Nome ou descrição acima do limite    |
| `401`  | Usuário não autenticado              |
| `403`  | Falta de propriedade da lista        |
| `409`  | Novo nome já está em uso             |
| `500`  | Erro interno ao atualizar no banco   |

---

## DELETE `/list/{list_id}` — Deletar lista

Remove uma lista do usuário autenticado. **Requer login**.

### Path Parameter

| Parâmetro   | Tipo   | Descrição                      |
|-------------|--------|--------------------------------|
| `list_id`   | string | ID da lista a ser deletada     |

### Resposta de Sucesso — `200`

```json
{
  "message": "Lista deletada com sucesso!"
}
```

### Erros possíveis

| Status | Causa                                                        |
|--------|--------------------------------------------------------------|
| `401`  | Usuário não autenticado                                      |
| `403`  | Falta de propriedade da lista                                |
| `404`  | Usuário não encontrado, lista não encontrada ou privada      |
| `500`  | Erro interno ao deletar no banco                             |

---

## POST `/list/save/{list_id}` — Salvar lista

Salva a lista pública de outro usuário na biblioteca do autenticado. **Requer login**.

### Path Parameters

| Parâmetro      | Tipo   | Descrição                      |
|----------------|--------|--------------------------------|
| `list_id`      | string | ID da lista a ser salva        |

### Resposta de Sucesso — `200`

```json
{
  "message": "Lista salva com sucesso!"
}
```

### Erros possíveis

| Status | Causa                                                   |
|--------|---------------------------------------------------------|
| `401`  | Usuário não autenticado                                 |
| `403`  | Falta de propriedade da lista                           |
| `404`  | Usuário não encontrado, lista não encontrada ou privada |
| `500`  | Erro interno ao salvar                                  |

---

## DELETE `/list/save/{list_id}` — Remover lista salva

Remove uma lista previamente salva da biblioteca do usuário autenticado. **Requer login**.

### Path Parameters

| Parâmetro      | Tipo   | Descrição                            |
|----------------|--------|--------------------------------------|
| `list_id`      | string | ID da lista a ser removida           |

### Resposta de Sucesso — `200`

```json
{
  "message": "Lista dessalvada com sucesso"
}
```

### Erros possíveis

| Status | Causa                                                   |
|--------|---------------------------------------------------------|
| `401`  | Usuário não autenticado                                 |
| `403`  | Usuário tentando dessalvar sua própria lista            |
| `404`  | Usuário não encontrado, lista não encontrada ou privada |
| `500`  | Erro interno ao remover                                 |

---

## POST `/list/game/{list_id}/{game_id}` — Adicionar jogo à lista

Adiciona um jogo a uma lista do usuário autenticado. **Requer login**.

### Path Parameters

| Parâmetro   | Tipo   | Descrição                                  |
|-------------|--------|--------------------------------------------|
| `list_id`   | string | ID da lista que receberá o jogo            |
| `game_id`   | int    | ID do jogo a ser adicionado                |

### Resposta de Sucesso — `200`

```json
{
  "message": "Jogo adicionado à lista com sucesso"
}
```

### Erros possíveis

| Status | Causa                              |
|--------|------------------------------------|
| `401`  | Usuário não autenticado            |
| `403`  | Falta de propriedade da lista      |
| `404`  | Lista não encontrada               |
| `500`  | Erro interno ao adicionar o jogo   |

---

## DELETE `/list/game/{list_id}/{game_id}` — Remover jogo da lista

Remove um jogo de uma lista do usuário autenticado. **Requer login**.

### Path Parameters

| Parâmetro   | Tipo   | Descrição                                  |
|-------------|--------|--------------------------------------------|
| `list_id`   | string | ID da lista da qual o jogo será removido   |
| `game_id`   | int    | ID do jogo a ser removido                  |

### Resposta de Sucesso — `200`

```json
{
  "message": "Jogo removido da lista com sucesso"
}
```

### Erros possíveis

| Status | Causa                              |
|--------|------------------------------------|
| `401`  | Usuário não autenticado            |
| `403`  | Falta de propriedade da lista      |
| `404`  | Lista não encontrada               |
| `500`  | Erro interno ao remover o jogo     |

---

## GET `/list/created/{user_id} - Busca as listas criadas pelo usuário

Busca as listas criadas por um usuário específico  . **Login opcional**

### Path Parameter

| Parâmetro |  Tipo  | Descrição                                         |
|-----------|--------|---------------------------------------------------|
| `user_id` | string | ID do usuário cujas listas criadas serão buscadas |

### Query Parameters (Paginação)

Aceita parâmetros padrão de paginação (`PageQuery`).

### Resposta de Sucesso - `200`

Retorna um objeto paginado contendo a lista de listas criadas e seus metadados de navegação.

### Erros possíveis

| Status | Causa                                    |
|--------|------------------------------------------|
| `500`  | Erro interno ao buscar as listas criadas |

---

## GET `/list/save/lists` — Buscar listas salvas

Busca de forma paginada as listas que foram salvas na biblioteca do usuário autenticado. **Requer login**.

### Query Parameters (Paginação)

Aceita parâmetros padrão de paginação (`PageQuery`).

### Resposta de Sucesso — `200`

Retorna um objeto paginado contendo as listas salvas.

### Erros possíveis

| Status | Causa                                   |
|--------|-----------------------------------------|
| `401`  | Usuário não autenticado                 |
| `500`  | Erro interno ao buscar as listas salvas |

---

## GET `/list/save/users/{list_id}` — Buscar os dados dos usuários que salvaram a lista

Busca de forma paginada os dados dos usuários que salvaram uma determinada lista pública. 

### Path Parameter

| Parâmetro | Tipo   | Descrição         |
|-----------|--------|-------------------|
| `list_id` | string | ID único da lista |

### Query Parameters (Paginação)

Aceita parâmetros padrão de paginação (`PageQuery`).

### Resposta de Sucesso — `200`

Retorna um objeto paginado com os dados dos usuários que salvaram a lista.

### Erros possíveis

| Status | Causa                                                                                    |
|--------|------------------------------------------------------------------------------------------|
| `403`  | Usuário bloqueado pelo proprietário da lista                                             |
| `404`  | Lista não encontrada                                                                     |
| `500`  | Erro interno ao buscar os usuários                                                       | 

---

## GET `/list/game/{list_id}` — Busca os games que pertencem a uma lista do usuário

Busca de forma paginada os jogos que pertencem a uma lista específica.

### Path Parameter

| Parâmetro | Tipo   | Descrição         |
|-----------|--------|-------------------|
| `list_id` | string | ID único da lista |

### Query Parameters (Paginação)

Aceita parâmetros padrão de paginação (`PageQuery`).

### Resposta de Sucesso — `200`

Retorna um objeto paginado com os jogos pertencentes à lista.

### Erros possíveis

| Status | Causa                                                                                    |
|--------|------------------------------------------------------------------------------------------|
| `403`  | Usuário bloqueado pelo autor da lista ou tentativa de ver lista privada de outro usuário |
| `404`  | Lista não encontrada                                                                     |
| `500`  | Erro interno ao buscar os jogos da lista                                                 |

---