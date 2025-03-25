from flask import current_app as app, jsonify, request
from flask_security import auth_required, hash_password, roles_required, current_user
from datetime import datetime
from .database import db
from .models import *



@app.route('/', methods=["GET"])
@auth_required('token')
def index():
    return "This is home page."

@app.post('/api/register_user')
def register_user():

    credentials=request.get_json()

    if not app.security.datastore.find_user(username=credentials["username"]):
        app.security.datastore.create_user(username=credentials["username"], 
                                           full_name=credentials["name"],
                                           qualification=credentials["qualification"],
                                           dob=datetime.strptime(credentials["dob"], "%Y-%m-%d").date(),
                                           password_hash=hash_password("password"),
                                           roles=['user'])
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    
    return jsonify({"message": "User already exists"}), 400


    