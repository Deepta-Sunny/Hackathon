"""
E-Commerce Database Schema
==========================
Mock database schema for realistic e-commerce chatbot testing
"""

# Sample E-Commerce Database Schema
ECOMMERCE_DB_SCHEMA = {
    "products": [
        {
            "product_id": "PROD001",
            "name": "Wireless Bluetooth Headphones",
            "category": "Electronics",
            "price": 79.99,
            "stock": 150,
            "description": "Premium noise-cancelling wireless headphones with 30-hour battery life",
            "brand": "AudioTech",
            "rating": 4.5
        },
        {
            "product_id": "PROD002",
            "name": "Smart Fitness Watch",
            "category": "Electronics",
            "price": 199.99,
            "stock": 85,
            "description": "Advanced fitness tracker with heart rate monitoring and GPS",
            "brand": "FitPro",
            "rating": 4.7
        },
        {
            "product_id": "PROD003",
            "name": "Organic Cotton T-Shirt",
            "category": "Clothing",
            "price": 24.99,
            "stock": 200,
            "description": "100% organic cotton, eco-friendly, available in multiple colors",
            "brand": "EcoWear",
            "rating": 4.3
        },
        {
            "product_id": "PROD004",
            "name": "Stainless Steel Water Bottle",
            "category": "Home & Kitchen",
            "price": 29.99,
            "stock": 120,
            "description": "Insulated water bottle keeps drinks cold for 24 hours",
            "brand": "HydroLife",
            "rating": 4.6
        },
        {
            "product_id": "PROD005",
            "name": "Yoga Mat Premium",
            "category": "Sports",
            "price": 39.99,
            "stock": 95,
            "description": "Extra thick non-slip yoga mat with carrying strap",
            "brand": "ZenFit",
            "rating": 4.4
        }
    ],
    
    "orders": [
        {
            "order_id": "ORD2024001",
            "customer_id": "CUST001",
            "customer_name": "John Smith",
            "items": [
                {"product_id": "PROD001", "quantity": 1, "price": 79.99}
            ],
            "total_amount": 79.99,
            "status": "Delivered",
            "order_date": "2024-01-15",
            "delivery_date": "2024-01-18",
            "shipping_address": "123 Main St, New York, NY 10001"
        },
        {
            "order_id": "ORD2024002",
            "customer_id": "CUST002",
            "customer_name": "Sarah Johnson",
            "items": [
                {"product_id": "PROD002", "quantity": 1, "price": 199.99},
                {"product_id": "PROD005", "quantity": 1, "price": 39.99}
            ],
            "total_amount": 239.98,
            "status": "In Transit",
            "order_date": "2024-01-20",
            "estimated_delivery": "2024-01-25",
            "shipping_address": "456 Oak Ave, Los Angeles, CA 90001"
        },
        {
            "order_id": "ORD2024003",
            "customer_id": "CUST003",
            "customer_name": "Mike Davis",
            "items": [
                {"product_id": "PROD003", "quantity": 3, "price": 74.97},
                {"product_id": "PROD004", "quantity": 2, "price": 59.98}
            ],
            "total_amount": 134.95,
            "status": "Processing",
            "order_date": "2024-01-22",
            "estimated_delivery": "2024-01-27",
            "shipping_address": "789 Pine Rd, Chicago, IL 60601"
        }
    ],
    
    "customers": [
        {
            "customer_id": "CUST001",
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "+1-555-0101",
            "loyalty_points": 250,
            "member_since": "2023-06-15"
        },
        {
            "customer_id": "CUST002",
            "name": "Sarah Johnson",
            "email": "sarah.j@email.com",
            "phone": "+1-555-0202",
            "loyalty_points": 580,
            "member_since": "2022-11-20"
        },
        {
            "customer_id": "CUST003",
            "name": "Mike Davis",
            "email": "mike.davis@email.com",
            "phone": "+1-555-0303",
            "loyalty_points": 120,
            "member_since": "2024-01-10"
        }
    ],
    
    "payment_methods": [
        "Credit Card (Visa, Mastercard, Amex)",
        "PayPal",
        "Apple Pay",
        "Google Pay",
        "Bank Transfer"
    ],
    
    "shipping_options": [
        {"method": "Standard Shipping", "cost": 5.99, "days": "5-7 business days"},
        {"method": "Express Shipping", "cost": 12.99, "days": "2-3 business days"},
        {"method": "Overnight Shipping", "cost": 24.99, "days": "1 business day"},
        {"method": "Free Shipping", "cost": 0.00, "days": "7-10 business days (orders over $50)"}
    ],
    
    "return_policy": {
        "return_window_days": 30,
        "conditions": "Items must be unused and in original packaging",
        "refund_method": "Original payment method",
        "processing_time": "5-7 business days after receipt"
    }
}


def get_product_by_id(product_id: str):
    """Get product details by ID"""
    for product in ECOMMERCE_DB_SCHEMA["products"]:
        if product["product_id"] == product_id:
            return product
    return None


def get_products_by_category(category: str):
    """Get all products in a category"""
    return [p for p in ECOMMERCE_DB_SCHEMA["products"] if p["category"].lower() == category.lower()]


def get_order_by_id(order_id: str):
    """Get order details by ID"""
    for order in ECOMMERCE_DB_SCHEMA["orders"]:
        if order["order_id"] == order_id:
            return order
    return None


def get_customer_by_id(customer_id: str):
    """Get customer details by ID"""
    for customer in ECOMMERCE_DB_SCHEMA["customers"]:
        if customer["customer_id"] == customer_id:
            return customer
    return None


def search_products(query: str):
    """Search products by name or description"""
    query_lower = query.lower()
    results = []
    for product in ECOMMERCE_DB_SCHEMA["products"]:
        if (query_lower in product["name"].lower() or 
            query_lower in product["description"].lower() or
            query_lower in product["category"].lower()):
            results.append(product)
    return results
