from dataclasses import dataclass

@dataclass
class DB_Result():
    success: bool
    message: str