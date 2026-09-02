# 🧐 src/middlewares/user_states.py


## 📈 Funções principais
- Analisar os cookies dos usuários que estão fazendo alguma chamada ao backend para definir se eles já fizeram o login, não fizeram login ou se o login expirou.

## ⚙️ Tecnologias utilizadas
- [FastAPI/Starlette (Python)](https://starlette.dev/middleware/#basehttpmiddleware)
- [jose (Python)](https://youtube.com/playlist?list=PLpdAy0tYrnKy3TvpCT-x7kGqMQ5grk1Xq&si=QLnk9gcBu543ayPL)

## A classe SetUserLoginState
A classe SetUserLoginState é um middleware que avalia e armazena o status do login do usuário no request.state, o qual será depois desempacotado pela dependency require_login nas rotas
