"""
Opciones de maridaje por comida / Food pairing options.

wine_types: tipos de vino que mejor maridan con este plato
ageing: crianzas preferidas para este plato
"""

FOOD_OPTIONS = [
    {
        "key": "carne_roja",
        "name": "Carne Roja",
        "icon": "🥩",
        "icon_name": "steak",
        "description": "Filetes, chuletón, cordero asado",
        "wine_types": ["Tinto"],
        "ageing": ["Crianza"],
    },
    {
        "key": "pescado",
        "name": "Pescado",
        "icon": "🐟",
        "icon_name": "fish",
        "description": "Merluza, dorada, bacalao, rape",
        "wine_types": ["Blanco"],
        "ageing": ["Joven"],
    },
    {
        "key": "marisco",
        "name": "Marisco",
        "icon": "🦐",
        "icon_name": "anchor",
        "description": "Gambas, langosta, ostras, pulpo",
        "wine_types": ["Blanco", "Espumoso"],
        "ageing": ["Joven"],
    },
    {
        "key": "aves",
        "name": "Aves",
        "icon": "🍗",
        "icon_name": "feather",
        "description": "Pollo, pavo, pato, codorniz",
        "wine_types": ["Blanco", "Tinto"],
        "ageing": ["Joven", "Crianza"],
    },
    {
        "key": "pasta",
        "name": "Pasta / Arroz",
        "icon": "🍝",
        "icon_name": "bowl",
        "description": "Pasta con tomate, paella, risotto",
        "wine_types": ["Tinto", "Rosado"],
        "ageing": ["Joven"],
    },
    {
        "key": "quesos",
        "name": "Quesos",
        "icon": "🧀",
        "icon_name": "cheese",
        "description": "Manchego, idiazábal, tetilla, cabrales",
        "wine_types": ["Tinto", "Blanco", "Generoso"],
        "ageing": ["Crianza"],
    },
    {
        "key": "postres",
        "name": "Postres",
        "icon": "🍰",
        "icon_name": "cake",
        "description": "Tarta, chocolate, frutas, helados",
        "wine_types": ["Espumoso", "Generoso"],
        "ageing": ["Joven", "Crianza"],
    },
    {
        "key": "aperitivo",
        "name": "Aperitivo",
        "icon": "🥂",
        "icon_name": "wine-glass-bubbles",
        "description": "Tapas, pinchos, snacks, aceitunas",
        "wine_types": ["Espumoso", "Blanco", "Rosado", "Generoso"],
        "ageing": ["Joven"],
    },
]
