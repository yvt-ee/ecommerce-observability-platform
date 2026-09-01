def test_get_products_returns_seeded_catalog(client):
    response = client.get("/api/products")
    assert response.status_code == 200

    products = response.json()
    assert len(products) >= 5
    assert {"Laptop", "Headphones", "Keyboard"}.issubset({p["name"] for p in products})
    for product in products:
        assert product["price"] > 0
