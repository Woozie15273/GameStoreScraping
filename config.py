from pathlib import Path
from dataclasses import dataclass
from schemas import SearchParams, Platforms

@dataclass(frozen=True)
class Config:
    BASE_URL: str = "https://sandbox.oxylabs.io/products"
    MAX_CONCURRENCY = 1
    DEFAULT_PATH: Path = Path("data")
    EXPORT_AS_CSV: bool = True
    EXPORT_AS_JSON: bool = False
    EXPORT_AS_SQLITE: bool = False

    # List of SearchParams directly in Config
    QUERIES = [
        SearchParams(
            platform=Platforms.PC,
            name=None,
            genre=["Role-Playing"],
            rating_min=3.0,
            rating_max=None,
            price_min=None,
            price_max=85.00,
            in_stock=False
        ),
        SearchParams(
            platform=Platforms.WII,
            name=None,
            genre=["Action"],
            rating_min=4.0,
            rating_max=None,
            price_min=None,
            price_max=90.00,
            in_stock=True
        ),
        # Add more SearchParams here
    ]