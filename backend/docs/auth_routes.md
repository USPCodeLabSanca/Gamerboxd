# 📡 Documentação das Rotas de Autenticação


## Sumário

- [POST `/auth/login/`](#post-authlogin---login)
- [DELETE `/auth/login/`](#delete-authlogin---logout)

---

## POST `/auth/login/` — Login

Autentica o usuário com email ou username e senha. **Não requer login**.

### Request Body

```json
{
  "email_or_username": "string",
  "password": "string"
}
```

| Campo               | Tipo   | Obrigatório | Descrição                          |
|---------------------|--------|-------------|------------------------------------|
| `email_or_username` | string | ✅          | Email ou username da conta         |
| `password`          | string | ✅          | Senha da conta                     |

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

Dois cookies `httponly` são definidos automaticamente na resposta:

| Cookie          | Descrição                         |
|-----------------|-----------------------------------|
| `access-token`  | JWT de curta duração (10 minutos) |
| `refresh-token` | JWT de longa duração (24 horas)   |

### Erros possíveis

| Status | Causa                                  |
|--------|----------------------------------------|
| `400`  | Conta não encontrada, senha incorreta  |
| `500`  | Erro interno                           |

---

## DELETE `/auth/login/` — Logout

Encerra a sessão do usuário removendo os cookies de autenticação. **Requer login**.

### Resposta de Sucesso — `200`

```json
{
  "message": "string"
}
```

Os cookies `access-token` e `refresh-token` são deletados automaticamente na resposta.

### Erros possíveis

| Status | Causa                            |
|--------|----------------------------------|
| `401`  | Usuário não autenticado          |
| `500`  | Erro interno ao buscar os dados  |
