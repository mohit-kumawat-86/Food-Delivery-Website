# ==========================================
# FOODIE WEBSITE - FLASK BACKEND
# ==========================================

import os
import sys
from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
from datetime import timedelta
import uuid

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Category, Restaurant, Product, Order, OrderItem, Review, CartItem, Subscriber

# ==========================================
# APP CONFIGURATION
# ==========================================
app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
            static_url_path='')

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'foodie.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'foodie-secret-key-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db.init_app(app)
CORS(app, supports_credentials=True)


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_session_id():
    """Get or create a session ID for cart tracking."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['session_id']


def get_current_user():
    """Get the currently logged-in user or None."""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def error_response(message, status_code=400):
    """Return a standardized error response."""
    return jsonify({'error': message}), status_code


def success_response(data=None, message='Success', status_code=200):
    """Return a standardized success response."""
    response = {'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


# ==========================================
# SERVE FRONTEND
# ==========================================
@app.route('/')
def serve_frontend():
    """Serve the main index.html file."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve image files."""
    images_dir = os.path.join(app.static_folder, 'images')
    return send_from_directory(images_dir, filename)


@app.route('/login.html')
def serve_login():
    return send_from_directory(app.static_folder, 'login.html')


@app.route('/signup.html')
def serve_signup():
    return send_from_directory(app.static_folder, 'signup.html')


@app.route('/cart.html')
def serve_cart():
    return send_from_directory(app.static_folder, 'cart.html')


@app.route('/orders.html')
def serve_orders():
    return send_from_directory(app.static_folder, 'orders.html')


@app.route('/profile.html')
def serve_profile():
    return send_from_directory(app.static_folder, 'profile.html')


@app.route('/pages.css')
def serve_pages_css():
    return send_from_directory(app.static_folder, 'pages.css')


@app.route('/menu.html')
def serve_menu():
    return send_from_directory(app.static_folder, 'menu.html')


