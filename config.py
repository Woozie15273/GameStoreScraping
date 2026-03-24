from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    BASE_URL: str = "https://sandbox.oxylabs.io/products"
    HEADLESS: bool = True
    MAX_CONCURRENCY = 1
    DEFAULT_CSV_PATH: str = "data/results.csv"
    # Example for Google Sheets
    GSHEET_SCOPES: list = ("https://www.googleapis.com/auth/spreadsheets",)