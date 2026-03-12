// ==========================================
// FOODIE WEBSITE - JAVASCRIPT FUNCTIONALITY
// With Flask Backend API Integration
// ==========================================

// API Configuration
const API_BASE = 'http://localhost:5000/api';
let useAPI = true; // Will be set to false if backend is unreachable

// CART MANAGEMENT (localStorage fallback)
let cart = JSON.parse(localStorage.getItem('foodieCart')) || [];

// DOM ELEMENTS
const hamburgerMenu = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');
const cartIcon = document.querySelector('.cart-icon');
const cartValue = document.querySelector('.cart-value');
const addToCartButtons = document.querySelectorAll('.btn-add-cart');

// INITIALIZE APP
document.addEventListener('DOMContentLoaded', () => {
    injectUIComponents();
    checkBackendConnection();
    initializeCart();
    attachEventListeners();
    updateCartCount();
    loadMenuLinks();
});

// ==========================================
// INJECT MODAL & DRAWER UI
// ==========================================
function injectUIComponents() {
    const html = `
    <!-- OVERLAY -->
    <div class="foodie-overlay" id="foodie-overlay" onclick="closeFoodieModals()"></div>

    <!-- MENU MODAL -->
    <div class="foodie-modal" id="menu-modal">
        <div class="foodie-modal-header">
            <h2 id="menu-modal-title">Restaurant Menu</h2>
            <button class="foodie-modal-close" onclick="closeFoodieModals()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="foodie-modal-body" id="menu-modal-body">
            <!-- Menu items injected here -->
        </div>
    </div>

    <!-- CART DRAWER -->
    <div class="foodie-drawer" id="cart-drawer">
        <div class="foodie-drawer-header">
            <h2>Your Cart</h2>
            <button class="foodie-drawer-close" onclick="closeFoodieModals()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="foodie-drawer-body" id="cart-drawer-body">
            <!-- Cart items injected here -->
        </div>
        <div class="foodie-drawer-footer" id="cart-drawer-footer">
            <!-- Summary injected here -->
        </div>
    </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
}

window.closeFoodieModals = function() {
    document.getElementById('foodie-overlay').classList.remove('active');
    document.getElementById('menu-modal').classList.remove('active');
    document.getElementById('cart-drawer').classList.remove('active');
}

// ==========================================
// BACKEND CONNECTION CHECK
// ==========================================
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE}/categories`, {
            method: 'GET',
            credentials: 'include'
        });
        if (response.ok) {
            useAPI = true;
            console.log('✅ Backend connected! Using API mode.');
            // Check if user is logged in and update header
            await updateAuthHeader();
            // Sync localStorage cart to backend
            await syncLocalCartToBackend();
        } else {
            useAPI = false;
            console.log('⚠️ Backend responded with error. Using offline mode.');
        }
    } catch (error) {
        useAPI = false;
        console.log('📴 Backend not reachable. Using offline (localStorage) mode.');
    }
}

// Update header based on auth state
async function updateAuthHeader() {
    try {
        const res = await fetch(`${API_BASE}/auth/me`, { credentials: 'include' });
        if (res.ok) {
            const data = await res.json();
            const user = data.data;
            const signInBtn = document.getElementById('sign-in-btn');
            if (signInBtn) {
                signInBtn.href = 'profile.html';
                signInBtn.innerHTML = `<i class="fa-solid fa-user"></i> ${user.name.split(' ')[0]}`;
            }
            // Update mobile menu sign in button too
            const mobileSignIn = document.querySelector('.mobile-menu .btn');
            if (mobileSignIn) {
                mobileSignIn.href = 'profile.html';
                mobileSignIn.innerHTML = `<i class="fa-solid fa-user"></i> ${user.name.split(' ')[0]}`;
            }
        }
    } catch (e) { /* not logged in */ }
}

