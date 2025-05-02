from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from model.routine import Routine
from routine_example import SkincareStep

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skincare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/routines/<int:routine_id>', methods=['GET'])#Get skincare routine step info
#Should work when Routine class is updated/implemented?
def get_routine(routine_id):#assumes routine_id is id of desired Routine object
    routine = Routine.query.get_or_404(routine_id)
    return jsonify({
        "id": routine.id,
        "name": routine.name,
        "steps": [{"step_number": s, "product_name": routine.products[s].name, "description": routine.products[s].description} for s in range(len(Routine.products))]
    })

@app.route('/routines/<int:routine_id>/steps', methods=['POST'])#Posting a Routine
def post_routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    db.session.add(routine)
    db.session.commit()
    return jsonify({"id": routine_id, "product_name": routine.products[i].name, "step_number": i, "description": routine.products[i].description} for i in range(len(routine.products))) , 201
#ask if above return statement is needed or not

@app.route('/routines/<int:routine_id>/steps', methods=['POST'])#post a step to a routine
def add_step(routine_id):
    data = request.json
    step = SkincareStep(routine_id=routine_id, step_number=data['step_number'],
                        product_name=data['product_name'], description=data.get('description'))
    db.session.add(step)
    db.session.commit()
    return jsonify({"id": step.id, "product_name": step.product_name, "step_number": step.step_number}), 201

@app.route('/routines/<int:routine_id>/steps/<int:step_id>', methods=['DELETE']) #delete a step
def delete_step(routine_id, step_id):
    # Query the step that matches the routine_id and step_id
    step = SkincareStep.query.filter_by(routine_id=routine_id, step_number=step_id).first()

    if not step:
        return jsonify({"error": "Step not found"}), 404
    db.session.delete(step)
    db.session.commit()
    return jsonify({"message": "Step deleted successfully"})

@app.route('/routines/<int:routine_id>/steps/<int:step_id>', methods=['PUT'])#edit step
def update_step(routine_id, step_id):
    # Retrieve the existing step or return 404
    step = SkincareStep.query.filter_by(id=step_id, routine_id=routine_id).first_or_404()
    data = request.json
    step.step_number = data.get('step_number', step.step_number)
    step.product_name = data.get('product_name', step.product_name)
    step.description = data.get('description', step.description)
    db.session.commit()
    return jsonify({"id": step.id, "routine_id": step.routine_id, "step_number": step.step_number, "product_name": step.product_name, "description": step.description})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





