from flask import current_app as app, jsonify, request, abort
from .models import *
from flask_jwt_extended import create_access_token, current_user, jwt_required
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from sqlalchemy import func

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
@app.route('/api/user/start_quiz/<int:quiz_id>', methods=['POST']) # Changed to POST
@jwt_required()
def start_quiz_api(quiz_id):
    user = current_user
    quiz = Quiz.query.get(quiz_id) # Use get() as it's by primary key

    if not quiz:
        return jsonify(message="Quiz not found."), 404

    existing_score = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    if existing_score:
        return jsonify(message="You have already attempted this quiz!"), 409 # 409 Conflict

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
            "correct_option": q.correct_option # As per original logic, sending this. Be aware of security implications.
        })
    
    # Prepare initial quiz state data for the frontend
    initial_quiz_state = {
        'quiz_id': quiz.id,
        'user_id': user.id,
        'time_duration_seconds': quiz.time_duration * 60, # Convert to seconds as per original session logic
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
    
    # Expecting quiz_id and all user_responses from the frontend
    quiz_id = request.json.get('quiz_id')
    user_responses = request.json.get('responses') # Dictionary: {question_index: selected_option}
    client_start_time_str = request.json.get('start_time') # Optional: if you want server to validate time
    client_end_time_str = request.json.get('end_time') # Optional: if you want server to validate time

    if not quiz_id or not user_responses:
        return jsonify(message="Invalid submission: Missing quiz ID or responses."), 400

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify(message="Quiz not found."), 404

    # Optional: Time validation on server side
    if client_start_time_str and client_end_time_str:
        try:
            # Assuming client sends ISO format or YYYY-MM-DD HH:MM:SS
            client_start_time = datetime.fromisoformat(client_start_time_str) if 'T' in client_start_time_str else datetime.strptime(client_start_time_str, '%Y-%m-%d %H:%M:%S')
            client_end_time = datetime.fromisoformat(client_end_time_str) if 'T' in client_end_time_str else datetime.strptime(client_end_time_str, '%Y-%m-%d %H:%M:%S')
            
            elapsed_time_seconds = (client_end_time - client_start_time).total_seconds()
            # If quiz.time_duration is in minutes, convert to seconds
            allowed_time_seconds = quiz.time_duration * 60
            if elapsed_time_seconds > allowed_time_seconds + 5: # Add a small buffer for network latency
                # return jsonify(message="Quiz submission timed out or took too long."), 403 # Forbidden
                pass # You might choose to just record, or penalize, or reject.
        except ValueError:
            # Handle invalid time formats from client
            pass

    # Ensure user hasn't already submitted score for this quiz
    existing_score = Score.query.filter_by(user_id=user.id, quiz_id=quiz_id).first()
    if existing_score:
        return jsonify(message="You have already submitted this quiz."), 409 # Conflict

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    # Create a map for quick lookup: {question_id: Question_object}
    # This is better than relying on question_index from frontend if questions can be out of order
    question_map = {q.id: q for q in questions} 

    total_score = 0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    
    # The original code iterated `enumerate(questions)` and used `responses.get(str(index))`.
    # This implies `responses` keys were stringified 0-based indices.
    # If frontend sends {question_id: selected_option}, we need to adapt.
    # Assuming frontend sends {question_index_as_string: selected_option_string} based on original `responses` structure.

    # Replicate original scoring logic: iterate through all *server-side* questions
    # and match them with responses from client based on their index (position in original `questions` list)
    for index, question in enumerate(questions):
        selected_answer_raw = user_responses.get(str(index)) # Get response by its index in the original question list
        
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
            
    # Or, if frontend sends {question_id: selected_option}:
    # for q_id_str, selected_answer_raw in user_responses.items():
    #     q_id = int(q_id_str) # Assuming question IDs are sent as strings
    #     question = question_map.get(q_id)
    #     if question:
    #         selected_answer = str(selected_answer_raw).strip().lower()
    #         correct_answer = str(question.correct_option).strip().lower()
    #         if selected_answer == correct_answer:
    #             total_score += 1
    #             correct_count += 1
    #         else:
    #             incorrect_count += 1
    # # Handle unanswered if iterating by `user_responses`
    # unanswered_count = len(questions) - len(user_responses)


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
@app.route('/api/user/scores', methods=['GET']) # Changed route, no user_id in path for current_user
@jwt_required()
def view_scores_api():
    user = current_user # The user whose scores we are viewing is the logged-in user

    # Query scores and join with Quiz and Question to get necessary details
    scores_data = db.session.query(
        Score,
        Quiz,
        Subject,   # Join Subject to get subject name
        Chapter    # Join Chapter to get chapter name
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
    else: # User role
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
    current_admin_user = current_user # Renamed to avoid conflict

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
        admin_user_details={
            "id": current_admin_user.id,
            "username": current_admin_user.username,
            "full_name": current_admin_user.full_name,
            "qualification": current_admin_user.qualification,
            "dob": current_admin_user.dob.isoformat() if current_admin_user.dob else None,
            "role": current_admin_user.role
        },
        quiz_id=quiz_id,
        quiz_title=quiz.type, # Assuming 'type' field acts as the quiz title or identifier
        quiz_attempts=quiz_attempts_data,
        total_questions_in_quiz=total_questions_in_quiz
    ), 200

#Profile
@app.route("/api/profile", methods=["GET", "PUT"]) # Combined GET for fetching and PUT for updating
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
        email = request.json.get("email") # Maps to username in your current model

        if not current_password or not new_password or not confirm_password:
            return jsonify(message="Please fill out all the required password fields for update."), 400

        if not check_password_hash(user.password_hash, current_password):
            return jsonify(message="Incorrect current password."), 401

        if new_password != confirm_password:
            return jsonify(message="New passwords do not match."), 400
        
        # Optional: Add validation for email/username uniqueness if changing email/username
        # if email and email != user.username:
        #     existing_user_with_email = User.query.filter_by(username=email).first()
        #     if existing_user_with_email and existing_user_with_email.id != user.id:
        #         return jsonify(message="This email/username is already taken."), 409


        new_password_hash = generate_password_hash(new_password)
        user.full_name = name
        user.password_hash = new_password_hash
        user.username = email # As per your existing logic

        db.session.commit()

        return jsonify(message="Profile updated successfully."), 200
