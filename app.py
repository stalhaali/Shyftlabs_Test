from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SECRET_KEY'] = secrets.token_hex(16)
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(50), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.String(1), nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = relationship('Student', backref='results')

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = relationship('Course', backref='results')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        first_name = request.form['first_name']
        family_name = request.form['family_name']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()

        today = datetime.now().date()
        age_limit_date = today - timedelta(days=(10 * 365))
        
        if dob > age_limit_date:
            flash('Students must be at least 10 years old.', 'error')
            return redirect(url_for('students'))

        new_student = Student(first_name=first_name, family_name=family_name, dob=dob)

        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully.', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Failed to add student.', 'error')
            return redirect(url_for('students'))

    students = Student.query.all()
    return render_template('students.html', students=students)


@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        course_name = request.form['course_name']

        new_course = Course(course_name=course_name)

        try:
            db.session.add(new_course)
            db.session.commit()
            flash('Course added successfully.', 'success')
            return redirect(url_for('courses'))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Failed to add course.', 'error')
            return redirect(url_for('courses'))

    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/results', methods=['GET', 'POST'])
def results():

    if request.method == 'POST':
        course_name = request.form['course_name']
        student_name = request.form['student_name']
        score = request.form['score']

        student = Student.query.get(student_name)
        course = Course.query.get(course_name)

        new_result = Result(course=course, student=student, score=score)

        try:
            db.session.add(new_result)
            db.session.commit()
            flash('Result added successfully.', 'success')
            return redirect(url_for('results'))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Failed to add result.', 'error')
            return redirect(url_for('results'))

    results = Result.query.all()
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('results.html', results=results, students=students, courses=courses)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
