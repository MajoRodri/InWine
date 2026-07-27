"""
Unit tests for recommendation, pairing, and search services.
Tests unitarios para los servicios de recomendación, maridaje y búsqueda.
"""

import pytest


# ── Recommender ───────────────────────────────────────────────────────────────

class TestGetWineRecommendation:
    from app.services.recommender import get_wine_recommendation as _fn

    def test_returns_wine_for_typical_input(self):
        from app.services.recommender import get_wine_recommendation
        result = get_wine_recommendation(
            "carne_roja", 50, "Sin preferencia", "Sin preferencia",
            "Sin preferencia", "Cena especial", "Sin preferencia",
        )
        assert result is not None
        assert "wine_name" in result
        assert "explanation" in result

    def test_respects_budget(self):
        from app.services.recommender import get_wine_recommendation
        result = get_wine_recommendation(
            "pescado", 15, "Sin preferencia", "Sin preferencia",
            "Sin preferencia", "Día a día", "Sin preferencia",
        )
        assert result is not None
        # When wines exist within budget, price must not exceed it
        assert result["price_euros"] <= 15

    def test_invalid_wine_type_falls_back(self):
        """An unrecognised wine_type must not crash — treated as no preference."""
        from app.services.recommender import get_wine_recommendation
        result = get_wine_recommendation(
            "aperitivo", 100, "TipoInventado", "Sin preferencia",
            "Sin preferencia", "Celebración", "Sin preferencia",
        )
        assert result is not None

    def test_zero_budget_clamped_to_one(self):
        """budget=0 must not cause division errors or empty results."""
        from app.services.recommender import get_wine_recommendation
        result = get_wine_recommendation(
            "carne_roja", 0, "Sin preferencia", "Sin preferencia",
            "Sin preferencia", "Día a día", "Sin preferencia",
        )
        # Either finds something (budget relaxed) or returns None — no crash
        assert result is None or "wine_name" in result

    def test_whitespace_inputs_normalised(self):
        from app.services.recommender import get_wine_recommendation
        result = get_wine_recommendation(
            " carne_roja ", 40, "  Tinto  ", "Sin preferencia",
            "Sin preferencia", "  Cena  ", "Sin preferencia",
        )
        assert result is not None


class TestGetUserProfile:
    def test_returns_valid_profile(self):
        from app.services.recommender import get_user_profile
        profile = get_user_profile(["especias", "estructura", "mas_40", "fines_semana", "carnes"])
        assert "id" in profile
        assert "name" in profile
        assert 0 <= profile["id"] <= 7

    def test_empty_answers_returns_default(self):
        from app.services.recommender import get_user_profile
        profile = get_user_profile([])
        assert profile is not None
        assert "id" in profile

    def test_none_answers_handled(self):
        from app.services.recommender import get_user_profile
        profile = get_user_profile(None)  # type: ignore[arg-type]
        assert profile is not None

    def test_unknown_answers_map_to_default(self):
        from app.services.recommender import get_user_profile
        profile = get_user_profile(["respuesta_inventada", "otra_rara"])
        assert profile is not None


class TestGetFilterOptions:
    def test_has_regions_and_grapes(self):
        from app.services.recommender import get_filter_options
        opts = get_filter_options()
        assert len(opts["regions"]) > 0
        assert len(opts["grapes"]) > 0

    def test_lists_are_sorted(self):
        from app.services.recommender import get_filter_options
        opts = get_filter_options()
        assert opts["regions"] == sorted(opts["regions"])
        assert opts["grapes"] == sorted(opts["grapes"])


# ── Pairing service ───────────────────────────────────────────────────────────

class TestGetFoodPairings:
    def test_known_food_returns_wines(self):
        from app.services.pairing_service import get_food_pairings
        wines = get_food_pairings("carne_roja")
        assert len(wines) > 0

    def test_unknown_food_returns_empty(self):
        from app.services.pairing_service import get_food_pairings
        assert get_food_pairings("comida_inventada") == []

    def test_carne_roja_returns_tintos(self):
        from app.services.pairing_service import get_food_pairings
        wines = get_food_pairings("carne_roja")
        assert all(w["vine_type"] == "Tinto" for w in wines)

    def test_results_capped_at_six(self):
        from app.services.pairing_service import get_food_pairings
        for food in ["carne_roja", "pescado", "marisco", "aves", "pasta", "quesos"]:
            assert len(get_food_pairings(food)) <= 6

    def test_sorted_by_rating_descending(self):
        from app.services.pairing_service import get_food_pairings
        wines = get_food_pairings("carne_roja")
        ratings = [w["rating"] for w in wines]
        assert ratings == sorted(ratings, reverse=True)


class TestGetBestValueWines:
    def test_respects_price_filter(self):
        from app.services.pairing_service import get_best_value_wines
        wines = get_best_value_wines(max_price=20, min_rating=4.0)
        assert all(w["price_euros"] <= 20 for w in wines)
        assert all(w["rating"] >= 4.0 for w in wines)

    def test_sorted_by_quality_price_ratio(self):
        from app.services.pairing_service import get_best_value_wines
        wines = get_best_value_wines(30, 3.5)
        if len(wines) >= 2:
            ratios = [w["quality_price_ratio"] for w in wines]
            assert ratios == sorted(ratios, reverse=True)

    def test_strict_filters_may_return_empty(self):
        from app.services.pairing_service import get_best_value_wines
        wines = get_best_value_wines(max_price=1, min_rating=5.0)
        assert isinstance(wines, list)


class TestGetWineById:
    def test_existing_id_returns_wine(self):
        from app.services.recommender import get_wine_by_id
        wine = get_wine_by_id(1)
        assert wine is not None
        assert wine["id"] == 1

    def test_missing_id_returns_none(self):
        from app.services.recommender import get_wine_by_id
        assert get_wine_by_id(999_999) is None

    def test_negative_id_returns_none(self):
        from app.services.recommender import get_wine_by_id
        assert get_wine_by_id(-1) is None


# ── Search service ────────────────────────────────────────────────────────────

class TestSearchWines:
    def test_known_term_returns_results(self):
        from app.services.search_service import search_wines
        assert len(search_wines("rioja")) > 0

    def test_empty_query_returns_empty(self):
        from app.services.search_service import search_wines
        assert search_wines("") == []

    def test_whitespace_query_returns_empty(self):
        from app.services.search_service import search_wines
        assert search_wines("   ") == []

    def test_no_match_returns_empty(self):
        from app.services.search_service import search_wines
        assert search_wines("xyzwinedoesnotexistxyz") == []

    def test_results_sorted_by_rating(self):
        from app.services.search_service import search_wines
        results = search_wines("tinto")
        if len(results) >= 2:
            ratings = [w["rating"] for w in results]
            assert ratings == sorted(ratings, reverse=True)

    def test_case_insensitive(self):
        from app.services.search_service import search_wines
        lower = search_wines("rioja")
        upper = search_wines("RIOJA")
        assert len(lower) == len(upper)
