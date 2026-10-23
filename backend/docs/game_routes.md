# 📡 Documentação das Rotas de Games


## Sumário

- [GET `/games` — Buscar games](#get-games--buscar-games)

---

## GET `/games` — Buscar games

Busca jogos pelo nome. 

**Regras e comportamentos:**
- **Não requer login**.


### Query Parameters

| Parâmetro   | Tipo   | Obrigatório | Padrão | Descrição                                   |
|-------------|--------|-------------|--------|---------------------------------------------|
| `search`    | string | ✅          | -      | Termo de busca para os jogos                |
| `page`      | int    | ❌          | `1`    | Número da página                            |
| `page_size` | int    | ❌          | `20`   | Quantidade máxima de resultados por página  |
| `detail`    | bool   | ✅          | -      | Quanto de detalhe (**\_\_GAME\_\_** ou **\_\_GAME_FULL\_\_**) a resposta terá |

### Resposta de Sucesso — `200`

```json
{
  "total": 0,   // Total de games que a API tem para essa busca
  "count": 0,   // Quantos games estão indo nessa página
  "games": [
    if (detail == true):
      __GAME_FULL__ 

    else:
      __GAME__
  ]
}
```

### Erros possíveis

| Status | HR    | Causa                 |
|--------|-------|-----------------------|
| `500`  |❌     | Erro interno          |
| `502`  |❌     | Falha da API de games |

---