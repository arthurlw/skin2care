from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)  # Consider password hashing
    gender = db.Column(db.String)
    skin_type = db.Column(db.String)
    age = db.Column(db.Integer)
    notifications = db.Column(db.Boolean, default=False)
    email = db.Column(db.String, unique=True, nullable=False)
    products = db.Column(db.String)  # Could store as JSON string or consider a relationship
    survey_id = db.Column(db.Integer)
    created_at = db.Column(db.String)
    updated_at = db.Column(db.String)

    def to_dict(self):
        return {
            "userId": self.user_id,
            "username": self.username,
            "password": self.password,
            "gender": self.gender,
            "skinType": self.skin_type,
            "age": self.age,
            "notifications": self.notifications,
            "email": self.email,
            "fav_products": self.products,
            "survey_id": self.survey_id
        }
    
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    message = db.Column(db.String, nullable=False)
    type = db.Column(db.String)  # e.g., "deal", "reminder", "product_update"
    is_read = db.Column(db.Boolean, default=False)
    product_id = db.Column(db.String, nullable=True)  # If notification is about a specific product
    created_at = db.Column(db.String, default=lambda: datetime.now().isoformat())
    expires_at = db.Column(db.String, nullable=True)  # Optional expiration time

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "type": self.type,
            "is_read": self.is_read,
            "product_id": self.product_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }


# CREATES user account
@app.route('/user', methods=['POST'])
def create_user():
    data = request.json

    if not data or 'user' not in data:
        return jsonify({"error: User does not exist"}), 400
    
    new_user = User(user=data['user'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"})

# GET user's notifications
@app.route('/user/<int:user_id>/notifications', methods=['GET'])
def get_notifications(user_id):
    user_notifications = Notification.query.filter_by(user_id=user_id).all()
    if not user_notifications:
        return jsonify([])
    
    result = []

    for user_notification in user_notifications:
        result.append({
            "user_id": user_notification.user_id,
            "message": user_notification.message
        })
    
    return jsonify(result)


# DELETE user's notifications
@app.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    notification = Notification.query.get(notification_id)

    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    

    db.session.delete(notification)
    db.session.commit()

    return jsonify({"message": "Notification deleted successfully!"})

# PUT User's email
@app.route('/user/<int:user_id>/email', methods=['PUT'])
def change_email(user_id):
    data = request.json
    
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    
    new_email = data['email']
    
    # Check if email is already in use by another user
    existing_email = User.query.filter(User.email == new_email, User.id != user_id).first()
    if existing_email:
        return jsonify({"error": "Email is already in use"}), 409
    
    # Find the user by ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Update the email
    user.email = new_email
    user.updated_at = datetime.now().isoformat()
    
    # Save changes
    db.session.commit()
    
    return jsonify({
        "message": "Email updated successfully",
        "user": user.to_dict()
    })

# PUT User's Password
@app.route('/user/<int:user_id>/password', methods=['PUT'])
def change_password(user_id):
    # Get data from the request JSON
    data = request.json
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({"error": "Current password and new password are required"}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    # Find the user by ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Verify the current password
    if user.password != current_password:  # In a real app, use proper password verification
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # Validate new password (add your password strength requirements)
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Update the password
    user.password = new_password  # In a real app, hash the password before storing
    user.updated_at = datetime.now().isoformat()
    
    # Save changes
    db.session.commit()
    
    return jsonify({
        "message": "Password updated successfully"
    })



