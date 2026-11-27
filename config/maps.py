MAP_NAMES = [
    "AATLIS",
    "ANTARCTIC PENINSULA",
    "BUSAN",
    "CIRCUIT ROYAL",
    "COLOSSEO",
    "DORADO",
    "ESPERANÇA",
    "EICHENWALDE",
    "WATCHPOINT:GRIMSVÖTON",
    "HAVANA",
    "HOLLYWOOD",
    "ILIOS",
    "JUNKERTOWN",
    "KING'S ROW",
    "LIJIANG TOWER",
    "MIDTOWN",
    "NEPAL",
    "NEON JUNCTION",
    "NEW JUNK CITY",
    "NEW QUEEN STREET",
    "NUMBANI",
    "OASIS",
    "PARAÍSO",
    "RIALTO",
    "ROUTE 66",
    "RUNASAPI",
    "SAMOA",
    "SHAMBALI MONASTERY",
    "SURAVASA",
    "TEMPLE OF ANUBIS",
    "THRONE OF ANUBIS",
    "WATCHPOINT:GIBRALTAR",
]


# Preserve the candidate set used by the original single-pass OCR script.
LEGACY_OCR_MAP_NAMES = [
    name for name in MAP_NAMES
    if name not in {"AATLIS", "NEON JUNCTION", "NEW QUEEN STREET"}
]
