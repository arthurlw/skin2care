from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    answers = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String)
    updated_at = db.Column(db.String)


@app.route('/survey', methods=['POST'])
def submit_survey():
    data = request.json
    
    if not data or 'answers' not in data:
        return jsonify({"error": "Survey answers are required"}), 400
    
    # new_response = SurveyResponse(answers=data['answers'])
    new_response = SurveyResponse(
    answers=data['answers'],
    user_id=data.get('user_id'),
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat()
)

    db.session.add(new_response)
    db.session.commit()
    
    return jsonify({
        "id": new_response.id,
        "user_id": new_response.user_id,
        "answers": new_response.answers,
        "created_at": new_response.created_at,
        "updated_at": new_response.updated_at
    }), 201

@app.route('/survey', methods=['GET'])
def get_surveys():
    responses = SurveyResponse.query.all()
    result = []
    
    for response in responses:
        result.append({
            "id": response.id,
            "answers": response.answers,
            "created_at": response.created_at,
            "updated_at": response.updated_at
        })
    
    return jsonify(result)

@app.route('/survey/<int:user_id>', methods=['GET'])
def get_survey(user_id):
    response = SurveyResponse.query.get_or_404(user_id)
    
    return jsonify({
        "id": response.id,
        "user_id": response.user_id,
        "answers": response.answers,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    })

@app.route('/survey/<int:user_id>', methods=['PATCH'])
def update_survey(user_id):
    response = SurveyResponse.query.get_or_404(user_id)
    data = request.json
    
    if 'answers' in data:
        response.answers = data['answers']
        db.session.commit()
    
    return jsonify({
        "id": response.id,
        "user_id": response.user_id,
        "answers": response.answers,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    })


@app.route('/survey/<int:user_id>', methods=['DELETE'])
def delete_survey(user_id):
    response = SurveyResponse.query.get_or_404(user_id)
    
    db.session.delete(response)
    db.session.commit()

    return jsonify ({
        "message": "Survey response deleted!",
        "id": user_id
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)