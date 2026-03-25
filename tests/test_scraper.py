# tests/test_scraper.py
import pytest
from schemas import SearchParams, Platforms
from services import Scraper

class TestScraper:

    @pytest.mark.asyncio
    async def test_scraper_search_by_name(self):
        params = SearchParams(name="Halo")  
        async with Scraper(headless=False) as scraper:
            results = await scraper.run(params)

        assert len(results) > 1, "Scraper returned an empty list"

        found_names = [r.name for r in results]
        assert any(params.name.lower() in name.lower() for name in found_names), \
            f"Keyword '{params.name}' not found in any results: {found_names[:5]}..."
        
        print(results)
        assert False

    @pytest.mark.asyncio
    async def test_scraper_filter_by_platform(self):
        params = SearchParams(platform=Platforms.PSP)
        async with Scraper(headless=False) as scraper:
            results = await scraper.run(params)

        assert len(results) > 1, "Scraper returned an empty list"

        mismatches = [r.name for r in results if params.platform not in r.platform.lower()]
        assert not mismatches, f"Platform mismatch found in these items: {mismatches}"

    @pytest.mark.asyncio
    async def test_scraper_price_filters(self):
        params = SearchParams(platform=Platforms.SWITCH, price_min=85, price_max=90)
        async with Scraper(headless=False) as scraper:
            results = await scraper.run(params)

        assert len(results) > 1, "Scraper returned an empty list"
        
        for r in results:
            assert r.platform == params.platform, f"Expected {params.platform}, got {r.platform} ({r.name})"
            
            assert params.price_min <= r.price <= params.price_max, \
                f"Price {r.price} out of range [{params.price_min}-{params.price_max}] for {r.name}"
            
    @pytest.mark.asyncio
    async def test_scraper_rating_filters(self):
        params = SearchParams(platform=Platforms.WII, rating_min=2.0, rating_max=4.0)
        async with Scraper(headless=False) as scraper:
            results = await scraper.run(params)

        assert len(results) > 1, "Scraper returned an empty list"
        
        for r in results:
            assert r.platform == params.platform, f"Expected {params.platform}, got {r.platform} ({r.name})"        
            assert params.rating_min <= r.rating <= params.rating_max, \
                f"Rating {r.rating} out of range [{params.rating_min}-{params.rating_max}] for {r.name}"

    @pytest.mark.asyncio
    async def test_scraper_rating_filters(self):
        params = SearchParams(platform=Platforms.WII_U, genre=['3D','Action'])
        async with Scraper(headless=False) as scraper:
            results = await scraper.run(params)

        assert len(results) > 1, "Scraper returned an empty list"
        
        for r in results:
            assert r.platform == params.platform, f"Expected {params.platform}, got {r.platform} ({r.name})"
            
            r_genre_lower = r.genre.lower()
            for g in params.genre:
                assert g.lower() in r_genre_lower, (
                    f"Item '{r.name}' has genres '{r.genre}', "
                    f"but is missing required genre: '{g}'"
                )

    @pytest.mark.asyncio
    async def test_scraper_stock_filters(self):
        params = SearchParams(platform=Platforms.XBOX_X, in_stock=False)
        async with Scraper(headless=False) as scraper:
            results = await scraper.run(params)
        
        assert len(results) > 1, "Scraper returned an empty list"

        for r in results:
            assert r.platform == params.platform, f"Expected {params.platform}, got {r.platform} ({r.name})"
            
            # Map the boolean param to the expected string
            expected_status = "in stock" if params.in_stock else "out of stock"
            
            assert r.status.lower() == expected_status, (
                f"Stock filter failed for '{r.name}'. "
                f"Expected '{expected_status}', but got '{r.status}'"
                )
        
