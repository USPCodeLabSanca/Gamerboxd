# 🧪 tests/

## 📈 Funções principais
- Definir testes unitários para validar o código fonte do backend.

## ⚙️ Tecnologias utilizadas
- [Pytest (Python)](https://docs.pytest.org/en/stable/)

## Testes unitários
Testes unitários são códigos que validam software "aos poucos". O intuito é isolar as diversas partes que compõem uma aplicação, e verificar se cada um deles está se comportando como esperado pelo desenvolvidor. Para o backend do Gamerboxd, isso significa que estamos testando majoritariamente a atuação das rotas, o que geralmente inclui validar:
- As regras de negócio;
- Os códigos e schemas de retorno;
- O tratamento de erros.


## Usando o pytest
O pytest é uma biblioteca voltada para escrever testes unitários de software. Usando-o, podemos escrever funções que fazem chamadas às rotas do backend e comparam o que elas realmente retornam com o que queremos que elas retornem. É como se fosse um run.codes onde nós somos responsáveis por escrever os casos de teste. Para isso, o pytest depende primordialmente da keyword **assert** do python.


### assert em python
O assert pode ser basicamente traduzido para a frase "me garanta que ...". 
Você passa o retorno real do código sendo testado e o retorno desejado, unindo os dois com um operador lógico.

```python
    def my_sum_function(a, b):
        """Recebe 2 numeros e os soma"""
        return a + b

    def test_sum_function():
        """Soma 2 números inteiros"""

        a = 1
        b = 2
        c = my_sum_function(a, b)

        assert c == 3       # Isso diz: "me garanta que o valor de c é 3". Esse assert passa!
        assert c != "3"     # Isso diz: "me garanta que o valor de c não é a str 3". Esse assert passa!
        assert c > 3        # Isso diz: "me garanta que o valor de c é maior que 3". Esse assert não passa!
        assert c < 3        # Isso diz: "me garanta que o valor de c é menor que 3". Esse assert não passa!
```

**Importante:** É necessário que TODOS os asserts numa função de teste sejam satisfeitos para que a gente diga que "o teste passou" (o teste acima, por exemplo, não passou pois 2 asserts falham). Ná hora de mostrar quantos testes passaram, o pytest não conta quantos asserts passaram, mas sim quantas funções de teste tiveram todos os seus asserts satisfeitos. Quando um assert falha, o pytest já encerra a execução daquela função e pula pra próxima, se houver.

Nem sempre queremos que o código testado "funcione". Podemos verificar se o tratamento de erros de uma função vai interromper a execução antes que erros se propaguem para camadas mais profundas do código:

```python
    def my_int_sum_function(a, b):
        """Recebe 2 valores, verifica se são inteiros, e os soma"""

        if (type(a) != int) or (type(b) != int):
            return None

        return a + b

    def test_sum_function_passing_string_returns_None():
        """Soma uma string de numero e um int"""

        a = "1"
        b = 2
        c = my_int_sum_function(a, b)

        assert c == None    # Esse assert passa!
        assert c != 3       # Esse assert passa!
        assert c == 3       # Esse assert não passa!
```

**Importante:** Note que nos 2 exemplos o nome da função de teste começa com test_\*. Isso é necessário para o pytest saber quais são as funções com testes que precisam ser rodadas, fazendo com que, no exemplo acima, o pytest verifique apenas a test_sum_function_passing_string_returns_None e não a my_int_sum_function.
Os nomes dos arquivos onde essas funções estão definidas também precisam seguir o padrão de test_\*.py (*\_test.py também funciona!) para que o pytest identifique que existem testes dentro deles para rodar. E o mesmo segue para pastas de arquivos, todas devem começar com /test_ .
Por causa disso, daqui em diante:
- "função de teste" será abreviada para "test_"
- "arquivo com funções de teste" será abreviado para "test_.py"
- "pasta com arquivos com funções de teste" será abreviado para "/test_"

---
### fixtures

Para testar códigos mais complexos, é necessário "deixar coisas prontas" antes de escrever um test_. Por exemplo, se queremos testar a funcionalidade de editar uma review no banco de dados, é necessário que exista uma conta de usuário ativa, já logada, e uma review que já esteja no db para que possamos começar a codar a parte que testa editar reviews. Se cada um desses tests_ tivesse que criar uma conta de usuário, inserir no db, logar, criar uma review, inserir no db para só aí começar a testar a funcionalidade de edição da review, ocorreria muita repetição de código. A solução do pytest para este problema são os **fixtures**.

Um fixture no pytest é uma função que "deixa pronto" certos dados que iremos reutilizar várias vezes para que os testes se mantenham o mais próximo possível de unitários (isso é, se mantenham validando pequenas porções de código isoladamente). 

```python

@pytest.fixture
def simple_user():
    """Gera um usuário básico"""

    return {"username": "Alice", "email": "alice@gmail.com"}


def test_create_user_with_fixture(simple_user): # Passe o fixture como parâmetro do test_ !!!
    """Cria uma conta no db usando o fixture simple_user"""

    assert simple_user["username"] == "Alice"           # Esse assert passa!
    assert simple_user["email"] == "alice@gmail.com"    # Esse assert passa!

    response = create_user(simple_user) # Cria a conta no backend
    assert response.status_code == 200  # Verifica se deu certo criar a conta (status_code 200 é sucesso)
```

Se o código do backend para inserir contas estiver certo e o simple_user não violar nenhuma regra de negócio, o teste vai passar. Caso contrário, ele irá falhar.

Em muitas situações, é necessário que o fixture não só prepare os dados para serem utilizados pelos tests_, como também trate esses dados após os tests_ rodarem. No exemplo abaixo, temos 2 tests_ que usam o fixture simple_user, o qual não faz nada depois que cada test_ chama ele:

```python

@pytest.fixture
def simple_user():
    """Gera um usuário básico"""

    return {"username": "Alice", "email": "alice@gmail.com"}


def test_create_user(simple_user):
    """Cria uma conta no db"""

    response = create_user(simple_user)
    assert response.status_code == 200

# A partir daqui, já existe no db uma conta atrelada ao username Alice

def test_create_user_again(simple_user):
    """Cria uma conta já usada no db"""

    response = create_user(simple_user)
    assert response.status_code == 200  
```

No excerto acima, se o backend fizer questão que usernames sejam únicos, a test_create_user_again com certeza não vai passar, porque usamos o mesmo usuário (*{"username": "Alice", "email": "alice@gmail.com"}*) duas vezes. Logo, o backend não irá retornar 200 para a segunda função de teste, porque a conta original do simple_user continuou no banco de dados.
Para resolver o problema, usamos no fixture a keyword **yield** do python, que pode ser basicamente traduzida para a frase "empresta ... pros tests_, mas me devolve depois de usar!".

```python

@pytest.fixture
def simple_user():
    """Gera um usuário básico e, se a conta existir no db após o test_ usá-lo, apaga-o"""

    user_account = {"username": "Alice", "email": "alice@gmail.com"}

    yield user_account  # Isso diz "empresta o user_account pros tests_, mas me devolve depois de usar!"

    # A partir daqui, o test_ que chamou a simṕle_user já acabou de rodar, 
    # e podemos fazer o que quisermos com o user_account

    if account_already_exists(user_account) == True:   
        delete_account(user_account)                   


def test_create_user(simple_user):           
    """Cria uma conta no db"""

    response = create_user(simple_user)
    assert response.status_code == 200

# Dessa vez, não vai ser problema usar a simple_user de novo, porque o fixture apagou a
# conta do banco de dados, então o username Alice está vago

def test_create_user_again(simple_user):
    """Cria uma conta no db de novo, mas a antiga já foi apagada pelo fixture"""
    
    response = create_user(simple_user)     
    assert response.status_code == 200      
```

Outro tópico relevante de um fixture é o **scope** dele. O scope é passado como parâmetro ao se usar o decorador do fixture (```@pytest.fixture(scope='...')```) e ele simboliza com qual frequência o fixture vai ser re-rodado.

```python

# Esse fixture vai rodar uma vez para cada test_ (default)
@pytest.fixture(scope='function')
def simple_user_function():
    user_account = {"username": "Alice", "email": "alice@gmail.com"}

    yield user_account

    if account_already_exists(user_account) == True:   
        delete_account(user_account)    

```

Os principais scopes são:

| scope                            | Quando que o fixture é chamado | Quando que o yield retorna pro fixture           |
|----------------------------------|--------------------------------|--------------------------------------------------|
| @pytest.fixture(scope='function')| Uma vez para cada test_        | O que vem depois do yield só vai ser ativado depois do test_ rodar                              |
| @pytest.fixture(scope='module')  | Uma vez para cada test_.py     | O que vem depois do yield só vai ser ativado depois de todos os tests_ definidos no test_.py rodarem                   |
| @pytest.fixture(scope='package') | Uma vez para cada /test_       | O que vem depois do yield só vai ser ativado depois de todos os tests_ definidos nos tests_.py dentro de /test_ rodarem |
| @pytest.fixture(scope='session') | Uma vez para todos os tests_   | O que vem depois do yield só vai ser ativado depois de todos os tests_ rodarem                                          |

Abordamos até aqui apenas a ponta do iceberg do que é possível com os fixtures do pytest, o que basta para entender sua implementação nos testes do Gamerboxd. É recomendável pesquisar mais afundo sobre seus usos pois tem muita coisa legal que dá para fazer!

---
### conftest.py
Imagine que o nosso projeto obedece a seguinte organização de arquivos:

```text
my_project/
├── src/
│   ├── frontend.py
│   └── backend.py
└── tests/
    ├── test_frontend/
    |   ├── test_buttons.py
    │   └── test_sliders.py
    └── test_backend/
        ├── test_routes.py
        └── test_security.py
```

Caso exista um fixture que todos os tests_.py precisam usar, uma maneira de fazer seria definir o fixture no começo de cada um desses tests_.py, o que não é uma boa prática de programação por causa da repetição de código. Outra forma é criar um arquivo utils.py, definir o fixture uma vez nele e importar esse utils.py para cada um dos tests_.py, o que já é bem melhor do que a ideia anterior. Ainda assim, o pytest tem um modo ainda mais otimizado de implementar esse código: usar o **conftest.py**.

Um arquivo conftest.py é uma evolução do utils.py, de maneira que o pytest já sabe que deve procurar por um e importá-lo para dentro dos tests_.py, não sendo necessário incluir `import conftest.py` para aproveitar dos fixtures ali definidos. A estrutura dos nossos arquivos se tornou então:

```text
my_project/
├── src/
│   ├── frontend.py
│   └── backend.py
└── tests/
    ├── conftest.py
    ├── test_frontend/
    |   ├── test_buttons.py
    │   └── test_sliders.py
    └── test_backend/
        ├── test_routes.py
        └── test_security.py
```

Dessa maneira, os 4 tests_.py podem acessar os fixtures definidos em conftest.py sem a necessidade de importar explicitamente essas funções.

Imagine agora que /test_backend precisa de alguns outros fixtures que são desnecessários para /test_frontend, e vice-versa. O pytest permite que criemos conftest.py para essas subpastas também:

```text
my_project/
├── src/
│   ├── frontend.py
│   └── backend.py
└── tests/
    ├── conftest.py
    ├── test_frontend/
    |   ├── conftest.py
    |   ├── test_buttons.py
    │   └── test_sliders.py
    └── test_backend/
        ├── conftest.py
        ├── test_routes.py
        └── test_security.py
```

Se existir um fixture em test_backend/conftest.py com o mesmo nome que um fixture em tests/conftest.py, os test_.py irão sempre usar o fixture do conftest.py mais próximo hierarquicamente, nesso caso o test_backend/conftest.py. Também não é possivel que um test_.py use um conftest.py de uma subpasta, eles olham apenas para os conftest.py em pastas pai ou na mesma pasta.

**Importante:** Os conftest.py não substituem completamente os arquivos utilitários!!! Eles servem apenas para facilitar a importação de features do pytest, como fixtures entre outras coisas, mas para helper functions, constantes globais ou classes de dados, ainda é necessário usar a modularização clássica do python, com arquivos utils.py e import.

---
### Rodando o pytest
O pytest tem uma CLI bem fácil de usar. Para rodar:

- Todos tests_, use o comando `pytest`;
- Os tests_ de apenas um test_.py, use o comando `pytest path/to/test_name_of_file.py`
- Um único test_, use o comando `pytest path/to/test_name_of_file.py::test_name_of_function`
- Os tests_ em modo verboso (mais detalhado sobre o que está dando certo e errado), use o comando `pytest -v`

O pytest também possui uma feature chamada hooks, que permite que customize melhor esses comandos para a ssua aplicação em específico.

---
### Últimas dicas

- Seja sempre bem explícito com os nomes dos tests_, mesmo que eles fiquem longos.

```python
# Nomes bons!
def test_creating_account_with_repeated_username_returns_400():
def test_following_same_user_twice_returns_ok_message():

# Nomes ruins!
def test_repeat_name():
def test_follow_twice():
```

