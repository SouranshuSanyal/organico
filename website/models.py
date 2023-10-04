from . import db
from datetime import datetime
from flask_login import UserMixin


class Products(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    productID = db.Column(db.String(150))
    productName = db.Column(db.String(150))
    productPrice = db.Column(db.String(150))
    category = db.Column(db.String(50), default = 'fruits')
    stock = db.Column(db.String(10))
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    phoneNumber = db.Column(db.Integer, unique = True)
    name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    role = db.Column(db.String(50), default='user')
    cart = db.relationship('Cart', backref='user', uselist=False, lazy=True)
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column (db.Integer, db.ForeignKey('user.id'))
    order = db.relationship('Order', backref='cart', uselist=False, lazy=True)
    items = db.relationship('CartItem', backref='cart', lazy=True)
    
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    quantity = db.Column(db.Integer, default=1)

    @property
    def total_price(self):
        return float(self.product.productPrice) * int(self.quantity)
    
    
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address_line1 = db.Column(db.String(250))
    address_line2 = db.Column(db.String(250), nullable=True)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(100))
    orders = db.relationship('Order', backref='address', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), unique=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Products', backref='order_items')
    order = db.relationship('Order', backref='order_items')

    @property
    def total_price(self):
        return float(self.product.productPrice) * int(self.quantity)
    

