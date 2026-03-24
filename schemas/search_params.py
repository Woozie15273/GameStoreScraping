from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchParams:
    platform: Optional[str] = None
    name: Optional[str] = None
    genre: Optional[list[str]] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    in_stock: Optional[bool] = None
