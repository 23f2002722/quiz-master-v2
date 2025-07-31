from flask import current_app as app, jsonify, request, abort
from .models import *
from flask_jwt_extended import create_access_token, current_user, jwt_required
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from sqlalchemy import func, or_, and_

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

#Start quiz
@app.route('/api/user/start_quiz/<int:quiz_id>', methods=['POST'])
@jwt_required()
def start_quiz_api(quiz_id):
    user = current_user
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify(message="Quiz not found."), 404

    existing_score = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    if existing_score:
        return jsonify(message="You have already attempted this quiz!"), 409 

    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    if not questions:
        return jsonify(message="No questions available for this quiz."), 404

    questions_data = []
    for q in questions:
        questions_data.append({
            "id": q.id,
            "question_statement": q.question_statement,
            "option1": q.option1,
            "option2": q.option2,
            "option3": q.option3,
            "option4": q.option4,
            "correct_option": q.correct_option 
        })
    
    # Prepare initial quiz state data for the frontend
    initial_quiz_state = {
        'quiz_id': quiz.id,
        'user_id': user.id,
        'time_duration_seconds': quiz.time_duration * 60,
        'questions': questions_data
    }

    return jsonify(
        message="Quiz started successfully!",
        quiz_data=initial_quiz_state
    ), 200

#Submit quiz
@app.route('/api/user/submit_quiz', methods=['POST'])
@jwt_required()
def submit_quiz_api():
    user = current_user
    
    quiz_id = request.json.get('quiz_id')
    user_responses = request.json.get('responses')
    client_start_time_str = request.json.get('start_time') 
    client_end_time_str = request.json.get('end_time') 

    if not quiz_id or not user_responses:
        return jsonify(message="Invalid submission: Missing quiz ID or responses."), 400

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify(message="Quiz not found."), 404

    if client_start_time_str and client_end_time_str:
        try:
            client_start_time = datetime.fromisoformat(client_start_time_str) if 'T' in client_start_time_str else datetime.strptime(client_start_time_str, '%Y-%m-%d %H:%M:%S')
            client_end_time = datetime.fromisoformat(client_end_time_str) if 'T' in client_end_time_str else datetime.strptime(client_end_time_str, '%Y-%m-%d %H:%M:%S')
            
            elapsed_time_seconds = (client_end_time - client_start_time).total_seconds()
            allowed_time_seconds = quiz.time_duration * 60
            if elapsed_time_seconds > allowed_time_seconds + 5:
                pass
        except ValueError:
            pass

    # Ensure user hasn't already submitted score for this quiz
    existing_score = Score.query.filter_by(user_id=user.id, quiz_id=quiz_id).first()
    if existing_score:
        return jsonify(message="You have already submitted this quiz."), 409 

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    question_map = {q.id: q for q in questions} 

    total_score = 0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    for index, question in enumerate(questions):
        selected_answer_raw = user_responses.get(str(index))
        
        if selected_answer_raw is not None:
            selected_answer = str(selected_answer_raw).strip().lower()
            correct_answer = str(question.correct_option).strip().lower()
            
            if selected_answer == correct_answer:
                total_score += 1
                correct_count += 1
            else:
                incorrect_count += 1
        else:
            unanswered_count += 1

    new_score = Score(
        user_id=user.id,
        quiz_id=quiz_id,
        total_score=total_score,
        timestamp=datetime.now(timezone.utc) # Using UTC timezone for consistency
    )
    db.session.add(new_score)
    db.session.commit()

    return jsonify(
        message=f"Quiz submitted! Your score: {total_score}/{len(questions)}",
        total_score=total_score,
        total_questions=len(questions),
        correct_answers=correct_count,
        incorrect_answers=incorrect_count,
        unanswered=unanswered_count
    ), 200

