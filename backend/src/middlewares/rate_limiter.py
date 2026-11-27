import threading
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class TokenBucket:
    """
    Balde de token para rate limiter

    Cada balde começa cheio com 'max_tokens' e realiza o refill de 'refill_rate' 
    tokens a cada 'interval' segundos, até a capacidade máxima.
    """

    def __init__(self, max_tokens: int, refill_rate: int, interval: float):
        """
        Inicializa um novo balde de tokens.

        :param max_tokens: Número máximo de tokens que o balde pode possuir.
        :param refill_rate: Número de tokens adicionado por intervalo de refil.
        :param interval: Tempo em segundos entre refills.
        """
        assert max_tokens > 0, "max_tokens deve ser positivo"
        assert refill_rate > 0, "refill_rate deve ser positivo"
        assert interval > 0, "interval deve ser positivo"

        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.interval = interval

        self.tokens = max_tokens
        self.refilled_at = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        """Adiciona tokens baseado no tempo que passou desde o último refill."""
        now = time.time()
        elapsed = now - self.refilled_at

        if elapsed >= self.interval:
            num_refills = int(elapsed // self.interval)
            self.tokens = min(
                self.max_tokens,
                self.tokens + num_refills * self.refill_rate
            )
            # Avança o timestamp pelo número de intervalos completos consumidos, 
            # para que os intervalos parciais não sejam perdidos.
            self.refilled_at += num_refills * self.interval

    def allow_request(self, tokens: int = 1) -> bool:
        """
        Tentativa de consumir 'tokens' do balde.

        Retorna True se é permitido e falso se o balde não possui tokens.
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_remaining(self) -> int:
        """Retorna a quantidade que sobra no balde de tokens"""
        with self.lock:
            self._refill()
            return self.tokens

    def get_reset_time(self) -> float:
        """Retorna o timestamp Unix de quando vai ser o próximo refill."""
        with self.lock:
            return self.refilled_at + self.interval



class RateLimiterStore:
    """
    Manuseia o balde de tokens por usuário.

    Cada chave única de usuário tem seu próprio balde
    com parâmetros idênticos (nosso caso é por IP).
    """

    def __init__(self, max_tokens: int, refill_rate: int, interval: float):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.interval = interval
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def get_bucket(self, key: str) -> TokenBucket:
        """
        Retorna o TokenBucket para uma chave de cliente dada.
        Cria um novo balde se ainda não existir um.
        """
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(
                    max_tokens=self.max_tokens,
                    refill_rate=self.refill_rate,
                    interval=self.interval,
                )
            return self._buckets[key]

        
class RateLimiter(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_tokens: int = 10,
        refill_rate: int = 2,
        interval: float = 1.0,
    ):
        super().__init__(app)
        self.store = RateLimiterStore(
            max_tokens=max_tokens,
            refill_rate=refill_rate,
            interval=interval,
        )


    async def dispatch(self, request: Request, call_next):
        """
        Middleware que coloca o limite de requests por IP, devolvendo um JSON com o tempo que falta para a próxima atualização.

        """
        # Identifica o IP do cliente
        client_ip = request.client.host if request.client else "unknown"
        bucket = self.store.get_bucket(client_ip)

        # Verifica se o cliente possui requests possíveis
        if not bucket.allow_request():
            retry_after = bucket.get_reset_time() - time.time()
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Try again later."},
                headers={
                    "Retry-After": str(max(1, int(retry_after))),
                    "X-RateLimit-Limit": str(bucket.max_tokens),
                    "X-RateLimit-Remaining": str(bucket.get_remaining()),
                    "X-RateLimit-Reset": str(int(bucket.get_reset_time())),
                },
            )

        # Request é permitida. Processa e coloca os headers na resposta.
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(bucket.max_tokens)
        response.headers["X-RateLimit-Remaining"] = str(bucket.get_remaining())
        response.headers["X-RateLimit-Reset"] = str(int(bucket.get_reset_time()))
        return response
