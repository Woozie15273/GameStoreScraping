from dataclasses import dataclass

@dataclass(frozen=True)
class Selectors:
    
    next_page_selector: str = '.next'
    collapsable_selector: str = 'li a + svg'
    dropdown_options_selector: str = '.platform-group-links'
    filter_wrapper_selector: str = '.filter-wrapper'

    search_input_selector: str = 'input'
    exec_search_selector: str = 'input + svg'

    product_card_selector: str = '.product-card'
    platform_selector: str = '.current-game-platform span:nth-child(2)'
    name_selector: str = '.title'
    genre_selector: str = '.category'
    rating_selector: str = '.rating'
    price_selector: str = '.price-wrapper'
    status_selector: str = '.price-wrapper + p'