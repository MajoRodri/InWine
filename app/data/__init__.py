from .loader import WINES
from .clusters import CLUSTER_PROFILES
from .cluster_ui import PROFILE_UI
from .user_profiles import USER_PROFILES, USER_PROFILES_BY_ID
from .food_options import FOOD_OPTIONS

# Precompute wine count per cluster / Conteo de vinos por cluster
_cluster_counts: dict[int, int] = {}
for _w in WINES:
    _cid = _w["cluster_id"]
    _cluster_counts[_cid] = _cluster_counts.get(_cid, 0) + 1

# Enrich USER_PROFILES with wine_count so explore page can use them directly
# Enriquece USER_PROFILES con wine_count para que la página de explorar los use
for _p in USER_PROFILES:
    _p["wine_count"] = _cluster_counts.get(_p["cluster_id"], 0)

# WINE_PROFILES: cluster stats + UI metadata + aesthetic name from USER_PROFILES
# Merges ML cluster data with the aesthetic user-facing name and UI fields.
# WINE_PROFILES: estadísticas del cluster + UI + nombre estético de USER_PROFILES
WINE_PROFILES: list[dict] = [
    {
        "id":          k,
        **v,
        **PROFILE_UI.get(k, {}),
        "wine_count":  _cluster_counts.get(k, 0),
        "name":           USER_PROFILES_BY_ID[k]["name"] if k in USER_PROFILES_BY_ID else v.get("name", f"Cluster {k}"),
        "description":    USER_PROFILES_BY_ID[k]["description"] if k in USER_PROFILES_BY_ID else v.get("description", ""),
        "description_en": USER_PROFILES_BY_ID[k].get("description_en", "") if k in USER_PROFILES_BY_ID else "",
    }
    for k, v in sorted(CLUSTER_PROFILES.items())
]
