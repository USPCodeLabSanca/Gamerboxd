# 📡 Documentação das Rotas de Games

## Sumário

- [GET `/game/{search}`](#get-gamesearch---buscar-games)

---

## GET `/game/{search}` — Buscar games

Busca jogos pelo nome. Não requer autenticação.

### Path Parameter

| Parâmetro | Tipo   | Descrição              |
|-----------|--------|------------------------|
| `search`  | string | Termo de busca do jogo |

### Query Parameters

| Parâmetro   | Tipo | Obrigatório | Padrão | Descrição                           |
|-------------|------|-------------|--------|-------------------------------------|
| `page`      | int  | ❌          | `1`    | Número da página                    |
| `page_size` | int  | ❌          | `20`   | Quantidade de resultados por página |

### Resposta de Sucesso — `200`

```json
{
  "count": 0,
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

| Status | Causa                                    |
|--------|------------------------------------------|
| `500`  | Erro interno ou falha ao buscar os dados |

---