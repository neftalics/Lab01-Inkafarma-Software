import ssl
import sys
import redis
import pika
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager

# Configurar logging para ver mensajes en la consola
logging.basicConfig(level=logging.INFO)

# Verificar si el módulo SSL está disponible
def check_ssl():
    if "ssl" not in sys.modules:
        raise ModuleNotFoundError("El módulo 'ssl' no está disponible en el entorno actual.")

check_ssl()

# Configuración de Redis para caché
#cache = redis.Redis(host='localhost', port=6379, db=0)

# Configuración de RabbitMQ
rabbitmq_params = pika.ConnectionParameters('localhost')
rabbit_connection = None
rabbit_channel = None

def init_rabbitmq():
    global rabbit_connection, rabbit_channel
    try:
        rabbit_connection = pika.BlockingConnection(rabbitmq_params)
        rabbit_channel = rabbit_connection.channel()
        rabbit_channel.queue_declare(queue='orders')
        logging.info("Conexión a RabbitMQ establecida")
    except Exception as e:
        logging.error("Error conectando a RabbitMQ: %s", e)
        rabbit_connection = None
        rabbit_channel = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_rabbitmq()
    yield
    if rabbit_connection:
        rabbit_connection.close()
        logging.info("Conexión a RabbitMQ cerrada")

app = FastAPI(lifespan=lifespan)

def publish_order(order_data: dict):
    """
    Publica el mensaje de la orden en la cola 'orders'.
    """
    if rabbit_channel is None:
        logging.error("RabbitMQ channel no está disponible. No se puede publicar el mensaje.")
        return
    message = str(order_data).encode('utf-8')
    try:
        rabbit_channel.basic_publish(
            exchange='',
            routing_key='orders',
            body=message
        )
        logging.info("Orden publicada en RabbitMQ: %s", order_data)
    except Exception as e:
        logging.error("Error publicando en RabbitMQ: %s", e)

def update_location_stock(location_id: int):
    """
    Función observer que actualiza el stock de una locación
    tomando los valores actuales en db_stock.
    """
    location = db_location.get(location_id)
    if not location:
        return
    updated_stock = []
    for stock_item in location["stock"]:
        product_id = stock_item["product_id"]
        # Si existe el producto en el stock global, se actualiza su cantidad
        if product_id in db_stock:
            updated_stock.append({
                "product_id": product_id,
                "quantity": db_stock[product_id]["quantity"]
            })
    # Actualizamos la lista de 'stock' de la locación
    location["stock"] = updated_stock

# Modelos de datos
class UserAuth(BaseModel):
    user_id: int
    username: str
    password: str

class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str = None

class Order(BaseModel):
    order_id: int
    user_id: int
    product_ids: List[int]
    quantity: List[int]
    location_id: int

class Payment(BaseModel):
    order_id: int
    status: str

class LoyaltyPoints(BaseModel):
    user_id: int
    points: int

class stock(BaseModel):
    product_id: int
    quantity: int

class location(BaseModel):
    location_id: int
    location_name: str
    stock: List[stock]
# Base de datos simulada
db_users = {
    1: {"username": "admin", "password": "password123"},
    2: {"username": "invitado", "password": "secret"}
}
db_products = {
    1: {"name": "Durex", "price": 18.0, "category": "Condoms"},
    2: {"name": "Panadol", "price": 8.0, "category": "Medicines"},
    3: {"name": "Pampers", "price": 25.0, "category": "Baby"},
    4: {"name": "Vick VapoRub", "price": 12.5, "category": "Medicines"},
    5: {"name": "Ensure", "price": 35.0, "category": "Supplements"},
    6: {"name": "Ibuprofen", "price": 9.0, "category": "Medicines"},
    7: {"name": "Curitas", "price": 6.0, "category": "First Aid"},
    8: {"name": "Aspirina", "price": 10.0, "category": "Medicines"},
    9: {"name": "Desitin", "price": 19.0, "category": "Baby"},
    10: {"name": "Huggies Wipes", "price": 14.0, "category": "Baby"},
    11: {"name": "Listerine", "price": 16.0, "category": "Personal Care"},
    12: {"name": "Paracetamol", "price": 7.5, "category": "Medicines"},
    13: {"name": "Ensure Plus", "price": 38.0, "category": "Supplements"},
    14: {"name": "Cicatricure Gel", "price": 22.0, "category": "Personal Care"},
    15: {"name": "Bepanthen", "price": 18.5, "category": "First Aid"},
    16: {"name": "Melatonina", "price": 20.0, "category": "Supplements"},
    17: {"name": "Neutrogena Cleanser", "price": 29.0, "category": "Personal Care"},
    18: {"name": "Similac 1", "price": 45.0, "category": "Baby"},
    19: {"name": "Omeprazol", "price": 11.0, "category": "Medicines"},
    20: {"name": "Cetaphil Lotion", "price": 27.0, "category": "Personal Care"},
}
db_orders = {}
db_payments = {}
db_loyalty = {}
db_stock = {
    1: {"product_id": 1, "quantity": 100},
    2: {"product_id": 2, "quantity": 120},
    3: {"product_id": 3, "quantity": 250},
    4: {"product_id": 4, "quantity": 80},
    5: {"product_id": 5, "quantity": 70},
    6: {"product_id": 6, "quantity": 90},
    7: {"product_id": 7, "quantity": 200},
    8: {"product_id": 8, "quantity": 60},
    9: {"product_id": 9, "quantity": 150},
    10: {"product_id": 10, "quantity": 130},
    11: {"product_id": 11, "quantity": 110},
    12: {"product_id": 12, "quantity": 95},
    13: {"product_id": 13, "quantity": 75},
    14: {"product_id": 14, "quantity": 85},
    15: {"product_id": 15, "quantity": 50},
    16: {"product_id": 16, "quantity": 60},
    17: {"product_id": 17, "quantity": 55},
    18: {"product_id": 18, "quantity": 45},
    19: {"product_id": 19, "quantity": 100},
    20: {"product_id": 20, "quantity": 70}
}

