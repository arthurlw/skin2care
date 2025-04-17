from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
DB_NAME = "tasks.db"

# Helper function to interact with the database
def query_db(query, args=(), fetch_one=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    data = cursor.fetchone() if fetch_one else cursor.fetchall()
    conn.commit()
    conn.close()
    return data

@app.route("/")
def index():
    tasks = query_db("SELECT * FROM tasks")
    return render_template("index.html", tasks=tasks)

# GET all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = query_db("SELECT * FROM tasks")
    return jsonify([dict(task) for task in tasks])

@app.route("/survey/<int:survey_id>", methods=["GET"])
def get_survey(survey_id):
    # Your survey logic here
    return jsonify({"survey_id": survey_id, "title": "Sample Survey"})

# GET a single task
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), fetch_one=True)
    if task:
        return jsonify(dict(task))
    return jsonify({"error": "Task not found"}), 404

# CREATE a new task
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400
    
    query_db("INSERT INTO tasks (title, description) VALUES (?, ?)", 
             (data["title"], data.get("description", "")))
    
    return jsonify({"message": "Task created successfully"}), 201

# UPDATE a task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    task = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), fetch_one=True)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404

    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    status = data.get("status", task["status"])

    query_db("UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?", 
             (title, description, status, task_id))

    return jsonify({"message": "Task updated successfully"})

# DELETE a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), fetch_one=True)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404

    query_db("DELETE FROM tasks WHERE id = ?", (task_id,))
    return jsonify({"message": "Task deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)
