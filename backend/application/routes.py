from flask import current_app as app, jsonify, request, abort
from .models import *
from flask_jwt_extended import create_access_token, current_user, jwt_required
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from sqlalchemy import and_

#Decorator-Role_Required
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            if current_user.role != required_role:
                return jsonify(message= "Unauthorized"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

#Index route
@app.route("/api/login", methods=["POST"])
def index():
    username=request.json.get("username", None)
    password=request.json.get("password", None)

    if not username or not password:
        return jsonify("Please fill in all fields."), 400
        
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify("User not fond."), 401
        
    if not check_password_hash(user.password_hash, password):
        return jsonify("Incorrect password."), 401

    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token,
                    message="Login Successful!"), 200

#Registration route
@app.route("/api/register_user", methods=["GET", "POST"])
def register_user():
    username = request.json.get("username", None)
    full_name = request.json.get("name", None)
    password = request.json.get("password", None)
    confirm_password = request.json.get("confirm_password", None)
    dob = request.json.get("dob", None)
    qualification = request.json.get("qualification", None)

    if not username or not full_name or not password or not confirm_password or not dob or not qualification:
        return jsonify("Please fill in all fields."), 400
        
    elif password != confirm_password:
        return jsonify("Password do not match."), 401
        
    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify("User already exist."), 401

    password_hash = generate_password_hash(password)
    dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    new_user = User(username=username, full_name=full_name, password_hash=password_hash, qualification=qualification, dob=dob_date)
    db.session.add(new_user)
    db.session.commit()
    return jsonify("User registered successfully."), 201

#Dashboard route
@app.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard_api():
    user = current_user

    if user.role == "user":
        current_date_obj = date.today()
        
        attempted_quiz_ids = db.session.query(Score.quiz_id).filter(Score.user_id == user.id).subquery()

        quizzes = Quiz.query.filter(
            and_(
                db.func.date(Quiz.date_of_quiz) >= current_date_obj,
                ~Quiz.id.in_(attempted_quiz_ids)
            )
        ).all()

        quiz_data = []
        for quiz in quizzes:
            questions_count = db.session.query(Question).filter(Question.quiz_id == quiz.id).count()
            quiz_data.append({
                "id": quiz.id,
                "type": quiz.type,
                "date_of_quiz": quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                "time_duration": quiz.time_duration,
                "remarks": quiz.remarks,
                "chapter_name": quiz.chapter.name,
                "subject_name": quiz.chapter.subject.name,
                "questions_count": questions_count
            })
        return jsonify(
            user_role="user",
            user_details={
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "qualification": user.qualification,
                "dob": user.dob.isoformat() if user.dob else None
            },
            quizzes=quiz_data
        ), 200

    else:
        subjects = db.session.query(Subject).all()
        chapters = db.session.query(Chapter).all()

        subject_data = []
        for subject in subjects:
            subject_data.append({
                "id": subject.id,
                "name": subject.name,
                "description": subject.description
            })

        chapter_data = []
        for chapter in chapters:
            questions_count = db.session.query(Question).join(Quiz).filter(Quiz.chapter_id == chapter.id).count()
            chapter_data.append({
                "id": chapter.id,
                "name": chapter.name,
                "description": chapter.description,
                "subject_name": chapter.subject.name,
                "questions_count": questions_count
            })
        return jsonify(
            user_role="admin",
            user_details={
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "qualification": user.qualification,
                "dob": user.dob.isoformat() if user.dob else None
            },
            subjects=subject_data,
            chapters=chapter_data
        ), 200

#Add subject
@app.route("/api/admin/add_subject", methods=["POST"])
@role_required("admin")
def add_subject_api():
    name = request.json.get("name")
    description = request.json.get("description")

    if not name:
        return jsonify(message="Subject name is required."), 400

    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    return jsonify(message="Subject added successfully.", subject_id=subject.id), 201

#Delete Subject
@app.route("/api/admin/delete_subject/<int:subject_id>", methods=["DELETE"])
@role_required("admin")
def delete_subject_api(subject_id):
    sub = Subject.query.filter_by(id=subject_id).first()

    if not sub:
        return jsonify(message="Subject not found."), 404

    db.session.delete(sub)
    db.session.commit()
    return jsonify(message="Subject deleted successfully."), 200

