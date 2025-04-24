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
    password = db.Column(db.String, nullable=False) 
    gender = db.Column(db.String)
    skin_type = db.Column(db.String)
    age = db.Column(db.Integer)
    notifications = db.Column(db.Boolean, default=False)
    email = db.Column(db.String, unique=True, nullable=False)
    products = db.Column(db.String) 
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
    type = db.Column(db.String) 
    is_read = db.Column(db.Boolean, default=False)
    product_id = db.Column(db.String, nullable=True) 
    created_at = db.Column(db.String, default=lambda: datetime.now().isoformat())
    expires_at = db.Column(db.String, nullable=True)

    user = db.relationship('User', backref=db.backref('user_notifications', lazy=True))

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
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
        
    
    required_fields = ['username', 'password', 'email', 'user_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 409
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409
    

    new_user = User(
        user_id=data['user_id'],
        username=data['username'],
        password=data['password'],
        email=data['email'],
        gender=data.get('gender'),
        skin_type=data.get('skin_type'),
        age=data.get('age'),
        notifications=data.get('notifications', False),
        products=data.get('products'),
        survey_id=data.get('survey_id'),
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully!", "user": new_user.to_dict()}), 201

# GET user's notifications
@app.route('/user/<string:user_id>/notifications', methods=['GET'])
def get_notifications(user_id):
    user_notifications = Notification.query.filter_by(user_id=user_id).all()
    if not user_notifications:
        return jsonify([])
    
    result = []

    for user_notification in user_notifications:
        result.append({
            "id": user_notification.id,
            "user_id": user_notification.user_id,
            "message": user_notification.message
        })
    
    return jsonify(result)

# CREATE a new notification
@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.json

    required_fields = ['user_id', 'message']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    new_notification = Notification(
        user_id=data['user_id'],
        message=data['message'],
        type=data.get('type'),
        is_read=data.get('is_read', False),
        product_id=data.get('product_id'),
        expires_at=data.get('expires_at'),
        created_at=datetime.now().isoformat()
    )

    db.session.add(new_notification)
    db.session.commit()

    return jsonify({
        "message": "Notification created successfully!",
        "notification": new_notification.to_dict()
    }), 201


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
@app.route('/user/<string:user_id>/email', methods=['PUT'])
def change_email(user_id):
    data = request.json
    
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    
    new_email = data['email']
    
    
    existing_email = User.query.filter(User.email == new_email, User.id != user_id).first()
    if existing_email:
        return jsonify({"error": "Email is already in use"}), 409
    
    
    # user = User.query.get(user_id)
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    
    user.email = new_email
    user.updated_at = datetime.now().isoformat()
    
    
    db.session.commit()
    
    return jsonify({
        "message": "Email updated successfully",
        "user": user.to_dict()
    })

# PUT User's Password
@app.route('/user/<string:user_id>/password', methods=['PUT'])
def change_password(user_id):
    data = request.json
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({"error": "Current password and new password are required"}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']

    # user = User.query.get(user_id)
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.password != current_password:
        return jsonify({"error": "Current password is incorrect"}), 401
    
    
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    
    user.password = new_password 
    user.updated_at = datetime.now().isoformat()
    
    
    db.session.commit()
    
    return jsonify({
        "message": "Password updated successfully"
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



