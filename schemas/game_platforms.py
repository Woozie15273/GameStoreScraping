from dataclasses import dataclass

@dataclass(frozen=True)
class Platforms():
    # Nintendo
    WII = "wii"
    WII_U = "wii-u"
    NINTENDO_64 = "nintendo-64"
    SWITCH = "switch"
    GAMECUBE = "gamecube"
    GBA = "game-boy-advance"
    N3DS = "3ds"
    DS = "ds"
    
    # Xbox
    XBOX = "xbox"
    XBOX_360 = 'xbox-360'
    XBOX_ONE = 'xbox-one'
    XBOX_X = 'xbox-series-x'
    
    # SEGA
    DREAMCAST = "Dreamcast"
    
    # PlayStation
    PS1 = "playstation-1"
    PS2 = "playstation-2"
    PS3 = "playstation-3"
    PS4 = "playstation-4"
    PS5 = "playstation-5"
    PS_VITA = "playstation-vita"
    PSP = "psp"
    
    # Others
    PC = "Pc"
    STADIA = "Stadia"
    ALL = "all"