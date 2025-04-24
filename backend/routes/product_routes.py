from flask import Blueprint, request, jsonify
from models.product import Product
from backend.data_store import add_product, get_product_by_id, get_product_by_name, get_user

product_routes = Blueprint("product_routes", __name__)

# Get product info by ID
@product_routes.route("/product/<int:product_id>", methods=["GET"])
def fetch_product_by_id(product_id):
    product = get_product_by_id(product_id)
    if product:
        return jsonify(product.to_dict()), 200
    return jsonify({"error": "Product not found"}), 404

# Get product info by name
@product_routes.route("/product/name/<string:product_name>", methods=["GET"])
def fetch_product_by_name(product_name):
    product = get_product_by_name(product_name)
    if product:
        return jsonify(product.to_dict()), 200
    return jsonify({"error": "Product not found"}), 404

@product_routes.route("/products", methods=["GET"])
def get_all_products():
    # Incorrect: return jsonify([p.to_dict() for p in get_product_by_id.values()]), 200
    # Correct:
    from backend.data_store import products_by_id
    return jsonify([p.to_dict() for p in products_by_id.values()]), 200

# Fix in add_new_product function - add a return statement
@product_routes.route("/product", methods=["POST"])
def add_new_product():
    data = request.json
    try:
        product = Product(**data)
        add_product(product)  # Save product using data_store.py
        return jsonify(product.to_dict()), 201  # Add this return statement
    except TypeError as e:
        return jsonify({"error": str(e)}), 400

# Save a favorite product by user_id
@product_routes.route("/user/<int:user_id>/favorites", methods=["POST"])
def save_favorite(user_id):
    data = request.json
    product_name = data.get("productName")

    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    product = get_product_by_name(product_name)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    user.fav_products.append(product)
    return jsonify({"message": f"Product '{product_name}' added to favorites"}), 201