// Sync localStorage cart items to backend when connection is established
async function syncLocalCartToBackend() {
    const localCart = JSON.parse(localStorage.getItem('foodieCart')) || [];
    if (localCart.length === 0) return;

    try {
        // Get products to find IDs
        const response = await fetch(`${API_BASE}/products`, { credentials: 'include' });
        const productsData = await response.json();
        const products = productsData.data;

        for (const item of localCart) {
            const product = products.find(p => p.name === item.name);
            if (product) {
                await fetch(`${API_BASE}/cart`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ product_id: product.id, quantity: 1 })
                });
            }
        }

        // Clear localStorage cart after sync
        localStorage.removeItem('foodieCart');
        cart = [];
        console.log('🔄 Local cart synced to backend');
        updateCartCount();
    } catch (error) {
        console.log('Could not sync cart:', error.message);
    }
}

// ==========================================
// MOBILE MENU TOGGLE
// ==========================================
function initializeCart() {
    updateCartCount();
}

hamburgerMenu.addEventListener('click', (e) => {
    e.preventDefault();
    mobileMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.mobile-menu a').forEach(link => {
    link.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
    });
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.navbar')) {
        mobileMenu.classList.remove('active');
    }
});

// ==========================================
// CART FUNCTIONALITY
// ==========================================
function attachEventListeners() {
    addToCartButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const productId = button.getAttribute('data-product-id');
            const itemName = button.getAttribute('data-item');
            const itemPrice = button.getAttribute('data-price');
            const restaurant = button.getAttribute('data-restaurant');

            // Disable button during request
            button.disabled = true;
            button.textContent = '...';

            if (useAPI && productId) {
                await addToCartAPI(parseInt(productId), itemName, button);
            } else if (useAPI && !productId) {
                // Fallback: find product by name if no ID
                await addToCartByName(itemName, button);
            } else {
                addToCartLocal({
                    name: itemName,
                    price: parseInt(itemPrice),
                    restaurant: restaurant,
                    id: Date.now()
                });
            }

            // Visual feedback
            button.textContent = '✓ Added';
            button.style.background = 'var(--lead)';
            button.disabled = false;

            setTimeout(() => {
                button.textContent = 'Add';
                button.style.background = 'var(--gold-finger)';
            }, 1500);
        });
    });
}

// Add to cart via API — directly using product ID
async function addToCartAPI(productId, name, button) {
    try {
        const response = await fetch(`${API_BASE}/cart`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });

        const result = await response.json();

        if (response.ok) {
            showNotification(result.message || `${name} added to cart!`);
        } else {
            showNotification(result.error || 'Could not add to cart');
        }
        updateCartCount();
    } catch (error) {
        console.error('API cart error, falling back to local:', error);
        addToCartLocal({ name, price: 0, restaurant: '', id: Date.now() });
    }
}

// Fallback: find product by name if no data-product-id
async function addToCartByName(name, button) {
    try {
        const response = await fetch(`${API_BASE}/products`, { credentials: 'include' });
        const productsData = await response.json();
        const product = productsData.data.find(p => p.name === name);

        if (product) {
            await addToCartAPI(product.id, name, button);
        } else {
            showNotification('Product not found');
        }
    } catch (error) {
        console.error('Could not find product:', error);
    }
}

// Add to cart via localStorage (fallback)
function addToCartLocal(newItem) {
    // Ensure item has a numeric id assigned
    if (!newItem.id) {
        newItem.id = Date.now();
    }
    
    // Check if item already exists in the cart by name
    const existingIndex = cart.findIndex(item => item.name === newItem.name);
    if (existingIndex > -1) {
        // Increment quantity if property exists, else set it to 2
        cart[existingIndex].qty = (cart[existingIndex].qty || 1) + 1;
    } else {
        // First time adding, set qty to 1
        newItem.qty = 1;
        cart.push(newItem);
    }
    saveCartLocal();
    updateCartCount();
    showNotification(`${newItem.name} added to cart!`);
}

function saveCartLocal() {
    localStorage.setItem('foodieCart', JSON.stringify(cart));
}

