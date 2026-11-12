# 🧐 src/middlewares/user_states.py


## 📈 Funções principais
- Analisar os cookies dos usuários que estão fazendo alguma chamada ao backend para definir se eles já fizeram o login, não fizeram login ou se o login expirou.
- Definir o tempo máximo que uma rota pode demorar para responder (timeout).

## ⚙️ Tecnologias utilizadas
- [FastAPI/Starlette (Python)](https://starlette.dev/middleware/#basehttpmiddleware)
- [jose (Python)](https://youtube.com/playlist?list=PLpdAy0tYrnKy3TvpCT-x7kGqMQ5grk1Xq&si=QLnk9gcBu543ayPL)

## A classe SetUserLoginStateMiddleware
A classe SetUserLoginStateMiddleware é um middleware que avalia e armazena o status do login do usuário no request.state, o qual será depois desempacotado pelas dependências require_login ou optional_login nas rotas.

## A classe TimeoutMiddleware
A classe TimeoutMiddleware é um middleware que só permite que a rota demore 15 segundos para responder o frontend, caso contrário, a execução daquela tarefa será interrompida e será devolvido codgio 504, timeout, para o frontend.
