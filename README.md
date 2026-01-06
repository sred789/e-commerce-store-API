API Endpoints

This API provides RESTful endpoints for managing users, products, and orders in an example eCommerce system.

User Endpoints
	•	GET /users
Retrieve all users
	•	GET /users/<id>
Retrieve a user by ID
	•	POST /users
Create a new user
	•	PUT /users/<id>
Update a user by ID
	•	DELETE /users/<id>
Delete a user by ID
	•	GET /users/<id>/orders
Retrieve all orders for a specific user

⸻

Product Endpoints
	•	GET /products
Retrieve all products
	•	GET /products/<id>
Retrieve a product by ID
	•	POST /products
Create a new product
	•	PUT /products/<id>
Update a product by ID
	•	DELETE /products/<id>
Delete a product by ID

⸻

Order Endpoints
	•	POST /orders
Create a new order (requires user_id and order_date)
	•	PUT /orders/<order_id>/add_product/<product_id>
Add a product to an order (duplicates prevented)
	•	DELETE /orders/<order_id>/remove_product/<product_id>
Remove a product from an order
	•	GET /users/<user_id>/orders
Retrieve all orders for a specific user
	•	GET /orders/<order_id>/products
Retrieve all products associated with an order

⸻

Project Overview

In this project, Flask, SQLAlchemy, and Marshmallow are used to build a RESTful API for an example eCommerce store.

The database consists of the following tables:
	•	User_account – stores user information
	•	Products – stores product details
	•	Orders – stores order records
	•	Order_product – association table used to model the many-to-many relationship between orders and products

The API supports full CRUD operations for users and products, order creation, and managing relationships between orders and products.
