from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import certifi
import os
import mongomock

# Load env vars
load_dotenv()

app = Flask(__name__)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/testdb")
mongo = PyMongo(app, tlsCAFile=certifi.where())
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")


class MongoAdapter:
    def __init__(self, app):
        self.app = app
        self._client = None

    @property
    def db(self):
        if self.app.config.get("TESTING"):
            if self._client is None:
                self._client = mongomock.MongoClient()
            db_name = self.app.config.get("MONGO_DBNAME") or self._get_db_name_from_uri()
            return self._client[db_name]

        if self._client is None:
            self._client = self._create_pymongo_client()
        return self._client.db

    @property
    def cx(self):
        if self.app.config.get("TESTING"):
            if self._client is None:
                self._client = mongomock.MongoClient()
            return self._client
        if self._client is None:
            self._client = self._create_pymongo_client()
        return self._client.cx

    def _create_pymongo_client(self):
        mongo_uri = self.app.config.get("MONGO_URI", "")
        use_tls = (
            mongo_uri.startswith("mongodb+srv://")
            or os.getenv("MONGO_TLS", "false").lower() in {"1", "true", "yes", "on"}
        )
        if use_tls:
            return PyMongo(self.app, tlsCAFile=certifi.where())
        return PyMongo(self.app)

    def _get_db_name_from_uri(self):
        mongo_uri = self.app.config.get("MONGO_URI", "")
        if not mongo_uri:
            return "student_db"
        return mongo_uri.rstrip("/").split("/")[-1] or "student_db"


# Use certifi CA bundle explicitly for cross-platform TLS reliability
# (notably fixes common macOS certificate verification failures).
mongo = MongoAdapter(app)

# Home page -> list students
@app.route('/')
def index():
    students = mongo.db.students.find()
    return render_template('index.html', students=students)

# Add student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        mongo.db.students.insert_one({
            "name": name,
            "email": email,
            "course": course
        })
        return redirect(url_for('index'))
    return render_template('add_student.html')

# Update student
@app.route('/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        new_course = request.form['course']
        mongo.db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"name": new_name, "email": new_email, "course": new_course}}
        )
        return redirect(url_for('index'))
    return render_template('update_student.html', student=student)


# Delete student
@app.route('/delete/<student_id>')
def delete_student(student_id):
    mongo.db.students.delete_one({"_id": ObjectId(student_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)


