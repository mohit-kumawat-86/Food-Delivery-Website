import requests, json, sys
BASE='http://127.0.0.1:5000'
s = requests.Session()
# Register user
reg = s.post(f'{BASE}/api/auth/register', json={
    'name':'Test User',
    'email':'testuser@example.com',
    'password':'test1234'
})
print('Register status', reg.status_code)
print(reg.json())
# Login
login = s.post(f'{BASE}/api/auth/login', json={'email':'testuser@example.com','password':'test1234'})
print('Login status', login.status_code)
print(login.json())
# Get products
prod_resp = s.get(f'{BASE}/api/products')
products = prod_resp.json().get('data', [])
if not products:
    print('No products found')
    sys.exit(0)
product_id = products[0]['id']
print('Using product_id', product_id)
# Add to cart
add = s.post(f'{BASE}/api/cart', json={'product_id': product_id, 'quantity':2})
print('Add to cart status', add.status_code)
print(add.json())
# Get cart
cart = s.get(f'{BASE}/api/cart')
print('Cart GET status', cart.status_code)
print(json.dumps(cart.json(), indent=2))
# Place order
order = s.post(f'{BASE}/api/orders', json={})
print('Place order status', order.status_code)
print(order.json())