#Add chapter
@app.route("/api/admin/add_chapter/<int:subject_id>", methods=["POST"])
@role_required("admin")
def add_chapter_api(subject_id):
    name = request.json.get("name")
    description = request.json.get("description")

    if not name:
        return jsonify(message="Chapter name is required."), 400

    chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()
    return jsonify(message="Chapter added successfully.", chapter_id=chapter.id), 201

#Edit chapter
@app.route("/api/admin/edit_chapter/<int:chapter_id>", methods=["PUT"])
@role_required("admin")
def edit_chapter_api(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()

    if not chapter:
        return jsonify(message="Chapter not found."), 404

    name = request.json.get("name")
    description = request.json.get("description")

    if not name:
        return jsonify(message="Chapter name cannot be empty."), 400

    chapter.name = name
    chapter.description = description
    db.session.commit()
    return jsonify(message="Chapter updated successfully."), 200

#Delete chapter
@app.route("/api/admin/delete_chapter/<int:chapter_id>", methods=["DELETE"])
@role_required("admin")
def delete_chapter_api(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()

    if not chapter:
        return jsonify(message="Chapter not found."), 404

    db.session.delete(chapter)
    db.session.commit()
    return jsonify(message="Chapter deleted successfully."), 200

#Quiz management
@app.route("/api/admin/quiz_management", methods=["GET"])
@role_required("admin")
def quiz_management_api():
    user = current_user
    quizzes = db.session.query(Quiz).all()

    quiz_data = []
    for quiz in quizzes:
        questions_count = db.session.query(Question).filter(Question.quiz_id == quiz.id).count()
        quiz_data.append({
            "id": quiz.id,
            "type": quiz.type,
            "chapter_id": quiz.chapter_id,
            "date_of_quiz": quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            "time_duration": quiz.time_duration,
            "remarks": quiz.remarks,
            "chapter_name": quiz.chapter.name,
            "subject_name": quiz.chapter.subject.name,
            "questions_count": questions_count
        })

    return jsonify(
        user_role="admin",
        user_details={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "qualification": user.qualification,
            "dob": user.dob.isoformat() if user.dob else None
        },
        quizzes=quiz_data
    ), 200

#Chapterwise quiz
@app.route("/api/admin/quiz/chapter/<int:chapter_id>", methods=["GET"])
@role_required("admin")
def chapterwise_quiz_api(chapter_id):
    user = current_user
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

    if not quizzes:
        return jsonify(message="No quizzes found for this chapter."), 404

    quiz_data = []
    for quiz_item in quizzes: # Renamed 'quiz' to 'quiz_item' to avoid conflict with the Quiz model name
        questions_count = db.session.query(Question).filter(Question.quiz_id == quiz_item.id).count()
        quiz_data.append({
            "id": quiz_item.id,
            "type": quiz_item.type,
            "chapter_id": quiz_item.chapter_id,
            "date_of_quiz": quiz_item.date_of_quiz.isoformat() if quiz_item.date_of_quiz else None,
            "time_duration": quiz_item.time_duration,
            "remarks": quiz_item.remarks,
            "chapter_name": quiz_item.chapter.name,
            "subject_name": quiz_item.chapter.subject.name,
            "questions_count": questions_count
        })

    return jsonify(
        user_role="admin",
        user_details={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "qualification": user.qualification,
            "dob": user.dob.isoformat() if user.dob else None
        },
        quizzes=quiz_data
    ), 200

#Add quiz
@app.route("/api/admin/add_quiz", methods=["POST"])
@role_required("admin")
def add_quiz_api():
    type = request.json.get("type")
    chapter_id = request.json.get("chapter_id")
    date_of_quiz = request.json.get("date_of_quiz")
    duration = request.json.get("duration")
    remarks = request.json.get("remarks")

    # Validate the input data
    if not chapter_id or not date_of_quiz or not type or not duration:
        return jsonify(message="All fields are required to create a quiz."), 400

    # Validate duration input
    try:
        duration = int(duration)
        if duration <= 0:
            raise ValueError("Duration must be positive.")
    except ValueError:
        return jsonify(message="Invalid duration. Please enter a valid number greater than zero."), 400

    # Parse date to proper formats
    try:
        # datetime.strptime returns a datetime object, which is compatible with db.DateTime
        parsed_date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d")
    except ValueError:
        return jsonify(message="Invalid date format. Use YYYY-MM-DD."), 400
    
    quiz = Quiz(
        type=type,
        chapter_id=chapter_id,
        date_of_quiz=parsed_date_of_quiz,
        time_duration=duration,
        remarks=remarks
    )
    db.session.add(quiz)
    db.session.commit()
    return jsonify(message="Quiz added successfully.", quiz_id=quiz.id), 201

#Delete quiz
@app.route("/api/admin/delete_quiz/<int:quiz_id>", methods=["DELETE"])
@role_required("admin")
def delete_quiz_api(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()

    if not quiz:
        return jsonify(message="Quiz not found."), 404

    db.session.delete(quiz)
    db.session.commit()
    return jsonify(message="Quiz deleted successfully."), 200

#Add question
@app.route("/api/admin/add_question/<int:quiz_id>", methods=["POST"])
@role_required("admin")
def add_question_api(quiz_id):
    statement = request.json.get('question_statement')
    option1 = request.json.get('option1')
    option2 = request.json.get('option2')
    option3 = request.json.get('option3')
    option4 = request.json.get('option4')
    correct_option = request.json.get('correct_option')

    if not all([statement, option1, option2, option3, option4, correct_option]):
        return jsonify(message='All fields are required!'), 400

    new_question = Question(
        quiz_id=quiz_id,
        question_statement=statement,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        correct_option=correct_option
    )

    db.session.add(new_question)
    db.session.commit()

    return jsonify(message='Question added successfully!', question_id=new_question.id), 201

#Edit question
@app.route("/api/admin/edit_question/<int:question_id>", methods=["PUT"])
@role_required("admin")
def edit_question_api(question_id):
    question = Question.query.filter_by(id=question_id).first()

    if not question:
        return jsonify(message="Question not found."), 404

    statement = request.json.get("question_statement")
    option1 = request.json.get("option1")
    option2 = request.json.get("option2")
    option3 = request.json.get("option3")
    option4 = request.json.get("option4")
    correct_option = request.json.get("correct_option")

    if not all([statement, option1, option2, option3, option4, correct_option]):
        return jsonify(message='All fields are required!'), 400

    question.question_statement = statement
    question.option1 = option1
    question.option2 = option2
    question.option3 = option3
    question.option4 = option4
    question.correct_option = correct_option
    
    db.session.commit()

    return jsonify(message='Question updated successfully!'), 200

#Delete question
@app.route("/api/admin/delete_question/<int:question_id>", methods=["DELETE"])
@role_required("admin")
def delete_question_api(question_id):
    question = Question.query.filter_by(id=question_id).first()

    if not question:
        return jsonify(message="Question not found."), 404

    db.session.delete(question)
    db.session.commit()
    return jsonify(message="Question deleted successfully."), 200

#Show user
@app.route("/api/admin/show_users", methods=["GET"])
@role_required("admin")
def show_users_api():
    current_admin_user = current_user
    users = User.query.filter_by(role="user").all()

    users_data = []
    for user_item in users:
        users_data.append({
            "id": user_item.id,
            "username": user_item.username,
            "full_name": user_item.full_name,
            "qualification": user_item.qualification,
            "dob": user_item.dob.isoformat() if user_item.dob else None,
            "role": user_item.role,
            "created_at": user_item.created_at.isoformat() if user_item.created_at else None
        })
    
    return jsonify(
        admin_user_details={
            "id": current_admin_user.id,
            "username": current_admin_user.username,
            "full_name": current_admin_user.full_name,
            "qualification": current_admin_user.qualification,
            "dob": current_admin_user.dob.isoformat() if current_admin_user.dob else None,
            "role": current_admin_user.role
        },
        users=users_data
    ), 200

#Delete User
@app.route("/api/admin/delete_user/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_user_api(id):
    user = User.query.get(id)

    if not user:
        return jsonify(message="User not found."), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify(message="User deleted successfully."), 200

#Logout
@app.route("/api/logout", methods=["POST"])
@jwt_required()
def logout_api():
    return jsonify(message="Successfully logged out."), 200