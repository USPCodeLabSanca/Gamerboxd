import math
import requests
from .utils import BaseUser


def get_page(user: BaseUser, url: str, total: int, page_size: int):
    """Realiza alguns testes de sanidade sobre as variáveis da página e depois retorna o conteúdo da página"""

    response = requests.get(url, cookies = user.cookies)
    assert response.status_code == 200, response.json()
    assert response.json()["total"] == total, response.json()
    assert response.json()["page_len"] <= page_size, response.json()
    assert response.json()["page_len"] == len(response.json()["content"]), response.json()
    assert response.json()["current_url"] == url, response.json()

    return response.json()["next_url"], response.json()["content"]


def queries_tests(subtests, user: BaseUser, url: str):
    """Testa que a API está validando os query parameters enviados antes de passar para a rota"""

    bad_queries = ["?order=errado", "?page_size=-1", "?page_size=100"]

    for bq in bad_queries:
        with subtests.test(msg=f"Testing bad query: {bq}"):
            wrong_url = url + bq
            response = requests.get(wrong_url, cookies = user.cookies)
            assert response.status_code == 422, response.json()
            if "order" in bq:
                assert response.json() == {"message": "Método de ordenação inválido!"}, response.json()

            elif "page_size":
                assert response.json() == {"message": "O tamanho da página tem que estar entre 1 e 50!"}, response.json()


def content_tests(user: BaseUser, url: str, seed, total: int, page_size: int):
    """Testa que a API está retornando a quantidade registros esperados e que seus campos também sigam o esperado"""

    seed.cleanup()      # Apaga os registros criados pelo último teste
    seed(user, total)   # Cria registros que esperamos encontrar nesse teste
    
    current = url + f"?page_size={page_size}"
    num_pages = math.ceil(total/page_size)
    pages_seen = 0

    # Itera por todas as páginas de dados
    while (pages_seen < num_pages):
        current, content = get_page(user, current, total, page_size)
        pages_seen += 1
        for c in content:
            assert sorted(c.keys()) == sorted(seed.expected_content), (c.keys(), seed.expected_content)

    assert current is None


def order_tests(subtests, user: BaseUser, url: str, seed, total: int, page_size: int):
    """Testa que a ordenação dos registros adicionados estão como esperado nas páginas de resposta da API"""

    all_orders = ["!" + ord for ord in seed.valid_orders] + seed.valid_orders + [""]

    for order in all_orders:
        received_records = []
        with subtests.test(msg=f"Testing order: {order}"):
            seed.cleanup()                                      # Apaga os registros criados pelo último teste
            expected_records = seed(user, total, order=order)   # Cria registros que esperamos encontrar nesse teste
            current = url + f"?page_size={page_size}"
            if len(order) != 0:
                current += f"&order={order}"
            num_pages = math.ceil(total/page_size)
            pages_seen = 0

            # Itera por todas as páginas de dados
            while (pages_seen < num_pages):
                current, content = get_page(user, current, total, page_size)
                pages_seen += 1

                for c in content:
                    assert c[seed.return_obj] not in received_records, received_records
                    if (not hasattr(seed, "ignore")) or (c[seed.return_obj] not in seed.ignore):
                        received_records.append(c[seed.return_obj])

            assert current is None
            assert received_records == expected_records, (received_records, expected_records)


def search_tests(subtests, user: BaseUser, url: str, seed, total: int, page_size: int):
    """Testa que buscar por registros adicionados retorna como esperado nas páginas de resposta da API"""

    for search in seed.searches:
        received_records = []
        with subtests.test(msg=f"Testing search {search}",):

            seed.cleanup()                                          # Apaga os registros criados pelo último teste                    
            expected_records = seed(user, total, search=search)     # Cria registros que esperamos encontrar nesse teste
            
            current = url + f"?page_size={page_size}&search={search}"
            num_pages = math.ceil(total/page_size)
            pages_seen = 0

            # Itera por todas as páginas de dados
            while (pages_seen < num_pages):
                current, content = get_page(user, current, total, page_size)
                pages_seen += 1

                for c in content:
                    assert c[seed.return_obj] not in received_records, received_records
                    if (not hasattr(seed, "ignore")) or (c[seed.return_obj] not in seed.ignore):
                        received_records.append(c[seed.return_obj])

            assert current is None
            assert received_records == expected_records, (received_records, expected_records)