// Update cart count in header
async function updateCartCount() {
    let count = 0;

    if (useAPI) {
        try {
            const response = await fetch(`${API_BASE}/cart`, { credentials: 'include' });
            if (response.ok) {
                const data = await response.json();
                count = data.data.summary.item_count;
            }
        } catch (error) {
            count = cart.length;
        }
    } else {
        const itemQuantity = cart.reduce((sum, item) => sum + (item.qty || 1), 0);
        count = itemQuantity;
    }

    cartValue.textContent = count;

    // Animate cart icon
    cartIcon.style.transform = 'scale(1.2)';
    setTimeout(() => {
        cartIcon.style.transform = 'scale(1)';
    }, 300);
}

// ==========================================
// NOTIFICATION SYSTEM
// ==========================================
function showNotification(message) {
    const existingNotification = document.querySelector('.success-message');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = 'success-message';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// ==========================================
// NEWSLETTER SUBSCRIPTION
// ==========================================
async function subscribeNewsletter() {
    const emailInput = document.getElementById('newsletter-email');
    const email = emailInput.value.trim();

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email) {
        showNotification('Please enter your email address');
        return;
    }

    if (!emailRegex.test(email)) {
        showNotification('Please enter a valid email address');
        return;
    }

    if (useAPI) {
        try {
            const response = await fetch(`${API_BASE}/newsletter`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ email })
            });
            const result = await response.json();
            showNotification(result.message || `✓ Subscribed! Check ${email} for offers.`);
            emailInput.value = '';
            return;
        } catch (error) {
            console.log('API newsletter failed, using localStorage');
        }
    }

    // Fallback to localStorage
    let subscribers = JSON.parse(localStorage.getItem('subscribers')) || [];
    subscribers.push({ email, date: new Date().toISOString() });
    localStorage.setItem('subscribers', JSON.stringify(subscribers));
    showNotification(`✓ Subscribed! Check ${email} for offers.`);
    emailInput.value = '';
}

// ==========================================
// CART ICON CLICK - VIEW CART IN DRAWER
// ==========================================
cartIcon.addEventListener('click', async (e) => {
    e.preventDefault();
    
    // Open Drawer
    document.getElementById('foodie-overlay').classList.add('active');
    document.getElementById('cart-drawer').classList.add('active');
    
    const drawerBody = document.getElementById('cart-drawer-body');
    const drawerFooter = document.getElementById('cart-drawer-footer');
    
    drawerBody.innerHTML = '<div style="text-align:center; padding: 2rem;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i></div>';
    drawerFooter.innerHTML = '';

    let items = [];
    let summary = {};

    if (useAPI) {
        try {
            const response = await fetch(`${API_BASE}/cart`, { credentials: 'include' });
            const data = await response.json();
            items = data.data.items.map(i => ({ 
                name: i.product_name, 
                price: i.price, 
                restaurant: i.restaurant_name,
                qty: i.quantity
            }));
            summary = {
                subtotal: data.data.summary.subtotal,
                deliveryFee: data.data.summary.delivery_fee,
                tax: data.data.summary.tax,
                total: data.data.summary.total
            };
        } catch (error) {
            console.log('API cart view failed, using local');
            useAPI = false; // Fallback to local
        }
    }

    if (!useAPI) {
        // Fallback or Local Processing
        if (cart.length === 0) {
            drawerBody.innerHTML = '<div style="text-align:center; padding: 2rem;"><p>Your cart is empty!</p></div>';
            return;
        }
        
        // Group identical items locally if needed, for simplicity we treat each as qty 1 in array
        let grouped = {};
        cart.forEach(item => {
            if(grouped[item.name]) {
                grouped[item.name].qty += (item.qty || 1);
            } else {
                grouped[item.name] = { ...item, qty: item.qty || 1 };
            }
        });
        
        items = Object.values(grouped);
        
        const subtotal = items.reduce((sum, item) => sum + (item.price * item.qty), 0);
        summary = {
            subtotal: subtotal,
            deliveryFee: 50,
            tax: Math.round(subtotal * 0.05),
            total: subtotal + 50 + Math.round(subtotal * 0.05)
        };
    }

    if(items.length === 0) {
        drawerBody.innerHTML = '<div style="text-align:center; padding: 2rem;"><p>Your cart is empty!</p></div>';
        return;
    }

    // Render Items
    drawerBody.innerHTML = items.map(item => `
        <div class="drawer-cart-item">
            <div class="drawer-cart-info">
                <h4>${item.name}</h4>
                <p>${item.restaurant} (x${item.qty})</p>
            </div>
            <div class="drawer-cart-price">₹${item.price * item.qty}</div>
        </div>
    `).join('');

    // Render footer
    drawerFooter.innerHTML = `
        <div class="drawer-summary-row"><span>Subtotal</span><span>₹${summary.subtotal}</span></div>
        <div class="drawer-summary-row"><span>Delivery Fee</span><span>₹${summary.deliveryFee}</span></div>
        <div class="drawer-summary-row"><span>Tax</span><span>₹${summary.tax}</span></div>
        <div class="drawer-summary-row total"><span>Total</span><span>₹${summary.total}</span></div>
        <button class="btn btn-checkout" onclick="window.location.href='cart.html'">Proceed to Checkout</button>
    `;

});

