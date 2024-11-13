from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, Schema, ValidationError
import mysql.connector
from mysql.connector import Error
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:yourpassword@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')

order_product = db.Table('Order_Product',
    db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
    )

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    products = db.relationship('Product', secondary=order_product, backref=db.backref('orders_in_product'))

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products_in_order'))

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ('name', 'email', 'phone', 'id')

class OrderSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    product_id = fields.List(fields.Int(), required=True)
    date = fields.Date(dump_only=True)

    class Meta:
        fields = ('id', 'customer_id', 'product_ids', 'date')

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Int(require=True)

    class Meta:
        fields = ('username', 'password', 'customer_id', 'id')

class ProductSchema(ma.Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True)

    class Meta:
        fields = ('name', 'price', 'id')

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
account_schema = CustomerAccountSchema()
accounts_schema = CustomerAccountSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

with app.app_context():
    db.create_all()

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"messages" : f"New customer, {customer_data['name']}, has been added successfully"}), 201

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message" : f"Customer details for {customer_data['name']} have been updated succesfully"}), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message" : "Customer removed successfully"}), 200

@app.route('/customer_accounts', methods=['POST'])
def add_customer_account():
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer_account = CustomerAccount(username=account_data['username'], password=account_data['password'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"message" : f"New Customer Account created for {account_data['username']}."}), 201

@app.route('/customer_accounts/<int:id>', methods=['GET'])
def get_customer_account_info(id):
    customer_account = CustomerAccount.query.get_or_404(id)

    account_data = {
        'id' : customer_account.id,
        'username' : customer_account.username,
        'password' : '*' * len(customer_account.password),
        'customer_id' : customer_account.customer_id
    }

    return jsonify(account_data)

@app.route('/customer_accounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer_account.username = account_data['username']
    customer_account.password = account_data['password']
    db.session.commit()
    return jsonify({"message" : f"Customer Account for {account_data['username']} has been updated successfully"}), 200

@app.route('/customer_accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"message" : "Customer Account removed successfully"}), 200

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message" : f"New product, {product_data['name']}, has been added successfully"}), 201

@app.route('/products/<int:id>', methods=['GET'])
def get_product_info(id):
    product_data = Product.query.get_or_404(id)
    return product_schema.jsonify(product_data)

@app.route('/products/<int:id>', methods=['PUT'])
def update_product_info(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message" : f"Product, {product_data.name}, has been updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message" : "Product removed successfully"}), 200

@app.route('/products', methods=['GET'])
def list_all_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/orders', methods=['POST'])
def place_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer = Customer.query.get_or_404(order_data['customer_id'])
    products = Product.query.filter(Product.id.in_(order_data['product_id'])).all()
    
    if not products or len(products) != len(order_data['product_id']):
        return jsonify({"error" : "One or more product IDs are invalid"}), 400

    new_order = Order(customer_id=customer.id, products=products, date=order_data['date'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message" : f"New order for ID: {customer.name} has been created"}), 201

@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)
    return order_schema.jsonify(order)

@app.route('/orders/<int:id>', methods=['GET'])
def track_order(id):
    customer_order = Order.query.get_or_404(id)

    days_to_deliver = 7
    delivery_date = customer_order.date + timedelta(days=days_to_deliver)

    order_details = {
        'Order Date' : customer_order.date,
        'Delivery Date' : delivery_date
    }
    return jsonify(order_details)
