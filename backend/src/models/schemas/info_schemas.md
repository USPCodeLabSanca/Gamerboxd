# 📜 src/models/schemas

## 📈 Funções principais
- Estruturar modelos para os dados que serão recebidos e enviados pelo backend

## ⚙️ Tecnologias utilizadas
- [Pydantic (Python)](https://fastapi.tiangolo.com/tutorial/extra-models/#multiple-models)

## Os modelos Pydantic (schemas)
Se um endpoint recebe um request_body, é recomendável criar um modelo pydantic para validar eles.

Para resolver estes problemas, define-se um modelo pydantic que engloba os campos que precisamos, e depois é só especificar que a rota recebe o modelo.

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

O FastAPI irá verificar os tipos de cada um dos atributos da classe Compra, então nós podemos focar mais nas regras de negócio do que na validação de entrada. 

Suponha agora que existe uma segunda rota que apenas verifica se o cartão é valido ou não, e então é necessário criar um segundo modelo com apenas dados do cartão:


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
