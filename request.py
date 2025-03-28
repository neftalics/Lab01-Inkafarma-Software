import pytest
from fastapi.testclient import TestClient
from main import app, db_orders, db_payments, db_loyalty, db_stock

client = TestClient(app)

def test_login_ok():
    data = {"username": "admin", "password": "password123", "user_id": 1}
    print("Probando /auth/login (OK) con:", data)
    response = client.post("/auth/login", json=data)
    print("Respuesta:", response.status_code, response.json())
    assert response.status_code == 200
    assert "Login successful" in response.text

def test_login_fail():
    data = {"username": "invalido", "password": "12345", "user_id": 99}
    print("Probando /auth/login (fail) con:", data)
    response = client.post("/auth/login", json=data)
    print("Respuesta:", response.status_code, response.json())
    assert response.status_code == 401

def test_get_products():
    print("Probando /products")
    response = client.get("/products")
    print("Respuesta:", response.status_code, response.json())
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_products_by_name():
    name = "Panadol"
    print(f"Probando /products/name/{name}")
    response = client.get(f"/products/name/{name}")
    data = response.json()
    print("Respuesta:", response.status_code, data)
    assert response.status_code == 200
    assert len(data) > 0
    assert any(name.lower() in p["name"].lower() for p in data)

def test_get_products_by_category():
    category = "Medicines"
    print(f"Probando /products/category/{category}")
    response = client.get(f"/products/category/{category}")
    data = response.json()
    print("Respuesta:", response.status_code, data)
    assert response.status_code == 200
    assert len(data) > 0
    for p in data:
        assert category.lower() in p["category"].lower()

def test_get_product_in_category_by_id():
    category = "Medicines"
    product_id = 2  # Panadol
    print(f"Probando /products/category/{category}/id/{product_id}")
    response = client.get(f"/products/category/{category}/id/{product_id}")
    data = response.json()
    print("Respuesta:", response.status_code, data)
    assert response.status_code == 200
    assert data["id"] == product_id

def test_get_products_recomendations():
    product_id = 2   # Panadol, categoría Medicines
    print(f"Probando /products/recomendations/{product_id}")
    response = client.get(f"/products/recomendations/{product_id}")
    data = response.json()
    print("Respuesta:", response.status_code, data)
    assert response.status_code == 200
    assert isinstance(data, list)
    for p in data:
        assert "medicines" in p["category"].lower()

def test_create_order():
    new_order = {
        "order_id": 999,
        "user_id": 1,
        "product_ids": [2, 4],
        "quantity": [5, 2],
        "location_id": 1
    }
    print("Creando orden:", new_order)
    response = client.post("/orders/create", json=new_order)
    print("Respuesta /orders/create:", response.status_code, response.json())
    assert response.status_code == 200
    assert "Order created successfully" in response.text
    assert 999 in db_orders
    order = db_orders[999]
    print("Orden registrada en db_orders:", order)
    assert order["user_id"] == 1
    assert order["product_ids"] == [2, 4]
    assert order["quantity"] == [5, 2]
    assert order["location_id"] == 1

def test_get_orders():
    print("Probando /orders")
    response = client.get("/orders")
    orders = response.json()
    print("Respuesta /orders:", response.status_code, orders)
    assert response.status_code == 200
    assert isinstance(orders, list)
    assert len(orders) > 0
    order_999 = None
    for o in orders:
        if o.get("order_id") == 999:
            order_999 = o
            break
    print("Orden 999 encontrada en /orders:", order_999)
    assert order_999 is not None
    assert order_999["user_id"] == 1
    assert order_999["product_ids"] == [2, 4]
    assert order_999["quantity"] == [5, 2]
    assert order_999["location_id"] == 1

