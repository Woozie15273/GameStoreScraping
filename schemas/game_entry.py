from dataclasses import dataclass

@dataclass
class GameEntry:
    platform: str
    name: str
    genre: str
    rating: float
    price: float
    status: str