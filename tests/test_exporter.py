import pytest

from config import Config
from schemas import SearchParams, GameEntry, Platforms
from services import Exporter, Scraper

class TestExporter:

    SAMPLE_GAMES: list[GameEntry] = [
        GameEntry('', 'Halo: Combat Evolved', 'Action,Shooter,First-Person,Sci-Fi', 5.0, 87.99, 'Out of Stock'),
        GameEntry('', 'Halo 3', 'Action,Shooter,First-Person,Sci-Fi,Arcade', 4.0, 81.99, 'Out of Stock'),
        GameEntry('', 'Halo: Reach', 'Action,Shooter,First-Person,Sci-Fi,Arcade', 4.0, 84.99, 'In stock'),
        GameEntry('', 'Halo: The Master Chief Collection - Halo 3', 'Action,Shooter,First-Person,Arcade', 4.0, 79.99, 'In stock'),
        GameEntry('', 'Halo: The Master Chief Collection', 'Miscellaneous,Compilation,Action,Shooter,First-Person,Sci-Fi,Arcade', 4.0, 79.99, 'Out of Stock'),
        GameEntry('', 'Halo 5: Guardians', 'Shooter,Sci-Fi,Action,First-Person,Arcade', 3.0, 64.99, 'In stock'),
        GameEntry('', 'Halo: Combat Evolved Anniversary', 'Action,Shooter,First-Person,Sci-Fi,Arcade', 3.0, 82.99, 'Out of Stock'),
        GameEntry('', 'Halo Wars', 'Strategy,Real-Time,Sci-Fi,General,Command', 3.0, 75.99, 'Out of Stock'),
        GameEntry('', 'Halo Wars: Definitive Edition', 'Strategy,Real-Time,General,Command', 3.0, 77.99, 'Out of Stock')
    ]
    
    @pytest.fixture
    def empty_exporter(self):
        return Exporter(data=[])
    
    @pytest.fixture
    def sample_exporter(self):
        return Exporter(data=self.SAMPLE_GAMES)    
    
    @pytest.mark.parametrize("params, expected_substrings, unexpected_substrings, fallback", [
        # Scenario 1: Standard mix of types
        (SearchParams(platform=Platforms.PC, rating_min=4.0), ["platform_pc", "rating_min_4"], [], None),
        
        # Scenario 2: List handling
        (SearchParams(genre=["RPG", "Indie"]), ["genre_rpg-indie"], [], None),
        
        # Scenario 3: None/Empty handling
        (SearchParams(platform=Platforms.PS5, name=None, genre=[]), ["platform_playstation-5"], ["name_", "genre_"], None),
        
        # Scenario 4: Sanitization (Special characters and spaces)
        (SearchParams(platform=Platforms.SWITCH), ["platform_switch"], [" ", "!"], None),
        
        # Scenario 5: Completely empty params
        (SearchParams(), [], [], "all_entries")
    ])
    def test_generate_filename_scenarios(self, empty_exporter: Exporter, params, expected_substrings, unexpected_substrings, fallback):
        """Tests all filename generation logic in a single parameterized loop."""
        result = empty_exporter.generate_filename(params)
        
        # Check for expected parts
        for substring in expected_substrings:
            assert substring in result
            
        # Check that excluded/None parts are NOT there
        for substring in unexpected_substrings:
            assert substring not in result
            
        # Check fallback logic for empty params
        if fallback:
            assert result == fallback
        
        # Ensure result is always lowercase
        assert result == result.lower()

    @pytest.mark.asyncio
    async def test_to_csv(self, sample_exporter: Exporter):
        filename = sample_exporter.generate_filename(SearchParams(name="Halo"))
        await sample_exporter.to_csv_async(filename)
    
    @pytest.mark.asyncio
    async def test_to_json(self, sample_exporter: Exporter):
        filename = sample_exporter.generate_filename(SearchParams(name="Halo"))
        await sample_exporter.to_json_async(filename)

    @pytest.mark.asyncio
    async def test_to_sqlite(self, sample_exporter: Exporter):
        filename = sample_exporter.generate_filename(SearchParams(name="Halo"))
        await sample_exporter.to_sqlite_async(filename)

    @pytest.mark.asyncio
    async def test_end_to_end_csv(self):
        params = SearchParams(
            platform = Platforms.PC,
            name = None,
            genre = ['Turn-Based'],
            rating_min = 3.0,
            rating_max = None,
            price_min= None,
            price_max = 85.00,
            in_stock = True)        

        EXPORT_AS_CSV = True
        EXPORT_AS_JSON = True
        EXPORT_AS_SQLITE = True

        async with Scraper(headless=False, max_concurrency=Config.MAX_CONCURRENCY) as scraper:
            results = await scraper.run(params)
        
        exporter = Exporter(results)
        filename = exporter.generate_filename(params)
        
        export_tasks = []

        if EXPORT_AS_CSV:
            export_tasks.append(exporter.to_csv_async(filename))
        if EXPORT_AS_JSON:
            export_tasks.append(exporter.to_json_async(filename))
        if EXPORT_AS_SQLITE:
            export_tasks.append(exporter.to_sqlite_async(filename))

        for task in export_tasks:
            await task
    