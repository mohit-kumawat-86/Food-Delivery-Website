# Food Delivery Website

A complete, responsive web application for a food delivery service with a modern UI and a Flask backend.

## 🌟 Features

- **Responsive Design**: Works perfectly on mobile, tablet, and desktop devices.
- **Dynamic Menu**: Browse products by category or restaurant.
- **Shopping Cart**: Add items to your cart, update quantities, and calculate totals (including taxes and delivery fees).
- **User Authentication**: Sign up and log in to save your order history and profile details.
- **Restaurant Pages**: View specific restaurant menus and reviews.
- **Order Management**: Checkout and view your past orders.
- **Search Functionality**: Easily find restaurants or specific food items.
- **Newsletter Subscription**: Sign up for the latest offers.

## 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3 (Custom responsive styling, variables for theming)
- JavaScript (Vanilla, no framework)

### Backend
- Python
- Flask & Flask-CORS
- SQLite (via SQLAlchemy)

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed on your system.

### Installation & Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/mohit-kumawat-86/Food-Delivery-Website.git
   cd Food-Delivery-Website
   ```

2. **Install Backend Dependencies**:
   ```bash
   pip install flask flask-cors sqlalchemy flask-sqlalchemy
   ```

3. **Run the Backend Server**:
   ```bash
   python backend/app.py
   ```
   *Note: Upon first run, the database (`foodie.db`) will be automatically created and seeded with sample data.*

4. **Access the Application**:
   Open your browser and navigate to:
   ```
   http://localhost:5000/
   ```
   (The Flask server serves the frontend files directly.)

## 📂 Project Structure

```
├── backend/
│   ├── app.py           # Main Flask application and API routes
│   ├── models.py        # SQLAlchemy database models
│   ├── seed_data.py     # Initial database seeding script
│   └── foodie.db        # SQLite database (generated)
├── images/              # Image assets for the frontend
├── index.html           # Main landing page
├── menu.html            # Menu browsing page
├── cart.html            # Shopping cart and checkout page
├── login.html           # User login page
├── signup.html          # User registration page
├── profile.html         # User profile page
├── orders.html          # Order history page
├── style.css            # Main stylesheet (global styles, layout)
├── pages.css            # Stylesheet for internal pages (cart, login, etc.)
└── script.js            # Frontend interactivity and API integration
```

## 🤝 Contributing

Feel free to fork this project, submit pull requests, or open issues if you find any bugs or have feature requests!