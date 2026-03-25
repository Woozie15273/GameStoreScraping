import asyncio
from playwright.async_api import async_playwright, Playwright, Browser, Page, Locator
from schemas import SearchParams, GameEntry, Selectors
from config import Config
import logging

class Scraper:
    def __init__(self, headless: bool = True, max_concurrency: int = 1):
        self.headless = headless
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def __aenter__(self):
        logging.debug("Starting Playwright...")
        self._playwright = await async_playwright().start()
        logging.debug("Launching browser (headless=%s)...", self.headless)
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless
        )
        logging.info("Browser launched successfully.")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logging.debug("Closing browser and Playwright...")
        if self._browser:
            await self._browser.close()
            logging.debug("Browser closed.")
        if self._playwright:
            await self._playwright.stop()
            logging.debug("Playwright stopped.")

    async def run(self, params: SearchParams) -> list[GameEntry]:
        async with self.semaphore:
            context = await self._browser.new_context()
            page = await context.new_page()
            logging.debug("Navigating to base URL: %s", Config.BASE_URL)
            await page.goto(Config.BASE_URL)
            entries = await self._search_and_scrape(page, params)
            logging.info("Scraped %d entries.", len(entries))
            await context.close()
            logging.debug("Context closed.")
            return entries

    async def _search_and_scrape(self, page: Page, params: SearchParams) -> list[GameEntry]:
        logging.debug("Starting scrape loop with params: %s", params)
        results: list[GameEntry] = []

        if params.platform:
            logging.debug("Filtering by platform: %s", params.platform)
            await self._goto_filtered_platform(page, params.platform)
        if params.name:
            logging.debug("Searching by name: %s", params.name)
            await self._search_by_name(page, params.name)

        while True:
            cards = page.locator(Selectors.product_card_selector)
            await cards.first.wait_for()
            count = await cards.count()
            logging.debug("Found %d product cards on page.", count)

            for i in range(count):
                try:
                    entry: GameEntry = await GameParser.from_locator(cards.nth(i))
                    if self._matches_criteria(entry, params):
                        if params.platform: entry.platform = params.platform
                        results.append(entry)
                except Exception as e:
                    logging.debug("Failed to parse card %d: %s", i, e)
                    continue

            next_btn = page.locator(Selectors.next_page_selector)
            is_disabled = "disabled" in (await next_btn.get_attribute("class") or "")
            if await next_btn.count() == 0 or is_disabled:
                logging.debug("No next page available. Ending pagination.")
                break
            
            logging.debug("Navigating to next page...")
            current_url = page.url
            await next_btn.click()
            await page.wait_for_function(
                "url => window.location.href !== url",
                arg=current_url
            )
        
        logging.info("Scraping complete. Total entries matched: %d", len(results))
        return results

    # --- Navigation Helpers ---
    async def _search_by_name(self, page: Page, name: str):
        logging.debug("Typing search query: %s", name)
        await page.locator(Selectors.search_input_selector).type(name)
        await page.locator(Selectors.exec_search_selector).click()
        await page.wait_for_load_state("networkidle")

    async def _expand_platform_collapsibles(self, page: Page):
        # Find all collapsible triggers
        triggers = page.locator(Selectors.collapsable_selector)
        count = await triggers.count()
        logging.debug("Expanding %d platform collapsibles.", count)

        for i in range(count):
            trigger = triggers.nth(i)
            parent_li = trigger.locator("xpath=..")  # go up to <a>, then parent <li>
            li = parent_li.locator("xpath=..")       # ensure we’re at the <li> level

            # Check if this <li> already has a sibling dropdown
            dropdown = li.locator(Selectors.dropdown_options_selector)
            if await dropdown.count() == 0:
                # Expand this collapsible
                await trigger.scroll_into_view_if_needed()
                await trigger.wait_for()
                await trigger.click(force=True)

                # Wait until dropdown options appear
                await li.locator(Selectors.dropdown_options_selector).wait_for()


    async def _goto_filtered_platform(self, page: Page, platform: str):
        logging.debug("Navigating to platform filter: %s", platform)
        await self._expand_platform_collapsibles(page)
        await page.locator(Selectors.filter_wrapper_selector).get_by_text(platform, exact=True).click()
        await page.wait_for_load_state("networkidle")

    # --- Criteria Matching ---
    def _matches_criteria(self, entry: GameEntry, params: SearchParams) -> bool:
        if params.name and params.name.lower() not in entry.name.lower():
            return False
        
        # If the user provided a list of genres, check for all match
        if params.genre:
            entry_genre_lower = entry.genre.lower()
            
            # Logic: "For every 'g' in our list, is 'g' present in the entry string?"
            if not all(g.lower() in entry_genre_lower for g in params.genre):
                return False
        
        if params.rating_min and entry.rating < params.rating_min:
            return False
        if params.rating_max and entry.rating > params.rating_max:
            return False
        if params.price_min and entry.price < params.price_min:
            return False
        if params.price_max and entry.price > params.price_max:
            return False
        
        # Convert "In Stock" -> True, "Out of Stock" -> False
        if params.in_stock is not None:            
            is_in_stock = entry.status.lower() == "in stock"            
            if is_in_stock != params.in_stock:
                return False
            
        return True

class GameParser:
    """Handles extraction of GameEntry objects from Playwright locators."""

    @staticmethod
    async def from_locator(e: Locator) -> GameEntry:
        # Genre
        genre_raw = await e.locator(Selectors.genre_selector).inner_text()
        genre = genre_raw.replace("\n", ",")

        # Rating
        rating = float(await e.locator(f"{Selectors.rating_selector} > *").count())

        # Price
        price_text = await e.locator(Selectors.price_selector).inner_text()
        price_value = float(price_text.replace("€", "").replace(",", ".").strip())

        # Name & Status
        name = await e.locator(Selectors.name_selector).inner_text()
        status = await e.locator(Selectors.status_selector).inner_text()

        return GameEntry(
            platform="",
            name=name,
            genre=genre,
            rating=rating,
            price=price_value,
            status=status,
        )