// ==========================================
// SMOOTH SCROLLING FOR ANCHOR LINKS
// ==========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');

        if (href === '#' || !document.querySelector(href)) {
            return;
        }

        e.preventDefault();
        const section = document.querySelector(href);

        if (section) {
            section.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==========================================
// RESTAURANT MENU BUTTONS - VIEW MENU MODAL
// ==========================================
function loadMenuLinks() {
    document.querySelectorAll('.view-menu').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const restaurantName = button.closest('.restaurant-card').querySelector('h3').textContent;
            
            // Open Modal UI
            document.getElementById('foodie-overlay').classList.add('active');
            const menuModal = document.getElementById('menu-modal');
            menuModal.classList.add('active');
            
            document.getElementById('menu-modal-title').textContent = `${restaurantName} Menu`;
            const modalBody = document.getElementById('menu-modal-body');
            modalBody.innerHTML = '<div style="text-align:center; padding: 2rem;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i></div>';

            if (useAPI) {
                try {
                    const response = await fetch(`${API_BASE}/restaurants`, { credentials: 'include' });
                    const data = await response.json();
                    const restaurant = data.data.find(r => r.name === restaurantName);

                    if (restaurant) {
                        const menuResponse = await fetch(`${API_BASE}/restaurants/${restaurant.id}`, { credentials: 'include' });
                        const menuData = await menuResponse.json();
                        const products = menuData.data.products || [];

                        if (products.length > 0) {
                            modalBody.innerHTML = products.map((p) => `
                                <div class="menu-item-row">
                                    <div class="menu-item-info">
                                        <h4>${p.name}</h4>
                                        <p>${p.description}</p>
                                        <span class="item-rating">⭐ ${p.rating} (${p.review_count})</span>
                                    </div>
                                    <div class="menu-item-action">
                                        <span>₹${p.price}</span>
                                        <button class="btn-add-cart" style="padding: 0.4rem 0.8rem;" onclick="window.addToCartFromModal(${p.id}, '${p.name}', ${p.price}, '${restaurantName}', this)">Add</button>
                                    </div>
                                </div>
                            `).join('');
                            return;
                        }
                    }
                } catch (error) {
                    console.log('API menu fetch failed');
                }
            }

            modalBody.innerHTML = `<p style="text-align: center; padding: 2rem;">Could not load menu for ${restaurantName}. Please try again later.</p>`;
        });
    });
}