#View score
@app.route('/api/user/scores', methods=['GET']) 
@jwt_required()
def view_scores_api():
    user = current_user 
    # Query scores and join with Quiz and Question to get necessary details
    scores_data = db.session.query(
        Score,
        Quiz,
        Subject, 
        Chapter  
    ).join(
        Quiz, Score.quiz_id == Quiz.id
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).join(
        Subject, Chapter.subject_id == Subject.id
    ).filter(Score.user_id == user.id).all()

    # Get total questions for each quiz
    all_quizzes_questions_count = {
        quiz_item.id: db.session.query(Question).filter(Question.quiz_id == quiz_item.id).count()
        for quiz_item in Quiz.query.all()
    }

    results = []
    for score_obj, quiz_obj, subject_obj, chapter_obj in scores_data:
        total_questions_in_quiz = all_quizzes_questions_count.get(quiz_obj.id, 0)
        results.append({
            "score_id": score_obj.id,
            "quiz_id": quiz_obj.id,
            "quiz_type": quiz_obj.type,
            "quiz_date": quiz_obj.date_of_quiz.isoformat() if quiz_obj.date_of_quiz else None,
            "total_score": score_obj.total_score,
            "total_questions": total_questions_in_quiz,
            "timestamp": score_obj.timestamp.isoformat() if score_obj.timestamp else None,
            "chapter_name": chapter_obj.name,
            "subject_name": subject_obj.name
        })
    
    return jsonify(
        user_details={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "qualification": user.qualification,
            "dob": user.dob.isoformat() if user.dob else None
        },
        scores=results
    ), 200


#Summary
@app.route('/api/summary', methods=['GET'])
@jwt_required()
def summary_api():
    user = current_user

    if user.role == "admin":
        subject_wise_top_scores_raw = db.session.query(
            Subject.name,
            db.func.max(Score.total_score).label('top_score')
        ).join(Chapter, Chapter.subject_id == Subject.id)\
         .join(Quiz, Quiz.chapter_id == Chapter.id)\
         .join(Score, Score.quiz_id == Quiz.id)\
         .group_by(Subject.name)\
         .all()

        subject_wise_user_attempts_raw = db.session.query(
            Subject.name,
            db.func.count(db.distinct(Score.user_id)).label('user_count')
        ).join(Chapter, Chapter.subject_id == Subject.id)\
         .join(Quiz, Quiz.chapter_id == Chapter.id)\
         .join(Score, Score.quiz_id == Quiz.id)\
         .group_by(Subject.name)\
         .all()

        subject_wise_top_scores = [{"subject_name": s.name, "top_score": s.top_score} for s in subject_wise_top_scores_raw]
        subject_wise_user_attempts = [{"subject_name": s.name, "user_count": s.user_count} for s in subject_wise_user_attempts_raw]

        return jsonify(
            user_role="admin",
            user_details={
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "qualification": user.qualification,
                "dob": user.dob.isoformat() if user.dob else None
            },
            subject_wise_top_scores=subject_wise_top_scores,
            subject_wise_user_attempts=subject_wise_user_attempts
        ), 200
    else: 
        subject_wise_attempts_raw = db.session.query(
            Subject.name,
            db.func.count(Score.id).label('attempt_count')
        ).join(Chapter, Chapter.subject_id == Subject.id)\
         .join(Quiz, Quiz.chapter_id == Chapter.id)\
         .join(Score, Score.quiz_id == Quiz.id)\
         .filter(Score.user_id == user.id)\
         .group_by(Subject.name)\
         .all()

        month_wise_attempts_raw = db.session.query(
            db.func.strftime('%Y-%m', Score.timestamp).label('month'),
            db.func.count(Score.id).label('attempt_count')
        ).filter(Score.user_id == user.id)\
         .group_by(db.func.strftime('%Y-%m', Score.timestamp))\
         .all()

        subject_wise_attempts = [{"subject_name": s.name, "attempt_count": s.attempt_count} for s in subject_wise_attempts_raw]
        month_wise_attempts = [{"month": m.month, "attempt_count": m.attempt_count} for m in month_wise_attempts_raw]

        return jsonify(
            user_role="user",
            user_details={
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "qualification": user.qualification,
                "dob": user.dob.isoformat() if user.dob else None
            },
            subject_wise_attempts=subject_wise_attempts,
            month_wise_attempts=month_wise_attempts
        ), 200

