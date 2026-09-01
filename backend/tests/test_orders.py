def test_create_order_success(client):
    product = client.get("/api/products").json()[0]

    response = client.post("/api/orders", json={"product_id": product["id"], "quantity": 2})

    assert response.status_code == 201
    order = response.json()
    assert order["product_id"] == product["id"]
    assert order["quantity"] == 2
    assert order["total_amount"] == round(product["price"] * 2, 2)


def test_get_orders_includes_created_order(client):
    product = client.get("/api/products").json()[0]
    client.post("/api/orders", json={"product_id": product["id"], "quantity": 1})

    response = client.get("/api/orders")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_create_order_with_unknown_product_returns_404(client):
    response = client.post("/api/orders", json={"product_id": 999999, "quantity": 1})
    assert response.status_code == 404


def test_create_order_with_invalid_quantity_returns_422(client):
    product = client.get("/api/products").json()[0]

    response = client.post("/api/orders", json={"product_id": product["id"], "quantity": 0})

    assert response.status_code == 422
