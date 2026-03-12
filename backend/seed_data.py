# ==========================================
# FOODIE WEBSITE - SEED DATA
# Populates the database with the exact same
# data that exists in index.html
# ==========================================

from models import db, Category, Restaurant, Product, Review


def seed_database():
    """Populate database with initial data matching the frontend."""

    # Clear existing data
    Review.query.delete()
    Product.query.delete()
    Restaurant.query.delete()
    Category.query.delete()
    db.session.commit()

    # ==========================================
    # CATEGORIES (from index.html categories section)
    # ==========================================
    categories = [
        Category(name='Pizza', icon='🍕', item_count=125),
        Category(name='Burgers', icon='🍔', item_count=98),
        Category(name='Asian', icon='🍜', item_count=156),
        Category(name='Indian', icon='🥘', item_count=203),
        Category(name='Sushi', icon='🍣', item_count=87),
        Category(name='Desserts', icon='🍰', item_count=112),
    ]
    db.session.add_all(categories)
    db.session.flush()

    # ==========================================
    # RESTAURANTS (from index.html restaurants section)
    # ==========================================
    restaurants = [
        Restaurant(
            name='Pizza Paradise',
            image='images/pizza.png',
            rating=4.8,
            order_count=1250,
            cuisine='Italian, Pizzas, Continental',
            delivery_time='20-30 min',
            delivery_fee='₹50 Delivery'
        ),
        Restaurant(
            name='Burger Barn',
            image='images/burger.png',
            rating=4.5,
            order_count=980,
            cuisine='Fast Food, Burgers, American',
            delivery_time='15-20 min',
            delivery_fee='Free'
        ),
        Restaurant(
            name='Spice Kitchen',
            image='images/fried-chicken.png',
            rating=4.9,
            order_count=2100,
            cuisine='Indian, North Indian, Curries',
            delivery_time='25-35 min',
            delivery_fee='₹49 Delivery'
        ),
        Restaurant(
            name='Asian Wok',
            image='images/spring-roll.png',
            rating=4.6,
            order_count=1450,
            cuisine='Chinese, Thai, Pan-Asian',
            delivery_time='20-30 min',
            delivery_fee='₹40 Delivery'
        ),
        Restaurant(
            name='Taco Fiesta',
            image='images/chicken-roll.png',
            rating=4.4,
            order_count=650,
            cuisine='Mexican, Tacos, Burritos',
            delivery_time='18-25 min',
            delivery_fee='₹30 Delivery'
        ),
        Restaurant(
            name='Sushi Master',
            image='images/spaghetti.png',
            rating=4.9,
            order_count=890,
            cuisine='Japanese, Sushi, Asian',
            delivery_time='30-40 min',
            delivery_fee='₹60 Delivery'
        ),
    ]
    db.session.add_all(restaurants)
    db.session.flush()

    # ==========================================
    # PRODUCTS (from index.html products section)
    # ==========================================
    products = [
        Product(
            name='Margherita Pizza',
            description='Fresh mozzarella, basil, tomato sauce',
            price=349,
            rating=4.8,
            review_count=245,
            image='images/pizza.png',
            restaurant_id=restaurants[0].id
        ),
        Product(
            name='Cheese Burger',
            description='Juicy beef patty with melted cheese',
            price=199,
            rating=4.7,
            review_count=189,
            image='images/burger.png',
            restaurant_id=restaurants[1].id
        ),
        Product(
            name='Pad Thai',
            description='Stir-fried noodles with shrimp and peanuts',
            price=299,
            rating=4.9,
            review_count=312,
            image='images/spaghetti.png',
            restaurant_id=restaurants[3].id
        ),
        Product(
            name='Butter Chicken',
            description='Tender chicken in creamy tomato sauce',
            price=399,
            rating=4.8,
            review_count=421,
            image='images/fried-chicken.png',
            restaurant_id=restaurants[2].id
        ),
        Product(
            name='Chicken Tacos',
            description='Grilled chicken with salsa and lime',
            price=249,
            rating=4.6,
            review_count=156,
            image='images/chicken-roll.png',
            restaurant_id=restaurants[4].id
        ),
        Product(
            name='Salmon Sushi Roll',
            description='Fresh salmon with avocado and cucumber',
            price=449,
            rating=4.9,
            review_count=298,
            image='images/sandwich.png',
            restaurant_id=restaurants[5].id
        ),
    ]
    db.session.add_all(products)
    db.session.flush()

    # ==========================================
    # REVIEWS (from index.html testimonials section)
    # ==========================================
    reviews = [
        Review(
            rating=5,
            text='The food arrived hot and delicious! Best pizza I\'ve had in a while. Highly recommend!',
            reviewer_name='Rajesh Kumar',
            reviewer_avatar='images/profile1.jpeg',
            restaurant_id=restaurants[0].id
        ),
        Review(
            rating=5,
            text='Super fast delivery! My order arrived in just 18 minutes. The burger was perfect!',
            reviewer_name='Priya Singh',
            reviewer_avatar='images/profile2.jpeg',
            restaurant_id=restaurants[1].id
        ),
        Review(
            rating=4,
            text='Great selection and reasonable prices. Definitely ordering again next week!',
            reviewer_name='Arjun Patel',
            reviewer_avatar='images/profile3.jpeg',
            restaurant_id=restaurants[2].id
        ),
        Review(
            rating=5,
            text='The sushi was incredibly fresh and beautifully presented. Worth every penny!',
            reviewer_name='Anjali Desai',
            reviewer_avatar='images/profile1.jpeg',
            restaurant_id=restaurants[5].id
        ),
        Review(
            rating=5,
            text='Easy to use app, great customer service. They even called to confirm my order preferences!',
            reviewer_name='Vikram Iyer',
            reviewer_avatar='images/profile2.jpeg',
            restaurant_id=restaurants[3].id
        ),
        Review(
            rating=5,
            text='Love the variety of restaurants. Found a new favorite place thanks to Foodie!',
            reviewer_name='Sana Gupta',
            reviewer_avatar='images/profile3.jpeg',
            restaurant_id=restaurants[4].id
        ),
    ]
    db.session.add_all(reviews)

    db.session.commit()
    print('[OK] Database seeded successfully!')
    print(f'   Categories: {Category.query.count()}')
    print(f'   Restaurants: {Restaurant.query.count()}')
    print(f'   Products: {Product.query.count()}')
    print(f'   Reviews: {Review.query.count()}')