#Quiz analytics
@app.route('/api/admin/quiz_analytics/<int:quiz_id>', methods=['GET'])
@role_required("admin")
def quiz_analytics_api(quiz_id):
    current_admin_user = current_user

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify(message="Quiz not found."), 404

    quiz_attempts_raw = db.session.query(
        User.id,
        User.full_name,
        User.username,
        Score.total_score,
        Score.timestamp,
        Score.quiz_id
    ).join(Score, Score.user_id == User.id)\
     .filter(Score.quiz_id == quiz_id)\
     .all()

    quiz_attempts_data = []
    for user_id, full_name, username, total_score, timestamp, q_id in quiz_attempts_raw:
        quiz_attempts_data.append({
            "user_id": user_id,
            "full_name": full_name,
            "username": username,
            "total_score": total_score,
            "timestamp": timestamp.isoformat() if timestamp else None,
            "quiz_id": q_id
        })

    total_questions_in_quiz = db.session.query(Question).filter(Question.quiz_id == quiz_id).count()

    return jsonify(
        quiz_id=quiz_id,
        quiz_title=quiz.type, 
        quiz_attempts=quiz_attempts_data,
        total_questions_in_quiz=total_questions_in_quiz
    ), 200

#Profile
@app.route("/api/profile", methods=["GET", "PUT"]) 
@jwt_required()
def profile_api():
    user = current_user

    if request.method == "GET":
        return jsonify(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            qualification=user.qualification,
            dob=user.dob.isoformat() if user.dob else None,
            role=user.role,
            created_at=user.created_at.isoformat() if user.created_at else None
        ), 200

    elif request.method == "PUT":
        name = request.json.get("name")
        current_password = request.json.get("current_password")
        new_password = request.json.get("new_password")
        confirm_password = request.json.get("confirm_password")
        email = request.json.get("email") 

        if not current_password or not new_password or not confirm_password:
            return jsonify(message="Please fill out all the required password fields for update."), 400

        if not check_password_hash(user.password_hash, current_password):
            return jsonify(message="Incorrect current password."), 401

        if new_password != confirm_password:
            return jsonify(message="New passwords do not match."), 400
        

        new_password_hash = generate_password_hash(new_password)
        user.full_name = name
        user.password_hash = new_password_hash
        user.username = email 

        db.session.commit()

        return jsonify(message="Profile updated successfully."), 200
    
