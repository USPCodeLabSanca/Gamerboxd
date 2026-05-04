from dataclasses import dataclass
from typing import Any

@dataclass
class DB_Result():
    success: bool
    message: str = None
    obj: Any = None
    error: Exception = None