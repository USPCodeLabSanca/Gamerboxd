import time
import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/docs"
MAX_TOKENS = 10
REFILL_RATE = 2
INTERVAL = 1.0


@pytest.fixture(autouse=True)
def wait_for_bucket_refill():
    """Garante que o balde seja recarregado após cada teste para evitar interferência."""
    yield
    # Aguarda tempo suficiente para o balde encher novamente antes do próximo teste.
    full_refill_time = (MAX_TOKENS / REFILL_RATE) * INTERVAL + 0.5
    time.sleep(full_refill_time)


def test_burst_requests_within_limit_return_200_and_excess_returns_429():
    """Envia 15 requisições rápidas para acionar o rate limit e verifica 200 e 429."""
    results = []

    for _ in range(15):
        response = requests.get(BASE_URL)
        results.append(response)

    allowed = [r for r in results if r.status_code == 200]
    blocked = [r for r in results if r.status_code == 429]

    # As primeiras requisições dentro da capacidade de rajada devem passar.
    assert len(allowed) == MAX_TOKENS
    # As requisições excedentes devem ser bloqueadas com status 429.
    assert len(blocked) == 5

    # Verifica os cabeçalhos padrão de rate limit na resposta bloqueada.
    last_blocked = blocked[-1]
    assert last_blocked.json() == {"detail": "Too many requests. Try again later."}
    assert last_blocked.headers["X-RateLimit-Limit"] == str(MAX_TOKENS)
    assert last_blocked.headers["X-RateLimit-Remaining"] == "0"
    assert "Retry-After" in last_blocked.headers
    assert "X-RateLimit-Reset" in last_blocked.headers


def test_tokens_refill_after_waiting_allows_new_requests():
    """Esgota os tokens, aguarda uma recarga e confirma que novas requisições voltam a funcionar."""
    # Esgota todos os tokens do balde.
    for _ in range(MAX_TOKENS):
        response = requests.get(BASE_URL)
        assert response.status_code == 200

    # Confirma que o balde está vazio e bloqueando requisições.
    blocked_response = requests.get(BASE_URL)
    assert blocked_response.status_code == 429

    # Aguarda 3 segundos para recarregar tokens (3 intervalos * 2 tokens = 6 tokens).
    time.sleep(3.1)

    # Envia requisições após a recarga e confirma que voltam a ser permitidas.
    for _ in range(5):
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        assert "X-RateLimit-Remaining" in response.headers