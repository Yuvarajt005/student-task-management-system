from flask import Flask, request, jsonify, render_template
import mysql.connector
import bcrypt
from config import DB_CONFIG

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def home():
   return render_template("login.html")

# ================= REGISTER =================
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        name = data['name']
        email = data['email']
        password = data['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        db = get_db()
        cursor = db.cursor()

        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, hashed_password))
        db.commit()

        return jsonify({"message": "User registered successfully"})
    
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    
    email = data['email']
    password = data['password']

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Login successful", "user": user})
    else:
        return jsonify({"message": "Invalid email or password"}), 401


# ================= ADD TASK =================
@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json

    user_id = data['user_id']
    task_title = data['task_title']
    description = data['description']
    due_date = data['due_date']
    priority = data.get('priority', 'low')   # NEW

    db = get_db()
    cursor = db.cursor()

    query = """
    INSERT INTO tasks (user_id, task_title, description, due_date, status, priority)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (user_id, task_title, description, due_date, "pending", priority))
    db.commit()

    return jsonify({"message": "Task added successfully"})


# ================= GET TASKS =================
@app.route('/get_tasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM tasks WHERE user_id=%s ORDER BY id DESC"
    cursor.execute(query, (user_id,))

    tasks = cursor.fetchall()

    return jsonify(tasks)


# ================= UPDATE TASK =================
@app.route('/update_task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json

    status = data.get('status')
    title = data.get('task_title')
    desc = data.get('description')

    db = get_db()
    cursor = db.cursor()

    # Dynamic update
    if status:
        cursor.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, task_id))
    
    if title:
        cursor.execute("UPDATE tasks SET task_title=%s WHERE id=%s", (title, task_id))
    
    if desc:
        cursor.execute("UPDATE tasks SET description=%s WHERE id=%s", (desc, task_id))

    db.commit()

    return jsonify({"message": "Task updated successfully"})


# ================= DELETE TASK =================
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    db.commit()

    return jsonify({"message": "Task deleted successfully"})


# ================= PAGES =================
@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/tasks_page')   # NEW PAGE
def tasks_page():
    return render_template('tasks.html')


# ================= RUN =================
if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
