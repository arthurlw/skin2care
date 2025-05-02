import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class Routine:
    def __init__(self, routine_id, username, products, date_created, ):
        self.routine_id = routine_id
        self.username = username
        self.products = products  # List of Product objects
        self.date_created = date_created

# Create the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

# Model definitions (same as before)
class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    brand = db.Column(db.String(255))
    product_type = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            "productId": self.product_id,
            "productName": self.name,
            "productDescription": self.description,
            "productBrand": self.brand,
            "type": self.product_type
        }

class Routine(db.Model):
    __tablename__ = 'routines'
    
    routine_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    
    products = db.relationship("RoutineProduct", back_populates="routine")
    
    def to_dict(self):
        return {
            "routineId": self.routine_id,
            "username": self.username,
            "products": [product.product.to_dict() for product in self.products],
            "dateCreated": self.date_created
        }

    def get_product_info(self):
        # return all of the information of routine in json format
        return json.dumps(self.to_dict())

class RoutineProduct(db.Model):
    __tablename__ = 'routine_products'
    
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routines.routine_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    step_number = db.Column(db.Integer)
    
    routine = db.relationship("Routine", back_populates="products")
    product = db.relationship("Product")

# Define your routes
@app.route('/routines/<int:routine_id>', methods=['GET'])
def get_routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    return jsonify({
        "id": routine.routine_id,
        "username": routine.username,
        "products": [{
            "step_number": i, 
            "product_name": p.product.name,
            "description": p.product.description
        } for i, p in enumerate(routine.products)]
    })


# Alternative way to create tables (outside of request context)
# with app.app_context():
#     db.create_all()
    
#     # Optionally, add some test data
#     # Check if no products exist
#     if Product.query.count() == 0:
#         # Add sample products
#         sample_product = Product(
#             name="Sample Product",
#             description="A sample skincare product",
#             brand="Sample Brand",
#             product_type="Cleanser"
#         )
#         db.session.add(sample_product)
        
#         # Add sample routine
#         sample_routine = Routine(
#             username="test_user",
#             date_created=datetime.now()
#         )
#         db.session.add(sample_routine)
#         db.session.commit()
        
#         # Associate product with routine
#         routine_product = RoutineProduct(
#             routine_id=sample_routine.routine_id,
#             product_id=sample_product.product_id
#         )
#         db.session.add(routine_product)
#         db.session.commit()

@app.route('/routines', methods=['POST'])  # Changed path - no routine_id needed for creation
def post_routine():
    # Get JSON data from request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Extract routine information
    username = data.get('username')
    product_ids = data.get('product_ids', [])  # List of product IDs to add to routine
    
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    # Create new routine
    new_routine = Routine(
        username=username,
        date_created=datetime.now()
    )
    
    db.session.add(new_routine)
    db.session.commit()  # Commit to get the routine_id
    
    # Add products to routine
    for i, product_id in enumerate(product_ids):
        product = Product.query.get(product_id)
        if product:
            routine_product = RoutineProduct(
                routine_id=new_routine.routine_id,
                product_id=product_id
            )
            db.session.add(routine_product)
    
    db.session.commit()
    
    # Return the created routine
    return jsonify({
        "id": new_routine.routine_id,
        "username": new_routine.username,
        "dateCreated": new_routine.date_created,
        "products": [{
            "step_number": i, 
            "product_name": rp.product.name,
            "description": rp.product.description
        } for i, rp in enumerate(new_routine.products)]
    }), 201

@app.route('/routines/<int:routine_id>', methods=['PUT'])
def update_routine_steps(routine_id):
    data = request.get_json()

    if not data or 'product_ids' not in data:
        return jsonify({"error": "product_ids list is required"}), 400

    new_product_ids = data['product_ids']
    routine = Routine.query.get_or_404(routine_id)

    # Fetch current RoutineProducts
    current_steps = RoutineProduct.query.filter_by(routine_id=routine_id).all()
    current_product_ids = [step.product_id for step in current_steps]

    # Delete steps that are no longer in the list
    for step in current_steps:
        if step.product_id not in new_product_ids:
            db.session.delete(step)

    # Add or update steps
    for idx, product_id in enumerate(new_product_ids):
        step = RoutineProduct.query.filter_by(routine_id=routine_id, product_id=product_id).first()
        if not step:
            new_step = RoutineProduct(routine_id=routine_id, product_id=product_id, step_number=idx)
            db.session.add(new_step)
        else:
            step.step_number = idx

    db.session.commit()

    updated_steps = RoutineProduct.query.filter_by(routine_id=routine_id).order_by(RoutineProduct.step_number).all()
    return jsonify({
        "routineId": routine_id,
        "steps": [{
            "step_number": step.step_number,
            "product_id": step.product_id,
            "product_name": step.product.name,
            "description": step.product.description
        } for step in updated_steps]
    }), 200


# Run the app
if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)