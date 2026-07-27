"""
User wine personality profiles / Perfiles de personalidad vinícola del usuario.

These archetypes describe HOW a person drinks wine, not the wine itself.
The quiz maps user answers to one of these profiles, then wines from the
matching cluster_id are recommended.

Estos arquetipos describen CÓMO bebe vino una persona, no el vino en sí.
El quiz asigna las respuestas del usuario a uno de estos perfiles, y se
recomiendan vinos del cluster_id correspondiente.
"""

USER_PROFILES: list[dict] = [
    {
        "id":              0,
        "cluster_id":      0,
        "name":            "Signature Reserve",
        "description":     (
            "Para ti el vino es colección y patrimonio. Buscas grandes reservas, "
            "añadas históricas de las D.O. más prestigiosas y no te importa invertir "
            "en una botella que espere su momento perfecto en la bodega."
        ),
        "description_en":  (
            "For you wine is a collection and a legacy. You seek great reserves, "
            "historic vintages from the most prestigious DOs, and you don't mind "
            "investing in a bottle that waits for its perfect moment in the cellar."
        ),
        "color":           "#C9A050",
        "bg":              "rgba(201, 160, 80, 0.12)",
        "border":          "rgba(201, 160, 80, 0.35)",
        "color_dark":      "#E8C060",
        "bg_dark":         "rgba(232, 192, 96, 0.22)",
        "border_dark":     "rgba(232, 192, 96, 0.50)",
        "icon_name":       "trophy",
        "characteristics":    ["Alta gama", "Coleccionista", "Gran Reserva", "Ocasiones únicas"],
        "characteristics_en": ["Premium", "Collector", "Gran Reserva", "Special occasions"],
        "temp":            "16-18°C",
    },
    {
        "id":              1,
        "cluster_id":      1,
        "name":            "Elegant Whites",
        "description":     (
            "Elegante, aromático y refinado: así es tu paladar. Los blancos atlánticos "
            "y los frescos Verdejos de Rueda son tu terreno. Buscas acidez viva, "
            "minerales expresivos y aromas que te transporten."
        ),
        "description_en":  (
            "Elegant, aromatic and refined — that's your palate. Atlantic whites and "
            "crisp Verdejos from Rueda are your territory. You seek lively acidity, "
            "expressive minerals and aromas that transport you."
        ),
        "color":           "#7AAED4",
        "bg":              "rgba(122, 174, 212, 0.12)",
        "border":          "rgba(122, 174, 212, 0.35)",
        "color_dark":      "#9AC8EC",
        "bg_dark":         "rgba(154, 200, 236, 0.22)",
        "border_dark":     "rgba(154, 200, 236, 0.50)",
        "icon_name":       "star",
        "characteristics":    ["Blanco", "Aromático", "Mariscos y pescado", "Mineral"],
        "characteristics_en": ["White", "Aromatic", "Seafood & fish", "Mineral"],
        "temp":            "8-10°C",
    },
    {
        "id":              2,
        "cluster_id":      2,
        "name":            "Fresh & Easy",
        "description":     (
            "Directo al grano, sin pretensiones. Te gustan los tintos jóvenes de "
            "regiones emergentes, con fruta viva y carácter propio. El precio no te "
            "asusta si la botella merece la pena."
        ),
        "description_en":  (
            "Straight to the point, no pretensions. You like young reds from emerging "
            "regions, with vibrant fruit and their own character. Price doesn't scare "
            "you if the bottle is worth it."
        ),
        "color":           "#5A8C60",
        "bg":              "rgba(90, 140, 96, 0.15)",
        "border":          "rgba(90, 140, 96, 0.35)",
        "color_dark":      "#7AC880",
        "bg_dark":         "rgba(122, 200, 128, 0.22)",
        "border_dark":     "rgba(122, 200, 128, 0.48)",
        "icon_name":       "leaf",
        "characteristics":    ["Tinto joven", "Regiones emergentes", "Sin crianza", "Frutal"],
        "characteristics_en": ["Young red", "Emerging regions", "Unoaked", "Fruity"],
        "temp":            "14-16°C",
    },
    {
        "id":              3,
        "cluster_id":      3,
        "name":            "Wild Terroir",
        "description":     (
            "Te atraen los vinos inclasificables, los que no encajan en ninguna "
            "categoría. Valdeorras, Penedès, Navarra... el mapa vinícola es tu "
            "campo de exploración y cada botella una sorpresa."
        ),
        "description_en":  (
            "You're drawn to wines that defy classification, the ones that don't fit "
            "any category. Valdeorras, Penedès, Navarra... the wine map is your "
            "playground and every bottle a surprise."
        ),
        "color":           "#6B7280",
        "bg":              "rgba(107, 114, 128, 0.08)",
        "border":          "rgba(107, 114, 128, 0.25)",
        "color_dark":      "#A8B0BC",
        "bg_dark":         "rgba(168, 176, 188, 0.20)",
        "border_dark":     "rgba(168, 176, 188, 0.42)",
        "icon_name":       "compass",
        "characteristics":    ["Ecléctico", "Asequible", "Versátil", "Sin prejuicios"],
        "characteristics_en": ["Eclectic", "Affordable", "Versatile", "Open-minded"],
        "temp":            "12-16°C",
    },
    {
        "id":              4,
        "cluster_id":      4,
        "name":            "Mediterranean Soul",
        "description":     (
            "Los generosos y vinos únicos del sur de España son tu pasión. Jerez, "
            "Montilla-Moriles, la crianza bajo flor... sabes que estos vinos "
            "representan una tradición centenaria sin igual en el mundo."
        ),
        "description_en":  (
            "The fortified and unique wines of southern Spain are your passion. Jerez, "
            "Montilla-Moriles, flor-aged wines... you know these wines represent a "
            "centuries-old tradition unmatched in the world."
        ),
        "color":           "#C48040",
        "bg":              "rgba(196, 128, 64, 0.12)",
        "border":          "rgba(196, 128, 64, 0.35)",
        "color_dark":      "#E09A50",
        "bg_dark":         "rgba(224, 154, 80, 0.22)",
        "border_dark":     "rgba(224, 154, 80, 0.50)",
        "icon_name":       "celebrate",
        "characteristics":    ["Generoso", "Jerez", "Maridaje gourmet", "Sobremesa"],
        "characteristics_en": ["Fortified", "Sherry", "Gourmet pairing", "After dinner"],
        "temp":            "8-14°C",
    },
    {
        "id":              5,
        "cluster_id":      5,
        "name":            "Bubble & Celebration",
        "description":     (
            "Para ti el vino es sinónimo de celebración. Un buen Cava con crianza "
            "prolongada es tu señal de que algo especial está por ocurrir. "
            "Vives el vino como experiencia social y festiva."
        ),
        "description_en":  (
            "For you wine is synonymous with celebration. A fine aged Cava signals "
            "that something special is about to happen. You live wine as a social "
            "and festive experience."
        ),
        "color":           "#C0A898",
        "bg":              "rgba(192, 168, 152, 0.12)",
        "border":          "rgba(192, 168, 152, 0.35)",
        "color_dark":      "#D8C4B8",
        "bg_dark":         "rgba(216, 196, 184, 0.22)",
        "border_dark":     "rgba(216, 196, 184, 0.48)",
        "icon_name":       "wine-glass-bubbles",
        "characteristics":    ["Espumoso", "Celebración", "Social", "Cava Premium"],
        "characteristics_en": ["Sparkling", "Celebration", "Social", "Premium Cava"],
        "temp":            "6-8°C",
    },
    {
        "id":              6,
        "cluster_id":      6,
        "name":            "Oak & Time",
        "description":     (
            "Rioja y Ribera del Duero son tu casa. Aprecias la crianza lenta en "
            "barrica, los taninos sedosos y las bodegas con décadas de historia. "
            "Un buen tinto con crianza es, para ti, la perfección."
        ),
        "description_en":  (
            "Rioja and Ribera del Duero are your home. You appreciate slow barrel "
            "ageing, silky tannins and wineries with decades of history. A fine "
            "aged red is, for you, perfection."
        ),
        "color":           "#7C4B0B",
        "bg":              "rgba(124, 75, 11, 0.08)",
        "border":          "rgba(124, 75, 11, 0.25)",
        "color_dark":      "#CC8040",
        "bg_dark":         "rgba(204, 128, 64, 0.22)",
        "border_dark":     "rgba(204, 128, 64, 0.50)",
        "icon_name":       "strength",
        "characteristics":    ["Tinto con crianza", "Rioja / Ribera", "Tradicional", "Con cuerpo"],
        "characteristics_en": ["Barrel-aged red", "Rioja / Ribera", "Classic", "Full-bodied"],
        "temp":            "16-18°C",
    },
    {
        "id":              7,
        "cluster_id":      7,
        "name":            "Everyday Red",
        "description":     (
            "Calidad sin complicaciones, casi cualquier día. Te gustan los tintos "
            "jóvenes de D.O. reconocidas con buena relación calidad-precio. "
            "Eres el perfil más cercano a los grandes amantes del vino español."
        ),
        "description_en":  (
            "Quality without fuss, almost every day. You like young reds from "
            "recognised DOs with great value for money. You're the profile closest "
            "to the great Spanish wine lovers."
        ),
        "color":           "#B91C1C",
        "bg":              "rgba(185, 28, 28, 0.08)",
        "border":          "rgba(185, 28, 28, 0.25)",
        "color_dark":      "#F07085",
        "bg_dark":         "rgba(240, 112, 133, 0.20)",
        "border_dark":     "rgba(240, 112, 133, 0.48)",
        "icon_name":       "heart",
        "characteristics":    ["Tinto joven", "D.O. Premium", "Calidad-precio", "Para cada día"],
        "characteristics_en": ["Young red", "Premium DO", "Value for money", "Everyday"],
        "temp":            "14-16°C",
    },
]

# Quick lookup by profile id / Búsqueda rápida por id de perfil
USER_PROFILES_BY_ID: dict[int, dict] = {p["id"]: p for p in USER_PROFILES}
