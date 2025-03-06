from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skincare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class SkincareRoutine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    steps = db.relationship('SkincareStep', backref='routine', lazy=True, cascade="all, delete-orphan")

class SkincareStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('skincare_routine.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

# Routes
@app.route('/routines', methods=['POST'])
def create_routine():
    data = request.json
    routine = SkincareRoutine(name=data['name'])
    db.session.add(routine)
    db.session.commit()
    return jsonify({"id": routine.id, "name": routine.name}), 201

@app.route('/routines/<int:routine_id>/steps', methods=['POST'])
def add_step(routine_id):
    data = request.json
    step = SkincareStep(routine_id=routine_id, step_number=data['step_number'],
                        product_name=data['product_name'], description=data.get('description'))
    db.session.add(step)
    db.session.commit()
    return jsonify({"id": step.id, "product_name": step.product_name, "step_number": step.step_number}), 201

@app.route('/routines/<int:routine_id>', methods=['GET'])
def get_routine(routine_id):
    routine = SkincareRoutine.query.get_or_404(routine_id)
    steps = SkincareStep.query.filter_by(routine_id=routine.id).order_by(SkincareStep.step_number).all()
    return jsonify({
        "id": routine.id,
        "name": routine.name,
        "steps": [{"step_number": s.step_number, "product_name": s.product_name, "description": s.description} for s in steps]
    })

@app.route('/routines/<int:routine_id>/steps/<int:step_id>', methods=['PUT'])
def update_step(routine_id, step_id):
    step = SkincareStep.query.filter_by(id=step_id, routine_id=routine_id).first_or_404()
    data = request.json
    step.step_number = data.get('step_number', step.step_number)
    step.product_name = data.get('product_name', step.product_name)
    step.description = data.get('description', step.description)
    db.session.commit()
    return jsonify({"id": step.id, "product_name": step.product_name, "step_number": step.step_number})

@app.route('/routines/<int:routine_id>', methods=['DELETE'])
def delete_routine(routine_id):
    routine = SkincareRoutine.query.get_or_404(routine_id)
    db.session.delete(routine)
    db.session.commit()
    return jsonify({"message": "Routine deleted successfully"})

@app.route('/routines/<int:routine_id>/steps/<int:step_id>', methods=['DELETE'])
def delete_step(routine_id, step_id):
    step = SkincareStep.query.filter_by(id=step_id, routine_id=routine_id).first_or_404()
    db.session.delete(step)
    db.session.commit()
    return jsonify({"message": "Step deleted successfully"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