#Search
@app.route('/api/search', methods=['GET'])
@jwt_required()
def search_api():
    user = current_user
    category = request.args.get('category')
    query = request.args.get('query', '').strip()

    if user.role == "admin":
        if category == "users":
            users_raw = User.query.filter(
                and_(
                    or_(
                        User.full_name.ilike(f"%{query}%"),
                        User.username.ilike(f"%{query}%"),
                        db.func.strftime("%Y-%m-%d", User.dob).ilike(f"%{query}%")
                    ),
                    User.role != "admin" 
                )
            ).all()
            
            users_data = []
            for user_item in users_raw:
                users_data.append({
                    "id": user_item.id,
                    "username": user_item.username,
                    "full_name": user_item.full_name,
                    "qualification": user_item.qualification,
                    "dob": user_item.dob.isoformat() if user_item.dob else None,
                    "role": user_item.role,
                    "created_at": user_item.created_at.isoformat() if user_item.created_at else None
                })
            return jsonify(category=category, users=users_data, user_role="admin"), 200

        elif category == "quiz":
            quizzes_raw = Quiz.query.join(Chapter).join(Subject).filter(
                or_(
                    Quiz.type.ilike(f"%{query}%"),
                    Chapter.name.ilike(f"%{query}%"),
                    Subject.name.ilike(f"%{query}%")
                )
            ).all()
            
            quiz_data = []
            for quiz_item in quizzes_raw:
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
            return jsonify(category=category, quizzes=quiz_data, user_role="admin"), 200

        elif category == "chapters":
            chapters_raw = Chapter.query.join(Subject).filter(
                Chapter.name.ilike(f"%{query}%")
            ).all()
            
            chapters_data = []
            for chapter_item in chapters_raw:
                questions_count = db.session.query(Question).join(Quiz).filter(Quiz.chapter_id == chapter_item.id).count()
                chapters_data.append({
                    "id": chapter_item.id,
                    "name": chapter_item.name,
                    "description": chapter_item.description,
                    "subject_name": chapter_item.subject.name,
                    "questions_count": questions_count
                })
            return jsonify(category=category, chapters=chapters_data, user_role="admin"), 200

        elif category == "subjects":
            subjects_raw = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
            
            subjects_data = []
            for subject_item in subjects_raw:
                subjects_data.append({
                    "id": subject_item.id,
                    "name": subject_item.name,
                    "description": subject_item.description
                })
            return jsonify(category=category, subjects=subjects_data, user_role="admin"), 200

        else: 
            return jsonify(message="Invalid search category for admin."), 400

    else: 
        if category == "quiz":
            current_date_obj = date.today()
            attempted_quiz_ids = db.session.query(Score.quiz_id).filter(Score.user_id == user.id).subquery()
            
            quizzes_raw = Quiz.query.join(Chapter).join(Subject).filter(
                and_(
                    or_(
                        Quiz.type.ilike(f"%{query}%"),
                        Chapter.name.ilike(f"%{query}%"),
                        Subject.name.ilike(f"%{query}%")
                    ),
                    db.func.date(Quiz.date_of_quiz) >= current_date_obj,
                    ~Quiz.id.in_(attempted_quiz_ids)
                )
            ).all()

            quiz_data = []
            for quiz_item in quizzes_raw:
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
            return jsonify(category=category, quizzes=quiz_data, user_role="user"), 200

        elif category == "scores":
            scores_raw = db.session.query(Score, Quiz, Chapter, Subject)\
                           .join(Quiz, Score.quiz_id == Quiz.id)\
                           .join(Chapter, Quiz.chapter_id == Chapter.id)\
                           .join(Subject, Chapter.subject_id == Subject.id)\
                           .filter(
                               and_(
                                   Score.user_id == user.id,
                                   or_(
                                       db.func.strftime("%Y-%m-%d %H:%M:%S", Score.timestamp).ilike(f"%{query}%"), # For timestamp search
                                       Chapter.name.ilike(f"%{query}%"),
                                       Quiz.type.ilike(f"%{query}%"),
                                       Subject.name.ilike(f"%{query}%")
                                   )
                               )
                           ).all()
            
            scores_data = []
            for score_obj, quiz_obj, chapter_obj, subject_obj in scores_raw:
                total_questions_in_quiz = db.session.query(Question).filter(Question.quiz_id == quiz_obj.id).count()
                scores_data.append({
                    "score_id": score_obj.id,
                    "quiz_id": quiz_obj.id,
                    "quiz_type": quiz_obj.type,
                    "quiz_date": quiz_obj.date_of_quiz.isoformat() if quiz_obj.date_of_quiz else None,
                    "total_score": score_obj.total_score,
                    "total_questions": total_questions_in_quiz,
                    "timestamp": score_obj.timestamp.isoformat() if score_obj.timestamp else None,
                    "chapter_name": chapter_obj.name,
                    "subject_name": subject_obj.name
                })
            return jsonify(category=category, scores=scores_data, user_role="user"), 200

        else: 
            return jsonify(message="Invalid search category for user."), 400
    return jsonify(message="Invalid search parameters."), 400

@app.route("/api/admin_contact", methods=["GET"])
def get_admin_contact_email():
    admin_user = User.query.filter_by(role="admin").first()
    if admin_user:
        return jsonify(admin_email=admin_user.username), 200 
    return jsonify(admin_email="contact@quizmaster.com"), 200 
