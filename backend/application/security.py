from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from application.models import User

jwt = JWTManager()

@jwt.user_identity_loader
def load(user_id):
    return user_id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)