def test_process_payment():
    print("Probando /payments/process para orden 999")
    # Tomamos el stock inicial de productos
    initial_stock_2 = db_stock[2]["quantity"]
    initial_stock_4 = db_stock[4]["quantity"]
    print(f"Stock inicial - Producto 2: {initial_stock_2}, Producto 4: {initial_stock_4}")
    
    payment_data = {"order_id": 999, "status": "Paid"}
    response = client.post("/payments/process", json=payment_data)
    print("Respuesta /payments/process:", response.status_code, response.json())
    assert response.status_code == 200
    # Verificamos el registro del pago
    assert payment_data["order_id"] in db_payments
    print("Pago registrado en db_payments:", db_payments[payment_data["order_id"]])
    assert db_payments[payment_data["order_id"]]["status"] == "Paid"
    
    # Verificamos la actualización del stock tras eliminar cantidades de la orden 999
    expected_stock_2 = initial_stock_2 - 5  # orden reduce 5 unidades del producto 2
    expected_stock_4 = initial_stock_4 - 2  # y 2 unidades del producto 4
    print(f"Stock esperado - Producto 2: {expected_stock_2}, Producto 4: {expected_stock_4}")
    print("Stock actual - Producto 2:", db_stock[2]["quantity"])
    print("Stock actual - Producto 4:", db_stock[4]["quantity"])
    assert db_stock[2]["quantity"] == expected_stock_2
    assert db_stock[4]["quantity"] == expected_stock_4
    
    # Validación adicional: la orden debe pertenecer al usuario correcto
    order = db_orders[payment_data["order_id"]]
    print("Orden asociada al pago:", order)
    assert order["user_id"] == 1

def test_loyalty_points():
    user_id = 101
    print(f"Probando /loyalty/{user_id}")
    response = client.get(f"/loyalty/{user_id}")
    data = response.json()
    print("Respuesta /loyalty:", response.status_code, data)
    assert response.status_code == 200
    assert data["user_id"] == user_id
    assert isinstance(data["points"], int)

def test_get_locations():
    print("Probando /locations")
    response = client.get("/locations")
    data = response.json()
    print("Respuesta /locations:", response.status_code, data)
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_location():
    location_id = 1
    print(f"Probando /locations/{location_id}")
    response = client.get(f"/locations/{location_id}")
    data = response.json()
    print(f"Respuesta /locations/{location_id}:", response.status_code, data)
    assert response.status_code == 200
    assert "location_name" in data

def test_get_location_stock():
    location_id = 1
    print(f"Probando /locations/{location_id}/stock")
    response = client.get(f"/locations/{location_id}/stock")
    data = response.json()
    print(f"Respuesta /locations/{location_id}/stock:", response.status_code, data)
    assert response.status_code == 200
    assert isinstance(data, list)

def test_get_location_stock_product():
    location_id = 1
    product_id = 2
    print(f"Probando /locations/{location_id}/stock/{product_id}")
    response = client.get(f"/locations/{location_id}/stock/{product_id}")
    data = response.json()
    print(f"Respuesta /locations/{location_id}/stock/{product_id}:", response.status_code, data)
    assert response.status_code == 200
    assert data["product_id"] == product_id

def test_get_location_stock_product_quantity():
    location_id = 1
    product_id = 2
    print(f"Probando /locations/{location_id}/stock/{product_id}/quantity")
    response = client.get(f"/locations/{location_id}/stock/{product_id}/quantity")
    data = response.json()
    print(f"Respuesta /locations/{location_id}/stock/{product_id}/quantity:", response.status_code, data)
    assert response.status_code == 200
    assert "quantity" in data

def test_get_stock():
    print("Probando /stock")
    response = client.get("/stock")
    data = response.json()
    print("Respuesta /stock:", response.status_code, data)
    assert response.status_code == 200
    assert isinstance(data, list)

def test_get_stock_product():
    prod_id = 2
    print(f"Probando /stock para producto con id {prod_id}")
    response = client.get(f"/stock/{prod_id}")
    data = response.json()
    print(f"Respuesta /stock/{prod_id}:", response.status_code, data)
    # Dependiendo de la implementación se espera "id" o "product_id"
    # Ajustamos la validación:
    assert response.status_code == 200
    assert data.get("id") == prod_id or data.get("product_id") == prod_id

def test_get_stock_product_quantity():
    prod_id = 2
    print(f"Probando /stock/{prod_id}/quantity")
    response = client.get(f"/stock/{prod_id}/quantity")
    data = response.json()
    print(f"Respuesta /stock/{prod_id}/quantity:", response.status_code, data)
    assert response.status_code == 200
    assert "quantity" in data

if __name__ == "__main__":
    pytest.main(["-sv", "request.py"])