# 📡 Documentação das Rotas de Autenticação


## Sumário

- [POST `/auth/login` — Login](#post-authlogin--login)
- [DELETE `/auth/login` — Logout](#delete-authlogin--logout)
- [GET `/auth/me` — Identificação](#get-authme--identificação)

---

## POST `/auth/login` — Login

Autentica o usuário com email ou username e senha. 

**Regras e comportamentos:**
- **Não requer login**. 
- Na resposta, são definidos automaticamente os dois [cookies padrão de autenticação](./routes.md#cookies-de-autenticação).


### Request Body

```json
{
  "email_or_username": "string",
  "password": "string"
}
```

| Campo               | Tipo   | Obrigatório | Descrição                                  |
|---------------------|--------|-------------|--------------------------------------------|
| `email_or_username` | string | ✅          | Email ou username da conta, case-sensitive |
| `password`          | string | ✅          | Senha da conta                             |

### Resposta de Sucesso — `200`

```json
{"message":"Login feito com sucesso!", "user_id": "string"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR (human readable)    | Causa                               |
|--------|------------------------|-------------------------------------|
| `400`  | ✅                     | Conta não existe ou senha incorreta |
| `500`  | ❌                     | Erro interno                        |

---

## DELETE `/auth/login` — Logout

Encerra a sessão do usuário.

**Regras e comportamentos:**
- **Não requer login**.
- Se o usuário não estiver logado, não irá levantar erro (idempotência).
- Os [cookies padrão de autenticação](./routes.md#cookies-de-autenticação) são deletados automaticamente na resposta.

### Resposta de Sucesso — `200`

```json
{"message": "Logout feito com sucesso!"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                   |
|--------|--------|-------------------------|
| `500`  | ❌     | Erro interno            |

---

## GET `/auth/me` — Identificação

Retorna o user_id e o email de um usuário autenticado.

**Regras e comportamentos:**
- **Requer login**.


### Resposta de Sucesso — `200`

```json
{"message": "Encontramos o usuário!", "user_id": "string", "email": "string"}
```

### [Erros](./routes.md#erros) possíveis

| Status | HR     | Causa                         |
|--------|--------|-------------------------------|
| `401`  | ✅     | Usuário não autenticado       |
| `500`  | ❌     | Erro interno                  |

