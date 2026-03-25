
---

# Product Scraper – Playwright + Exporter Pipeline

A modular scraping pipeline that extracts product data from [game store](https://sandbox.oxylabs.io/products)
and exports the results into CSV, JSON, or SQLite formats.

The project is fully implemented, tested, and structured for clarity, maintainability, and extensibility.

---

## Project Structure

```
- schemas/
    game_entry.py        # Dataclass representing a structured scraped item
    game_platforms.py    # Supported platform definitions
    search_params.py     # Dataclass for search/filter parameters
    selectors.py         # Playwright CSS selectors

- services/
    exporter.py          # CSV, JSON, SQLite export logic
    scraper.py           # Playwright browser + scraping workflow

- tests/
    test_exporter.py     # Exporter unit tests
    test_scraper.py      # Scraper unit tests

- config.py              # Global constants and default paths
- main.py                # Orchestrates scraping + exporting
- readme.md
- requirements.txt
```

---

## Core Components

### 1. Scraper
The scraper:
- Launches a Playwright browser
- Navigates through product listings
- Extracts structured data into `GameEntry` objects
- Applies filters defined in `SearchParams`

Output:  
A list of validated `GameEntry` dataclass instances.

---

### 2. Exporter

The `Exporter` class receives a list of `GameEntry` objects and provides:

#### Shared Internal Helpers
- `_ensure_data()`  
  Ensures data exists before exporting.

- `_prepare_path(filename, ext)`  
  Builds output paths using `Config.DEFAULT_PATH`.

- `_entries_as_dicts()`  
  Converts dataclasses to dictionaries for serialization.

- `_format_val()`  
  Normalizes parameter values for filenames.

#### Filename Generation
`generate_filename(params: SearchParams)`  
Creates a sanitized, descriptive filename based on search parameters.

---

### 3. Export Formats

#### CSV Export
- Writes rows in dataclass field order
- Uses Python’s built‑in `csv` module
- Async version: `to_csv_async()`

#### JSON Export
- Serializes using `_entries_as_dicts()`
- Pretty‑printed JSON output
- Async version: `to_json_async()`

#### SQLite Export
- Table name: `games`
- Columns match `GameEntry` fields
- Uses parameterized SQL inserts
- Async version: `to_sqlite_async()`

---

## Running the Application

`main.py` orchestrates the full workflow:

1. Load configuration values from `Config`
2. Iterate through each `SearchParams` entry defined in `Config.QUERIES`
3. Run the scraper for each query
4. Pass results to `Exporter`
5. Export to CSV, JSON, or SQLite depending on configuration flags

### Using Configuration

All runtime behavior is controlled through the `Config` dataclass:

- Which URLs to scrape (`BASE_URL`)
- How many concurrent browser contexts to run (`MAX_CONCURRENCY`)
- Where to store exported files (`DEFAULT_PATH`)
- Which export formats to produce (`EXPORT_AS_*`)
- Which sets of filters to run (`QUERIES`)

Each `SearchParams` entry in `Config.QUERIES` results in a separate scrape‑and‑export cycle.

---

## Headless vs Headful Mode

[The target website](sandbox.oxylabs.io/products) does not render correctly when Playwright runs in headless mode.  
For this reason, the scraper is configured to run in **headful mode** by default.  
This behavior is defined in `config.py` and should remain enabled unless the site changes its rendering behavior.

---