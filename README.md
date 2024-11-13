# E-Commerce API

This is a RESTful API for managing customers, products, orders, and customer accounts in an e-commerce system. The API is built with **Flask** and **SQLAlchemy**, and utilizes CRUD functionality and integration with a **MySQL** database. Finally Postman collections are available for endpoint testing.

## Features
+ Customer Management: Create, retrieve, update, and delete customer data.
+ Customer Account Management: Create and manage customer account details.
+ Product Management: Utilize CRUD operations to manage product catalog.
+ Order Management: Place and track orders.
+ Postman Collection: Use pre-built collections for endpoint testing.

## How to Use
1. Make sure access is available to MySQL and POSTMAN.
2. Within VS Code:
    1. Clone repository
    2. Set up virtual environment and install necessary imports
    3. Create a MySQL Database
    4. Reconfigure the Database URI with your MySQL username, password, and database name
    5. Run flask application
3. Within Postman:
    1. Import Postman collections
    2. Use http://localhost:5000/ along with the imported collections for endpoint testing
