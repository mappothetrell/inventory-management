"""
Tests for restocking API endpoints.
"""
import pytest


class TestRestockingEndpoints:
    """Test suite for restocking-related endpoints."""

    def test_get_recommendations_basic(self, client):
        """Test getting restocking recommendations with a generous budget."""
        response = client.get("/api/restocking/recommendations?budget=100000")
        assert response.status_code == 200

        data = response.json()
        assert "budget" in data
        assert "total_recommended_cost" in data
        assert "remaining_budget" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0

        first_item = data["items"][0]
        for field in [
            "sku", "item_name", "warehouse", "category", "quantity_on_hand",
            "reorder_point", "current_demand", "forecasted_demand", "trend",
            "unit_cost", "urgency_score", "recommended_quantity",
            "recommended_cost", "funded",
        ]:
            assert field in first_item, f"Missing field: {field}"

    def test_recommendations_only_include_urgent_items(self, client):
        """Every recommended item should be understocked or facing rising demand."""
        response = client.get("/api/restocking/recommendations?budget=100000")
        data = response.json()

        for item in data["items"]:
            understocked = item["quantity_on_hand"] < item["reorder_point"]
            demand_rising = item["forecasted_demand"] > item["current_demand"]
            assert understocked or demand_rising

    def test_recommendations_sorted_by_urgency_desc(self, client):
        """Recommendations should be ranked most-urgent first."""
        response = client.get("/api/restocking/recommendations?budget=100000")
        data = response.json()

        urgency_scores = [item["urgency_score"] for item in data["items"]]
        assert urgency_scores == sorted(urgency_scores, reverse=True)

    def test_recommendations_greedy_allocation_continues_past_unaffordable_items(self, client):
        """Greedy walk should skip an unaffordable item but keep funding cheaper ones ranked below it."""
        full_response = client.get("/api/restocking/recommendations?budget=100000")
        full_items = full_response.json()["items"]
        assert len(full_items) > 1

        budget = round(full_items[0]["recommended_cost"] - 0.01, 2)
        response = client.get(f"/api/restocking/recommendations?budget={budget}")
        data = response.json()
        items = data["items"]

        assert items[0]["funded"] is False

        remaining = budget
        for item in items:
            expected_funded = item["recommended_cost"] <= remaining
            assert item["funded"] == expected_funded
            if expected_funded:
                remaining -= item["recommended_cost"]

        assert any(item["funded"] for item in items[1:])

    def test_recommendations_respects_warehouse_filter(self, client):
        """Test filtering recommendations by warehouse."""
        response = client.get("/api/restocking/recommendations?budget=100000&warehouse=Tokyo")
        assert response.status_code == 200

        data = response.json()
        for item in data["items"]:
            assert item["warehouse"] == "Tokyo"

    def test_recommendations_respects_category_filter(self, client):
        """Test filtering recommendations by category."""
        response = client.get("/api/restocking/recommendations?budget=100000&category=Sensors")
        assert response.status_code == 200

        data = response.json()
        for item in data["items"]:
            assert item["category"].lower() == "sensors"

    def test_recommendations_zero_budget(self, client):
        """A zero budget should fund nothing but still return the ranked candidate list."""
        response = client.get("/api/restocking/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["total_recommended_cost"] == 0
        assert data["remaining_budget"] == 0
        assert all(not item["funded"] for item in data["items"])

    def test_place_restocking_order_appends_to_orders(self, client):
        """Placing a restocking order should append it to the orders list with a lead time."""
        payload = {
            "budget": 1000,
            "items": [
                {"sku": "TEST-SKU-1", "item_name": "Test Widget", "quantity": 10, "unit_cost": 5.0}
            ],
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 200

        created = response.json()
        assert created["order_number"].startswith("RSK-")
        assert created["source"] == "restocking"
        assert 7 <= created["lead_time_days"] <= 14
        assert created["status"] == "Processing"

        orders_response = client.get("/api/orders")
        all_orders = orders_response.json()
        assert any(o["order_number"] == created["order_number"] for o in all_orders)

    def test_place_restocking_order_total_value_matches_items(self, client):
        """Test that the created order's total value matches its line items."""
        payload = {
            "budget": 1000,
            "items": [
                {"sku": "TEST-SKU-2", "item_name": "Test Bolt", "quantity": 4, "unit_cost": 2.5},
                {"sku": "TEST-SKU-3", "item_name": "Test Nut", "quantity": 3, "unit_cost": 1.0},
            ],
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 200

        created = response.json()
        calculated_total = sum(item["quantity"] * item["unit_price"] for item in created["items"])
        assert abs(created["total_value"] - calculated_total) < 0.01

    def test_place_restocking_order_empty_items_rejected(self, client):
        """Test that submitting a restocking order with no items is rejected."""
        response = client.post("/api/restocking/orders", json={"budget": 1000, "items": []})
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