db_location = {
    1: {"location_id": 1, "location_name": "Farmacia", "stock": [db_stock[1], db_stock[2], db_stock[4], db_stock[6], db_stock[7], db_stock[19]]},
    2: {"location_id": 2, "location_name": "Supermercado", "stock": [db_stock[3], db_stock[5], db_stock[9], db_stock[10], db_stock[18]]},
    3: {"location_id": 3, "location_name": "Droguería", "stock": [db_stock[8], db_stock[11], db_stock[12], db_stock[13], db_stock[14], db_stock[15], db_stock[16], db_stock[17], db_stock[20]]},
}

# Servicio de autenticación
@app.post("/auth/login")
def login(user: UserAuth):
    print(user.model_dump())
    user_found = False
    
    # Buscamos en db_users un usuario con username/password coincidente
    for uid, user_data in db_users.items():
        if user_data["username"] == user.username and user_data["password"] == user.password:
            user_found = True
            break

    if user_found:
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/locations", response_model=List[location])
def get_locations():
    locations = []
    for location_id, location in db_location.items():
        locations.append({"id": location_id, **location})
    return locations

@app.get("/locations/{location_id}", response_model=location)
def get_location(location_id: int):
    location = db_location.get(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return {"id": location_id, **location}

@app.get("/locations/{location_id}/stock", response_model=List[stock])
def get_location_stock(location_id: int):
    location = db_location.get(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return location["stock"]

@app.get("/locations/{location_id}/stock/{product_id}", response_model=stock)
def get_location_stock_product(location_id: int, product_id: int):  
    location = db_location.get(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    for stock in location["stock"]:
        if stock["product_id"] == product_id:
            return stock
    raise HTTPException(status_code=404, detail="Producto no encontrado en la ubicación")

@app.get("/locations/{location_id}/stock/{product_id}/quantity", response_model=stock)
def get_location_stock_product_quantity(location_id: int, product_id: int):
    location = db_location.get(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    for stock in location["stock"]:
        if stock["product_id"] == product_id:
            return {"product_id": product_id, "quantity": stock["quantity"]}
    raise HTTPException(status_code=404, detail="Producto no encontrado en la ubicación")

@app.get("/stock", response_model=List[stock])
def get_stock():
    stocks = []
    for product_id, stock in db_stock.items():
        stocks.append({"id": product_id, **stock})
    return stocks

@app.get("/stock/{product_id}", response_model=stock)
def get_stock_product(product_id: int): 
    stock = db_stock.get(product_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"id": product_id, **stock}

@app.get("/stock/{product_id}/quantity", response_model=stock)
def get_stock_product_quantity(product_id: int):
    stock = db_stock.get(product_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"product_id": product_id, "quantity": stock["quantity"]}    


# Servicio de productos
@app.get("/products", response_model=List[Product])
def get_products():
    products = []
    for product_id, product in db_products.items():
        products.append({"id": product_id, **product})
    return products

@app.get("/products/name/{name}", response_model=List[Product])
def get_products_name(name: str):
    products = []
    for product_id, product in db_products.items():
        if name.lower() in product["name"].lower():
            products.append({"id": product_id, **product})
    #cache.set(name, products)
    return products

@app.get("/products/category/{category}", response_model=List[Product])
def get_products_category(category: str):
    products = []
    for product_id, product in db_products.items():
        if category.lower() in product["category"].lower():
            products.append({"id": product_id, **product})
    return products

@app.get("/products/category/{category}/id/{product_id}", response_model=Product)
def get_product_in_category_by_id(category: str, product_id: int):
    product = db_products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if category.lower() not in product["category"].lower():
        raise HTTPException(status_code=404, detail="El producto no pertenece a esa categoría")
    return {"id": product_id, **product}

@app.get("/products/recomendations/{product_id}", response_model=List[Product])
def get_products_same_category(product_id: int):
    product = db_products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    category = product["category"].lower()
    results = []
    for pid, p in db_products.items():
        if p["category"].lower() == category:
            results.append({"id": pid, **p})
    return results

# Servicio de órdenes con mensajería asíncrona
@app.post("/orders/create")
def create_order(order: Order):
    db_orders[order.order_id] = order.dict()
    publish_order(order.dict())
    return {"message": "Order created successfully"}

@app.get("/orders", response_model=List[Order])
def get_orders():
    return [Order(**o) for o in db_orders.values()]

@app.post("/payments/process")
def process_payment(payment: Payment):
    if payment.order_id not in db_orders:
        raise HTTPException(status_code=404, detail="Order not found")

    order = db_orders[payment.order_id]

    # Disminuir stock global
    for idx, product_id in enumerate(order["product_ids"]):
        qty = order["quantity"][idx]
        db_stock[product_id]["quantity"] -= qty

    # Actualizamos el stock en la locación asociada (observer)
    update_location_stock(order["location_id"])

    # Registrar pago
    db_payments[payment.order_id] = payment.dict()

    return {"message": "Payment processed"}

# Servicio de fidelidad
@app.get("/loyalty/{user_id}", response_model=LoyaltyPoints)
def get_loyalty_points(user_id: int):
    return {"user_id": user_id, "points": db_loyalty.get(user_id, 0)}
