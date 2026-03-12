# ==========================================
# FOODIE WEBSITE - DATABASE MODELS
# ==========================================

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# ==========================================
# USER MODEL
# ==========================================
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), default='')
    address = db.Column(db.String(300), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat()
        }


# ==========================================
# CATEGORY MODEL
# ==========================================
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    item_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'item_count': self.item_count
        }


# ==========================================
# RESTAURANT MODEL
# ==========================================
class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), default='')
    rating = db.Column(db.Float, default=0.0)
    order_count = db.Column(db.Integer, default=0)
    cuisine = db.Column(db.String(200), default='')
    delivery_time = db.Column(db.String(50), default='')
    delivery_fee = db.Column(db.String(50), default='')

    products = db.relationship('Product', backref='restaurant', lazy=True)
    reviews = db.relationship('Review', backref='restaurant', lazy=True)

    def to_dict(self, include_products=False):
        data = {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'rating': self.rating,
            'order_count': self.order_count,
            'cuisine': self.cuisine,
            'delivery_time': self.delivery_time,
            'delivery_fee': self.delivery_fee
        }
        if include_products:
            data['products'] = [p.to_dict() for p in self.products]
        return data


# ==========================================
# PRODUCT MODEL
# ==========================================
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), default='')
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200), default='')
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'rating': self.rating,
            'review_count': self.review_count,
            'image': self.image,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else ''
        }


# ==========================================
# ORDER MODEL
# ==========================================
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subtotal = db.Column(db.Integer, default=0)
    delivery_fee = db.Column(db.Integer, default=50)
    tax = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    delivery_address = db.Column(db.String(300), default='')
    payment_method = db.Column(db.String(50), default='cod')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self, include_items=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'subtotal': self.subtotal,
            'delivery_fee': self.delivery_fee,
            'tax': self.tax,
            'total': self.total,
            'status': self.status,
            'delivery_address': self.delivery_address,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat()
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data


# ==========================================
# ORDER ITEM MODEL
# ==========================================
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'quantity': self.quantity,
            'price': self.price
        }


# ==========================================
# REVIEW MODEL
# ==========================================
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(500), default='')
    reviewer_name = db.Column(db.String(100), default='')
    reviewer_avatar = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'rating': self.rating,
            'text': self.text,
            'reviewer_name': self.reviewer_name or (self.user.name if self.user else 'Anonymous'),
            'reviewer_avatar': self.reviewer_avatar,
            'created_at': self.created_at.isoformat()
        }


# ==========================================
# CART ITEM MODEL (session-based cart)
# ==========================================
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)  # links to user session or user_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'restaurant_name': self.product.restaurant.name if self.product and self.product.restaurant else '',
            'price': self.product.price if self.product else 0,
            'quantity': self.quantity,
            'image': self.product.image if self.product else ''
        }


# ==========================================
# NEWSLETTER SUBSCRIBER MODEL
# ==========================================
class Subscriber(db.Model):
    __tablename__ = 'subscribers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
