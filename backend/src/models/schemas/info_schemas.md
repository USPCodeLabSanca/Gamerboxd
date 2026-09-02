# 📜 src/models/schemas

## 📈 Funções principais
- Estruturar modelos para os dados que serão recebidos e enviados pelo backend

## ⚙️ Tecnologias utilizadas
- [FastAPI/Pydantic (Python)](https://fastapi.tiangolo.com/tutorial/extra-models/#multiple-models)


## Os modelos Pydantic (schemas)
Se um endpoint recebe muitos query parameters, é recomendável criar um modelo pydantic que englobe eles. Sem os modelos pydantic, construir os endpoints que recebem muitos query parameters seria algo parecido com isso:

```python


@my_router.get("/compra/cartao")
def example_route(nome: str, num: str, cvc: int, validade: str, valor: float, is_cartao_de_credito: bool):

    compra_deu_certo = efetuar_compra(nome, num, cvc, validade, valor, is_cartao_de_credito)

    if compra_deu_certo == True:
        return JSONResponse({"message": f"Compra no cartao {num} realizada com sucesso"})

    return JSONResponse({"message": "Erro ao realizar compra"})

```

Apesar dessa rota tecnicamente funcionar, o FastAPI não verifica com tanta robustez se cada um dos parâmetros atende o tipo de variável que foi especificado na declaração da função ou até se todas as variáveis realmente foram enviadas. Além disso, o execesso de variáveis torna o código mais difícil de manter,

Para resolver estes problemas, define-se um modelo pydantic que engloba os query parameters de compra que precisamos, e depois é só especificar que espera-se que todos os dados contidos no modelo Compra sejam enviados para o endpoint 

```python

from pydantic import BaseModel

class Compra(BaseModel):
    nome: str,
    num: str,
    cvc: int,
    validade: str,
    is_cartao_de_credito: bool,
    valor: float


@my_router.get("/compra/cartao")
def example_route(compra: Compra):

    compra_deu_certo = efetuar_compra(compra)

    if compra_deu_certo == True:
        return JSONResponse({"message": f"Compra no cartao {compra.num} realizada com sucesso"})

    return JSONResponse({"message": "Erro ao realizar compra"})

```

Visivelmente o código já está mais facil de acompanhar, e o FastAPI irá verificar os tipos de cada query parameter mais facilmente. 

Suponha agora que existe uma segunda rota que apenas verifica se o cartão é valido ou não, e então é necessário criar um segundo modelo com apenas dados do cartão para evitarmos o excesso de parãmetros como visto antes:


```python

from pydantic import BaseModel

class Cartao(BaseModel):
    nome: str,
    num: str,
    cvc: int,
    validade: str,
    is_cartao_de_credito: bool = True


class Compra(BaseModel):
    nome: str,
    num: str,
    cvc: int,
    validade: str,
    is_cartao_de_credito: bool = True
    valor: float


@my_router.get("/compra/cartao")
def example_route(compra: Compra):

    compra_deu_certo = efetuar_compra(compra)

    if compra_deu_certo == True:
        return JSONResponse({"message": f"Compra no cartao {compra.num} realizada com sucesso"})

    return JSONResponse({"message": "Erro ao realizar compra"})


@my_router.get("/cartao")
def example_route_2(cartao: Cartao):

    cartao_valido = is_card_valid(cartao)

    if cartao_valido == False:
        return JSONResponse({"message": "Cartão invalido"})

    return JSONResponse({"message": "Cartão valido"})
    

```

Nota-se que o modelo Compra é praticamente identico ao modelo Cartao, com excessão do atributo valor. Para evitar repetição desnecessária de código, podemos fazer uma espécie de herança de modelos:

```python

from pydantic import BaseModel

class Cartao(BaseModel):
    nome: str,
    num: str,
    cvc: int,
    validade: str,
    is_cartao_de_credito: bool = True

class Compra(Cartao):
    valor: float

```

Ao passar o Cartao para a classe Compra ao invés do BaseModel, é a mesma coisa de incluir todos os campos do Cartao na Compra que nem estava antes. É possível fazer esse processo de herança várias vezes para compor classes mais complexas.

Resumindo: Os modelos pydantic são classes nas quais os atributos serão convertidos nas chaves dos query parameters enviados e os valores serão checados com o tipo especificado do atributo. 