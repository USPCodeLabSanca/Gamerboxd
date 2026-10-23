# 📡 Documentação das Rotas de Listas


## Sumário

- [POST `/lists` — Criar lista](#post-lists--criar-lista)
- [GET `/lists/{list_id}` — Ver lista](#get-listslist_id--ver-lista)
- [PUT `/lists/{list_id}` — Editar lista](#put-listslist_id--editar-lista)
- [DELETE `/lists/{list_id}` — Deletar lista](#delete-listslist_id--deletar-lista)
- [GET `/lists/created/{user_id}` — Busca as listas criadas pelo usuário](#get-listscreateduser_id--busca-as-listas-criadas-pelo-usuário)
- [POST `/lists/save/{list_id}` — Salvar lista](#post-listssavelist_id--salvar-lista)
- [DELETE `/lists/save/{list_id}` — Remover lista salva](#delete-listssavelist_id--remover-lista-salva)
- [GET `/lists/save` — Buscar listas salvas](#get-listssave--buscar-listas-salvas)
- [POST `/lists/game/{list_id}/{game_id}` — Adicionar jogo à lista](#post-listsgamelist_idgame_id--adicionar-jogo-à-lista)
- [DELETE `/lists/game/{list_id}/{game_id}` — Remover jogo da lista](#delete-listsgamelist_idgame_id--remover-jogo-da-lista)
- [GET `/lists/game/{list_id}` — Busca os games que pertencem a uma lista](#get-listsgamelist_id--busca-os-games-que-pertencem-a-uma-lista)

---

## POST `/lists` — Criar lista

Cria uma nova lista para o usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.
-  Ao ser criada, a lista é automaticamente salva para o autor, e os games passados são automaticamente inclusos na lista.
-  Se um game_id não for válido, a rota não irá retornar erro: a lista ainda será criada mas esse game não será incluso nela, e o game_id será retornado no array `not_included` no response body de sucesso. Game_ids repetidos serão apenas ignorados. 

### Request Body

```json
{
  "name": "string",
  "description": "string" | null,
  "privacy": 0,
  "first_games": [0]  
}
```

| Campo         | Tipo      | Obrigatório | Padrão | Regras                                                    |
|---------------|-----------|-------------|--------|-----------------------------------------------------------|
| `name`        | string    | ✅          | —      | Máximo de 45 caracteres, único por usuário                |
| `description` | string    | ❌          | `null` | Máximo de 300 caracteres                                  |
| `privacy`     | int       | ✅          | —      | Deve ser um dos valores dispostos na seção de privacidade |
| `first_games` | list[int] | ❌          | `[]`   | Os itens devem ser game_id válidos e distintos            |

### Resposta de Sucesso — `200`

```json
{"message":"Lista criada com sucesso!", "list_id": "string", "not_included": [0]}
```

### Erros possíveis

| Status | HR (human readable)    | Causa                                               |
|--------|------------------------|-----------------------------------------------------|
| `400`  | ✅                     | Nome ou descrição acima do limite de caracteres     |
| `401`  | ✅                     | Usuário não autenticado                             |
| `406`  | ❌                     | A privacidade não é um dos valores válidos          |
| `409`  | ✅                     | Usuário já possui uma lista com esse nome           |
| `500`  | ❌                     | Erro interno                                        |      

---

## GET `/lists/{list_id}` — Ver lista

Retorna os dados completos de uma lista.

**Regras e comportamentos:**
- **Não requer login**.

### Path Parameter

| Parâmetro   | Tipo   | Descrição                        |
|-------------|--------|----------------------------------|
| `list_id`   | string | ID único da lista a ser buscada  |

### Resposta de Sucesso — `200`

Retorna schema **\_\_LIST_FULL\_\_**

### Erros possíveis

| Status | HR     | Causa                                                                                  |
|--------|--------|----------------------------------------------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou o autor da lista                                                      |
| `403`  | ❌     | Usuário está bloqueado pelo autor da lista, a lista é "privada demais" para o usuário  |
| `404`  | ✅     | Lista não encontrada                                                                   |
| `500`  | ❌     | Erro interno                                                                           |  

---

## PUT `/lists/{list_id}` — Editar lista

Atualiza os dados de uma lista do usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.
- Se a privacidade da lista subir, todos os usuários que salvaram a lista e estiverem abaixo dessa nova privacidade terão a lista removida da sua biblioteca.
- Até os campos inalterados precisam ser enviados.
- As listas **Jogos Favoritos** e **Jogos Completados** são imutáveis em nome e descrição, podendo mudar apenas a privacidade delas.

### Path Parameter

| Parâmetro       | Tipo   | Descrição                         |
|-----------------|--------|-----------------------------------|
| `list_id`       | string | ID da lista a ser editada         |

### Request Body

```json
{
  "name": "string",
  "description": "string" | null,
  "privacy": 0
}
```

| Campo         | Tipo    | Obrigatório | Regras                                                    |
|---------------|---------|-------------|-----------------------------------------------------------|
| `name`        | string  | ✅          | Máximo de 45 caracteres, único por usuário                |
| `description` | string  | ✅          | Máximo de 300 caracteres                                  |
| `privacy`     | int     | ✅          | Deve ser um dos valores dispostos na seção de privacidade |

### Resposta de Sucesso — `200`

Retorna schema **\_\_LIST_FULL\_\_**

### Erros possíveis

| Status | HR     | Causa                                       | 
|--------|--------|---------------------------------------------|
| `400`  | ✅     | Nome ou descrição acima do limite           |
| `401`  | ✅     | Usuário não autenticado                     |
| `403`  | ❌     | O usuário não é autor da lista, o usuário está tentando editar o nome ou a descrição das listas padrão |
| `404`  | ✅     | Lista não encontrada                        |
| `406`  | ❌     | A privacidade não é um dos valores válidos  |
| `409`  | ✅     | Novo nome já está em uso pelo usuário       |
| `500`  | ❌     | Erro interno                                | 

---

## DELETE `/lists/{list_id}` — Deletar lista

Deleta uma lista do usuário autenticado. 

**Regras e comportamentos:**
- **Requer login**.
- As listas **Jogos Favoritos** e **Jogos Completados** não podem ser deletadas.
- A lista será removida de todas as bibliotecas de usuários que salvaram ela.

### Path Parameter

| Parâmetro   | Tipo   | Descrição                      |
|-------------|--------|--------------------------------|
| `list_id`   | string | ID da lista a ser deletada     |

### Resposta de Sucesso — `200`

```json
{"message": "Lista deletada com sucesso!"}
```

### Erros possíveis


| Status | HR     | Causa                                                                            |
|--------|--------|----------------------------------------------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                                                          |
| `403`  | ❌     | O usuário não é autor da lista, o usuário está tentando deletar as listas padrão |
| `404`  | ✅     | Lista não encontrada                                                             |
| `500`  | ❌     | Erro interno                                                                     | 

---

## GET `/lists/created/{user_id}` — Busca as listas criadas pelo usuário

Busca as listas criadas por um usuário específico.

**Regras e comportamentos:**
- **Não requer login**.
- As listas que são muito privadas para o usuário que está buscando não serão enviadas no content, e nem contarão para o total.

### Path Parameter

| Parâmetro |  Tipo  | Descrição                                         |
|-----------|--------|---------------------------------------------------|
| `user_id` | string | ID do usuário cujas listas criadas serão buscadas |

### Query Parameters (Paginação)

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis nomes da listas criadas pelo usuário
- order padrão é `-updated_at`, que mostra as listas editadas mais recentemente. Os orders possíveis são: `["created_at", "-created_at", "name", "-name", "updated_at", "-updated_at"]`.

### Resposta de Sucesso - `200`

Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas **\_\_LIST\_\_**.

### Erros possíveis

| Status | HR     | Causa                                           |
|--------|--------|-------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou o autor das listas             |
| `403`  | ❌     | O usuário está bloqueado pelo autor das listas  |
| `404`  | ✅     | O usuário criador das listas não foi encontrado |
| `406`  | ❌     | Query parameters presentes, porém inválidos                      |
| `500`  | ❌     | Erro interno                                    | 

---

## POST `/lists/save/{list_id}` — Salvar lista

Salva a lista de outro usuário na biblioteca do autenticado.

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado já tiver salvado a lista, a rota não irá incluir novamente no DB, mas também não irá levantar erro (idempotência)

### Path Parameters

| Parâmetro      | Tipo   | Descrição                      |
|----------------|--------|--------------------------------|
| `list_id`      | string | ID da lista a ser salva        |

### Resposta de Sucesso — `200`

```json
{"message": "Lista salva com sucesso!"}
```

### Erros possíveis


| Status | HR     | Causa                                                                                   |
|--------|--------|-----------------------------------------------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou o autor da lista                                                       |
| `401`  | ✅     | Usuário não autenticado                                                                 |
| `403`  | ❌     | O usuário está bloqueado pelo autor da lista, a lista é "privada demais" para o usuário |
| `404`  | ✅     | Lista não encontrada                                                                    |
| `500`  | ❌     | Erro interno                                                                            | 

---

## DELETE `/lists/save/{list_id}` — Remover lista salva

Remove uma lista previamente salva da biblioteca do usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado não tiver salvado a lista, a rota não irá levantar erro (idempotência).
- Não é possível dessalvar sua própria lista, apenas deletá-la.

### Path Parameters

| Parâmetro      | Tipo   | Descrição                            |
|----------------|--------|--------------------------------------|
| `list_id`      | string | ID da lista a ser removida           |

### Resposta de Sucesso — `200`

```json
{"message": "Lista dessalva com sucesso!"}
```

### Erros possíveis


| Status | HR     | Causa                                         |
|--------|--------|-----------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                       |
| `403`  | ❌     | Usuário tentando dessalvar sua própria lista  |
| `404`  | ✅     | Lista não encontrada                          |
| `500`  | ❌     | Erro interno                                  |

---

## GET `/lists/save` — Buscar listas salvas

Busca de forma paginada as listas que foram salvas na biblioteca do usuário autenticado.

**Regras e Comportamentos:**
- **Requer login**.
- Inclui as listas que o próprio usuário autenticado criou e as listas padrão **Jogos Favoritos** e **Jogos Completados**.

### Query Parameters (Paginação)

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis nomes da listas salvas pelo usuário
- order padrão é `-created_at`, que mostra as mais recém salvas listas. Os orders possíveis são: `["created_at", "-created_at", "name", "-name"]`.

### Resposta de Sucesso — `200`

Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas **\_\_LIST\_\_**.

### Erros possíveis

| Status | HR     | Causa                         |
|--------|--------|-------------------------------|
| `401`  | ✅     | Usuário não autenticado       |
| `406`  | ❌     | Query parameters presentes, porém inválidos    |
| `500`  | ❌     | Erro interno                  |

---

## POST `/lists/game/{list_id}/{game_id}` — Adicionar jogo à lista

Adiciona um jogo a uma lista do usuário autenticado. 

**Regras e comportamentos:**
- **Requer login**.
- Se o usuário autenticado já tiver adicionado esse game à lista, a rota **irá** levantar erro.
- Para as listas **Jogos Completados** e **Jogos Favoritos**, não é possível adicionar jogos usando essa rota, apenas ao criar ou editar reviews com os parâmetros `completed` e `liked`, marcando-os como verdadeiros, respectivamente.

### Path Parameters

| Parâmetro   | Tipo   | Descrição                                  |
|-------------|--------|--------------------------------------------|
| `list_id`   | string | ID da lista que receberá o jogo            |
| `game_id`   | int    | ID do jogo a ser adicionado                |

### Resposta de Sucesso — `200`

```json
{"message": "Game adicionado à lista com sucesso!"}
```

### Erros possíveis

| Status | HR     | Causa                                                               |
|--------|--------|---------------------------------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                                             |
| `403`  | ❌     | Falta de propriedade da lista, tentando adicionar às listas padrão  |
| `404`  | ✅     | Lista não encontrada, game não encontrado (game_id inválido!)       |
| `409`  | ✅     | O jogo já pertence a lista                                          |
| `500`  | ❌     | Erro interno                                                        |

---

## DELETE `/lists/game/{list_id}/{game_id}` — Remover jogo da lista

Remove um jogo de uma lista do usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.
- Se o game não pertencer a lista, a rota não irá levantar erro (idempotência). Para as listas **Jogos Completados** e **Jogos Favoritos**, não é possível remover jogos usando essa rota, apenas ao editar reviews com os parâmetros `completed` e `liked` marcando-os como falso, respectivamente, ou ao deletar a review em que esses parâmetros estavam marcados como verdadeiros.

### Path Parameters

| Parâmetro   | Tipo   | Descrição                                  |
|-------------|--------|--------------------------------------------|
| `list_id`   | string | ID da lista da qual o jogo será removido   |
| `game_id`   | int    | ID do jogo a ser removido                  |

### Resposta de Sucesso — `200`

```json
{"message": "Game removido da lista com sucesso!"}
```

### Erros possíveis

| Status | HR     | Causa                                                               |
|--------|--------|---------------------------------------------------------------------|
| `401`  | ✅     | Usuário não autenticado                                             |
| `403`  | ❌     | Falta de propriedade da lista, tentando remover das listas padrão   |
| `404`  | ✅     | Lista não encontrada, game não encontrado (game_id inválido!)       |
| `500`  | ❌     | Erro interno                                                        |

---

## GET `/lists/game/{list_id}` — Busca os games que pertencem a uma lista

Busca de forma paginada os jogos que pertencem a uma lista específica. 

**Regras e comportamentos:**
- **Não requer login**

### Path Parameter

| Parâmetro | Tipo   | Descrição         |
|-----------|--------|-------------------|
| `list_id` | string | ID único da lista |

### Query Parameters (Paginação)

**\_\_PAGE_QUERY\_\_**:
- search busca por possíveis titulos de games que pertencem a lista
- order padrão é `-created_at`, que mostra as mais recém inclusos games à lista. Os orders possíveis são: `["created_at", "-created_at", "title", "-title"]`.

### Resposta de Sucesso — `200`

Retorna schema **\_\_PAGE_RESULT\_\_**, onde o content é uma lista de schemas **\_\_GAME\_\_**.

### Erros possíveis

| Status | HR     | Causa                                                                          |
|--------|--------|--------------------------------------------------------------------------------|
| `400`  | ✅     | Usuário bloqueou autor da lista                                                |
| `403`  | ❌     | Usuário bloqueado pelo autor da lista, lista é "privada demais" para o usuário |
| `404`  | ✅     | Lista não encontrada                                                           |
| `406`  | ❌     | Query parameters presentes, porém inválidos                                                     |
| `500`  | ❌     | Erro interno ao buscar os jogos da lista                                       |

---