# ==========================================
# CATEGORIES API
# ==========================================
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all food categories."""
    categories = Category.query.all()
    return jsonify({
        'data': [c.to_dict() for c in categories],
        'count': len(categories)
    })


# ==========================================
# RESTAURANTS API
# ==========================================
@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """Get all restaurants, optionally filtered by cuisine."""
    cuisine = request.args.get('cuisine', '')

    query = Restaurant.query
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(f'%{cuisine}%'))

    restaurants = query.all()
    return jsonify({
        'data': [r.to_dict() for r in restaurants],
        'count': len(restaurants)
    })


@app.route('/api/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """Get a single restaurant with its menu (products)."""
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return error_response('Restaurant not found', 404)

    return jsonify({
        'data': restaurant.to_dict(include_products=True)
    })


# ==========================================
# PRODUCTS API
# ==========================================
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products, optionally filtered."""
    category = request.args.get('category', '')
    restaurant_id = request.args.get('restaurant_id', type=int)
    search = request.args.get('search', '')

    query = Product.query

    if restaurant_id:
        query = query.filter_by(restaurant_id=restaurant_id)

    if category:
        # Filter by matching restaurant cuisine
        query = query.join(Restaurant).filter(Restaurant.cuisine.ilike(f'%{category}%'))

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )

    products = query.all()
    return jsonify({
        'data': [p.to_dict() for p in products],
        'count': len(products)
    })


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product."""
    product = Product.query.get(product_id)
    if not product:
        return error_response('Product not found', 404)

    return jsonify({'data': product.to_dict()})


# ==========================================
# AUTH API
# ==========================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return error_response('No data provided')

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return error_response('Name, email, and password are required')

    if len(password) < 6:
        return error_response('Password must be at least 6 characters')

    # Check if user already exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        return error_response('Email already registered')

    # Create user
    user = User(name=name, email=email)
    user.set_password(password)

    if data.get('phone'):
        user.phone = data['phone']
    if data.get('address'):
        user.address = data['address']

    db.session.add(user)
    db.session.commit()

    # Auto-login after registration
    session['user_id'] = user.id

    # Transfer guest cart items to user
    session_id = get_session_id()
    CartItem.query.filter_by(session_id=session_id, user_id=None).update({'user_id': user.id})
    db.session.commit()

    return success_response(user.to_dict(), 'Registration successful', 201)


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with email and password."""
    data = request.get_json()
    if not data:
        return error_response('No data provided')

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return error_response('Email and password are required')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response('Invalid email or password', 401)

    session['user_id'] = user.id

    # Transfer guest cart items to user
    session_id = get_session_id()
    CartItem.query.filter_by(session_id=session_id, user_id=None).update({'user_id': user.id})
    db.session.commit()

    return success_response(user.to_dict(), 'Login successful')


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout current user."""
    session.pop('user_id', None)
    return success_response(message='Logged out successfully')


@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """Get currently logged-in user info."""
    user = get_current_user()
    if not user:
        return error_response('Not logged in', 401)

    return jsonify({'data': user.to_dict()})


@app.route('/api/auth/me', methods=['PUT'])
def update_current_user():
    """Update currently logged-in user's profile."""
    user = get_current_user()
    if not user:
        return error_response('Not logged in', 401)

    data = request.get_json()
    if not data:
        return error_response('No data provided')

    if 'name' in data and data['name'].strip():
        user.name = data['name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip()
    if 'address' in data:
        user.address = data['address'].strip()

    db.session.commit()
    return success_response(user.to_dict(), 'Profile updated successfully')


# ==========================================
# CART API
# ==========================================
@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get current cart items."""
    session_id = get_session_id()
    user = get_current_user()

    if user:
        items = CartItem.query.filter_by(user_id=user.id).all()
    else:
        items = CartItem.query.filter_by(session_id=session_id, user_id=None).all()

    cart_items = [item.to_dict() for item in items]

    # Calculate totals
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    delivery_fee = 50 if subtotal > 0 else 0
    tax = round(subtotal * 0.05)
    total = subtotal + delivery_fee + tax

    return jsonify({
        'data': {
            'items': cart_items,
            'summary': {
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'tax': tax,
                'total': total,
                'item_count': len(cart_items)
            }
        }
    })


@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add an item to the cart."""
    data = request.get_json()
    if not data:
        return error_response('No data provided')

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return error_response('Product ID is required')

    product = Product.query.get(product_id)
    if not product:
        return error_response('Product not found', 404)

    session_id = get_session_id()
    user = get_current_user()

    # Check if item already in cart
    if user:
        existing = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()
    else:
        existing = CartItem.query.filter_by(session_id=session_id, user_id=None, product_id=product_id).first()

    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(
            session_id=session_id,
            user_id=user.id if user else None,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    return success_response(
        {'product_name': product.name, 'price': product.price},
        f'{product.name} added to cart!',
        201
    )


@app.route('/api/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """Update cart item quantity."""
    data = request.get_json()
    quantity = data.get('quantity', 1) if data else 1

    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        return error_response('Cart item not found', 404)

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()
    return success_response(message='Cart updated')


@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    """Remove an item from the cart."""
    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        return error_response('Cart item not found', 404)

    db.session.delete(cart_item)
    db.session.commit()
    return success_response(message='Item removed from cart')


@app.route('/api/cart', methods=['DELETE'])
def clear_cart():
    """Clear all items from the cart."""
    session_id = get_session_id()
    user = get_current_user()

    if user:
        CartItem.query.filter_by(user_id=user.id).delete()
    else:
        CartItem.query.filter_by(session_id=session_id, user_id=None).delete()

    db.session.commit()
    return success_response(message='Cart cleared')


# ==========================================
# ORDERS API
# ==========================================
@app.route('/api/orders', methods=['POST'])
def place_order():
    """Place a new order (checkout)."""
    user = get_current_user()
    session_id = get_session_id()

    # Get cart items
    if user:
        cart_items = CartItem.query.filter_by(user_id=user.id).all()
    else:
        cart_items = CartItem.query.filter_by(session_id=session_id, user_id=None).all()

    if not cart_items:
        return error_response('Cart is empty')

    data = request.get_json() or {}
    delivery_address = data.get('delivery_address', '')
    payment_method = data.get('payment_method', 'cod')

    # Calculate totals
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    delivery_fee = 50
    tax = round(subtotal * 0.05)
    total = subtotal + delivery_fee + tax

    # Create order
    order = Order(
        user_id=user.id if user else None,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax=tax,
        total=total,
        status='confirmed',
        delivery_address=delivery_address or (user.address if user else ''),
        payment_method=payment_method
    )
    db.session.add(order)
    db.session.flush()

    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)

    # Clear the cart
    for cart_item in cart_items:
        db.session.delete(cart_item)

    db.session.commit()

    return success_response(order.to_dict(), 'Order placed successfully!', 201)


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get order history for logged-in user."""
    user = get_current_user()
    if not user:
        return error_response('Please login to view orders', 401)

    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return jsonify({
        'data': [o.to_dict() for o in orders],
        'count': len(orders)
    })


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a single order's details."""
    order = Order.query.get(order_id)
    if not order:
        return error_response('Order not found', 404)

    return jsonify({'data': order.to_dict()})


# ==========================================
# REVIEWS API
# ==========================================
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Get all reviews, optionally filtered by restaurant."""
    restaurant_id = request.args.get('restaurant_id', type=int)

    query = Review.query.order_by(Review.created_at.desc())
    if restaurant_id:
        query = query.filter_by(restaurant_id=restaurant_id)

    reviews = query.all()
    return jsonify({
        'data': [r.to_dict() for r in reviews],
        'count': len(reviews)
    })


@app.route('/api/reviews', methods=['POST'])
def create_review():
    """Submit a new review."""
    data = request.get_json()
    if not data:
        return error_response('No data provided')

    rating = data.get('rating')
    text = data.get('text', '').strip()
    restaurant_id = data.get('restaurant_id')

    if not rating or not restaurant_id:
        return error_response('Rating and restaurant_id are required')

    if not (1 <= rating <= 5):
        return error_response('Rating must be between 1 and 5')

    user = get_current_user()

    review = Review(
        user_id=user.id if user else None,
        restaurant_id=restaurant_id,
        rating=rating,
        text=text,
        reviewer_name=user.name if user else data.get('reviewer_name', 'Anonymous')
    )
    db.session.add(review)
    db.session.commit()

    return success_response(review.to_dict(), 'Review submitted!', 201)


# ==========================================
# NEWSLETTER API
# ==========================================
@app.route('/api/newsletter', methods=['POST'])
def subscribe_newsletter():
    """Subscribe to newsletter."""
    data = request.get_json()
    if not data:
        return error_response('No data provided')

    email = data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return error_response('Please provide a valid email address')

    # Check if already subscribed
    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        return success_response(message=f'{email} is already subscribed!')

    subscriber = Subscriber(email=email)
    db.session.add(subscriber)
    db.session.commit()

    return success_response(subscriber.to_dict(), f'✓ Subscribed! Check {email} for offers.', 201)


# ==========================================
# SEARCH API
# ==========================================
@app.route('/api/search', methods=['GET'])
def search():
    """Search across restaurants and products."""
    query = request.args.get('q', '').strip()
    if not query:
        return error_response('Search query is required')

    restaurants = Restaurant.query.filter(
        db.or_(
            Restaurant.name.ilike(f'%{query}%'),
            Restaurant.cuisine.ilike(f'%{query}%')
        )
    ).all()

    products = Product.query.filter(
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )
    ).all()

    return jsonify({
        'data': {
            'restaurants': [r.to_dict() for r in restaurants],
            'products': [p.to_dict() for p in products]
        },
        'total_results': len(restaurants) + len(products)
    })


# ==========================================
# APP STARTUP
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()

        # Seed database if empty
        if Category.query.count() == 0:
            from seed_data import seed_database
            seed_database()
            print('[SEED] Database seeded with initial data')
        else:
            print(f'[DB] Database already has {Category.query.count()} categories, {Restaurant.query.count()} restaurants, {Product.query.count()} products')

    print('')
    print('================================')
    print('   FOODIE BACKEND SERVER')
    print('   http://localhost:5000')
    print('   API: http://localhost:5000/api')
    print('================================')
    print('')

    app.run(debug=True, host='0.0.0.0', port=5000)
