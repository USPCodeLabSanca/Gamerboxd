# 🛣️ tests/

## 📈 Funções principais
- Definir testes unitários para verificar as rotas do backend

## ⚙️ Tecnologias utilizadas
- [Pytest (Python)](https://docs.pytest.org/en/stable/)

## Testes unitários
Testes unitários são códigos que validam software "aos poucos". O intuito é isolar os diferentes pedacinhos que compõe uma aplicação, e verificar se cada módulo está se comportando como esperado pelo desenvolvidor. Para o Gamerboxd, isso significa que estamos testando majoritariamente a atuação das rotas, o que inclui na maioria dos casos validar:
- Os códigos https de retorno;
- Os schemas retornados;
- O tratamento de erros;
- As regras de negócio.

## Usando o pytest
O pytest é uma biblioteca voltada para testes unitários de software. Usando-a, podemos escrever funções que fazem chamadas às rotas do backend e comparam o que ele retorna ao que queremos que ele retorne. É como se fosse um run.codes onde nós somos responsáveis por escrever os casos de teste. Para isso, o pytest depende de uma estrutura lógica do python: o **assert**.

### assert em python
O assert pode ser basicamente traduzido para a frase "me garanta". Você passa tanto o retorno da função ou do módulo que esta testando para assert quanto o retorno desejado, usando o operador ==:

```python
    def my_sum_function(a, b)
        """Recebe 2 numeros e o soma"""
        return a + b

    def test_sum_function():
        """Soma de 2 números"""

        a = 1
        b = 2
        c = my_sum_function(a, b)

        assert c == 3   # Isso diz pro pytest: "me garanta que o valor de c é o int 3". Esse teste dá certo!
        assert c == 4   # Isso diz pro pytest: "me garanta que o valor de c é o int 4". Esse teste dá errado!
```

Nem sempre queremos que o código testado funcione. Podemos verificar se o tratamento de erros de uma função vai parar a execução antes que erros do usuário se propaguem para camadas mais profundas do código.

```python
    def my_int_sum_function(a, b)
        """Recebe 2 valores, verifica se são inteiros, e os soma"""

        if (type(a) != int) or (type(b) != int)
            return None

        return a + b

    def test_sum_function_passing_string():
        """Soma de uma string de numero e um int"""

        a = "1"
        b = 2
        c = my_int_sum_function(a, b)

        assert c == None    # Isso diz pro pytest: "me garanta que o valor de c é None". Esse teste dá certo!
        assert c == 3       # Isso diz pro pytest: "me garanta que o valor de c é o int 3". Esse teste dá errado!
```

Note que nos 2 exemplos a função de teste começa com test_*. Isso é necessário para o pytest saber quais são as funções com testes que precisam ser rodadas. Os arquivos onde essas funções 

Para testes de códigos mais complexos, como o nosso backend, é necessário "deixar coisas prontas" antes de escrever um 



