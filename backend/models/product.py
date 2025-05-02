import json
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# Create the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Configure your database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Assuming db is already initialized with:
# db = SQLAlchemy(app)

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

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
    
    def get_product_info(self):
        # return all of the information of one product in json format
        return json.dumps(self.to_dict())