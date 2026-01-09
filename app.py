from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from sqlalchemy import Column, Table, Integer, String, ForeignKey, Float
from marshmallow import ValidationError
from typing import List, Optional
import pandas as pd;
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:water123!@localhost/ecommerce_api'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

ma = Marshmallow(app)

#User table

class User(Base):
    __tablename__ = 'user_account'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


#Product table
class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    orders: Mapped[List["Order"]] = relationship(back_populates="products", secondary="order_product")


#Order table
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_date: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user_account.id'),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="orders")
    products: Mapped[List["Product"]] = relationship(
        back_populates="orders",
        secondary="order_product"
    )


#Order_Product association
order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey('orders.id'), primary_key=True),
    Column("product_id", ForeignKey('products.id'), primary_key=True)
)

#Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=User
        load_instance=True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Order
        load_instance=True
        include_fk = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Product
        load_instance=True

user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


with app.app_context():
    db.create_all()

# Routes
#Create user
@app.route("/users", methods=["POST"])
def create_user():
    try:
        new_user = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.message), 400
    
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

#Get all users
@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = db.session.query(User).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return users_schema.jsonify(users), 200


#Get user by ID
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try: 
        user= db.session.query(User).get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return user_schema.jsonify(user)


#Update user
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        user_data = request.json
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data["name"]
    user.email = user_data["email"]
    user.address = user_data["address"]
    db.session.commit()

    return user_schema.jsonify(user), 200

#Delete user
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

#Create product
@app.route("/products", methods=["POST"])
def create_product():
    try:
        new_product = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.message), 400
    
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product), 201

#Get all products
@app.route("/products", methods=["GET"])
def get_products():
    try:
        products = db.session.query(Product).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return products_schema.jsonify(products), 200

#Get product by ID
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = db.session.query(Product).get(product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return product_schema.jsonify(product)

#Update product
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    try:
        product_data = request.json
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.name = product_data["name"]
    product.price = product_data["price"]
    db.session.commit()

    return product_schema.jsonify(product), 200

#Delete product
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

#Create order
@app.route("/orders", methods=["POST"])
def create_order():
    try:
        new_order = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 201

#Add product to order
@app.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["PUT"])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order:
        return jsonify({"message": "Order not found"}), 404
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if product in order.products:
        return jsonify({"message": "Product already in order"}), 409

    order.products.append(product)
    db.session.commit()

    return jsonify({"message": "Product added to order"}), 200

#Delete product from an order
@app.route("/orders/<int:order_id>/remove_product/<int:product_id>", methods=["DELETE"])
def remove_product_from_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order:
        return jsonify({"message": "Order not found"}), 404
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if product not in order.products:
        return jsonify({"message": "Product not in order"}), 409

    order.products.remove(product)
    db.session.commit()

    return jsonify({"message": "Product removed from order"}), 200

#Get all orders for a user
@app.route("/users/<int:user_id>/orders", methods=["GET"])
def get_orders_for_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return orders_schema.jsonify(user.orders), 200

#Get all products in order
@app.route("/orders/<int:order_id>/products", methods=["GET"])
def get_products_in_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    return products_schema.jsonify(order.products), 200


#Export to csv
@app.route("/users/export", methods=["GET"])
def export_users_to_csv():
    users = db.session.query(User).all()

    data = [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "address": u.address
    } for u in users]

    df = pd.DataFrame(data)

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"users_{timestamp}.csv"

    # Ensure exports folder exists
    os.makedirs("exports", exist_ok=True)

    filepath = os.path.join("exports", filename)
    df.to_csv(filepath, index=False)

    return jsonify({
        "message": "Users exported successfully",
        "file": filename
    }), 200

if __name__ == "__main__":
    app.run(debug=True)