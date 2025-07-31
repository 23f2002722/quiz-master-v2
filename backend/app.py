from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import *
from application.security import jwt
from flask_cors import CORS

app = None

def create_app():
    app=Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    app.app_context().push()
    return app

app=create_app() 

from application.routes import *
from application.routes_user import *

if __name__=="__main__":
    db.create_all()
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        password_hash = generate_password_hash("987")
        admin = User(
            username="admin@gmail.com",
            full_name="admin",
            qualification="Graduation",
            dob=date(2004,12,16),
            password_hash=password_hash,
            role="admin",
        )
        db.session.add(admin)
    db.session.commit()

    app.run()