// Global scope adapter for inline click handlers in modal
window.addToCartFromModal = async function(id, name, price, restaurant, btnElement) {
    btnElement.disabled = true;
    btnElement.textContent = '...';

    if (useAPI) {
        await addToCartAPI(id, name, btnElement);
    } else {
        addToCartLocal({ name, price, restaurant, id: Date.now() });
    }

    btnElement.textContent = '✓ Added';
    btnElement.style.background = 'var(--lead)';
    btnElement.disabled = false;

    setTimeout(() => {
        btnElement.textContent = 'Add';
        btnElement.style.background = 'var(--gold-finger)';
    }, 1500);
}

// ==========================================
// CATEGORY CARDS - FILTER FUNCTIONALITY
// ==========================================
document.querySelectorAll('.category-card').forEach(card => {
    card.addEventListener('click', async function() {
        const categoryName = this.querySelector('h3').textContent;

        if (useAPI) {
            try {
                const response = await fetch(`${API_BASE}/products?category=${encodeURIComponent(categoryName)}`, { credentials: 'include' });
                const data = await response.json();

                if (data.data.length > 0) {
                    showNotification(`Found ${data.count} ${categoryName} items!`);
                } else {
                    showNotification(`Showing ${categoryName} restaurants...`);
                }
                return;
            } catch (error) {
                console.log('API category filter failed');
            }
        }

        showNotification(`Showing ${categoryName} restaurants...`);
    });
});

// ==========================================
// KEYBOARD SHORTCUTS
// ==========================================
document.addEventListener('keydown', (e) => {
    // Press 'C' to show cart (only when not typing in an input)
    if (e.key.toLowerCase() === 'c' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
        cartIcon.click();
    }

    // Press 'Escape' to close mobile menu
    if (e.key === 'Escape') {
        mobileMenu.classList.remove('active');
    }
});

// ==========================================
// PAGE PERFORMANCE OPTIMIZATION
// ==========================================
window.addEventListener('load', () => {
    console.log('🍕 Foodie Website Loaded Successfully!');
    console.log(`📦 Cart Items: ${cart.length}`);
    console.log(`💰 Total Value: ₹${cart.reduce((sum, item) => sum + item.price, 0)}`);
    console.log(`🔗 Backend: ${useAPI ? 'Connected' : 'Offline (localStorage mode)'}`);
});

// ==========================================
// SERVICE WORKER REGISTRATION (Future PWA Feature)
// ==========================================
if ('serviceWorker' in navigator) {
    // Uncomment when service worker is ready
    // navigator.serviceWorker.register('sw.js');
}

// ==========================================
// ANALYTICS TRACKING (Placeholder)
// ==========================================
function trackEvent(eventName, eventData) {
    console.log(`📊 Event: ${eventName}`, eventData);
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================
function formatCurrency(amount) {
    return `₹${amount.toLocaleString('en-IN')}`;
}

function getCartSummary() {
    const subtotal = cart.reduce((sum, item) => sum + item.price, 0);
    const deliveryFee = 50;
    const tax = Math.round(subtotal * 0.05);

    return {
        subtotal,
        deliveryFee,
        tax,
        total: subtotal + deliveryFee + tax,
        itemCount: cart.length
    };
}

// Export for debugging
window.foodieDebug = {
    getCart: () => cart,
    clearCart: async () => {
        if (useAPI) {
            try {
                await fetch(`${API_BASE}/cart`, {
                    method: 'DELETE',
                    credentials: 'include'
                });
            } catch (e) { /* fallback below */ }
        }
        cart = [];
        saveCartLocal();
        updateCartCount();
        showNotification('Cart cleared!');
    },
    getCartSummary: getCartSummary,
    isBackendConnected: () => useAPI,
    addTestItems: () => {
        const testItems = [
            { name: 'Test Pizza', price: 399, restaurant: 'Pizza Paradise', id: Date.now() },
            { name: 'Test Burger', price: 199, restaurant: 'Burger Barn', id: Date.now() + 1 }
        ];
        testItems.forEach(item => addToCartLocal(item));
    }
};

console.log('💡 Tip: Use window.foodieDebug for debugging. Try foodieDebug.isBackendConnected()');
