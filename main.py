import asyncio
import logging

from services import Scraper, Exporter
from schemas import SearchParams
from config import Config

async def _process_query(scraper: Scraper, params: SearchParams):
    logging.info(f"Running query: {params}")

    results = await scraper.run(params)
    exporter = Exporter(results)
    filename = exporter.generate_filename(params)

    export_tasks = []

    if Config.EXPORT_AS_CSV:
        export_tasks.append(exporter.to_csv_async(filename))
    if Config.EXPORT_AS_JSON:
        export_tasks.append(exporter.to_json_async(filename))
    if Config.EXPORT_AS_SQLITE:
        export_tasks.append(exporter.to_sqlite_async(filename))

    for task in export_tasks:
        await task

    logging.info(f"Finished exporting for query: {params}")


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    queries = Config.QUERIES

    async with Scraper(
        headless=False,
        max_concurrency=Config.MAX_CONCURRENCY
    ) as scraper:

        for params in queries:
            await _process_query(scraper, params)

    logging.info("All queries completed.")


if __name__ == "__main__":
    asyncio.run(main())
