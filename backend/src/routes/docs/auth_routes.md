# 📡 Documentação das Rotas de Autenticação


## Sumário

- [POST `/auth/login/`](#post-authlogin---login)
- [POST `/auth/logout/`](#post-authlogout---logout)

---

## POST `/auth/login/` — Login

Autentica o usuário com email ou username e senha. Não requer autenticação prévia.

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

| Status | Causa                              |
|--------|------------------------------------|
| `400`  | Conta não encontrada, senha incorreta |
| `500`  | Erro interno ao buscar os dados    |

---

## POST `/auth/logout/` — Logout

Encerra a sessão do usuário removendo os cookies de autenticação. Não requer autenticação.

### Resposta de Sucesso — `200`

```json
{
  "message": "Log Out"
}
```

Os cookies `access-token` e `refresh-token` são deletados automaticamente na resposta.

---

## 🔐 Autenticação

Certifique-se de que as requisições são feitas com `credentials: 'include'` (fetch) ou `withCredentials: true` (axios) para que os cookies sejam enviados e recebidos corretamente.

```js
// Login com fetch
fetch('/auth/login/', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email_or_username: '...', password: '...' })
})

// Logout com axios
axios.post('/auth/logout/', {}, { withCredentials: true })
```

---