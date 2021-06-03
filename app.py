from logging import log
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from marshmallow import fields
from marshmallow.decorators import POST_DUMP

from sqlalchemy.orm import backref


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


# db model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(256))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __init__(self, name, description, price, quantity) -> None:
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)       
    products = db.relationship('Product', backref='category', lazy=True)

db.create_all()
# schema
class CategorySchema(ma.Schema):
    class Meta:
        fields = ("id", "name")

class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description", "price", "quantity")
    category = ma.Nested(CategorySchema)


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

# CATEGORY API
@app.get('/')
def hello():
    return jsonify({ "data": "Hello, World"})

@app.get('/categories')
def get_categories():
    categories = Category.query.all()
    res = categories_schema.dump(categories)
    return jsonify(res)

@app.post('/category')
def add_category():
    name = request.json['name']
    
    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return category_schema.jsonify(new_category)

@app.get('/category/<int:id>')
def get_category(id):
    category = Category.query.get(id)
    return category_schema.jsonify(category)

@app.put('/category/<int:id>')
def update_category(id):
    category = Category.query.get(id)
    name = request.json['name']
    
    category.name = name
    db.session.commit()
    return category_schema.jsonify(category)    

@app.delete('/category/<int:id>')
def delete_category(id):
    category = Category.query.get(id)
    db.session.delete(category)
    db.session.commit()
    return category_schema.jsonify(category)

# PRODUCT API
@app.get('/products')
def get_products():
    product = Product.query.all()
    res = products_schema.dump(product)
    return jsonify(res)

@app.get('/product/<int:id>')
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

@app.post('/product')
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    quantity = request.json['quantity']
    category_id = request.json['category_id']
    category = Category.query.get(int(category_id))
    if not category:
        return jsonify({"error": "Category not exist"})
    new_product = Product(name=name, description=description, price=price, quantity=quantity)
    new_product.category_id = category_id
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)

@app.put('/product/<int:id>')
def update_product(id):
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    quantity = request.json['quantity']
    category_id = request.json['category_id']
    category = Category.query.get(int(category_id))
    if not category:
        return jsonify({"error": "Category not exist"})
    product = Product.query.get(id)
    product.name = name
    product.description = description
    product.price = price
    product.quantity = quantity
    product.category_id = category_id
    db.session.commit()
    return product_schema.jsonify(product)

@app.delete('/product/<int:id>')
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)

if __name__ == '__main__':
    app.run(debug=True)

