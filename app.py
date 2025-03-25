from flask import Flask
from application.database import db
from application.models import *
from application.config import LocalDevelopmentConfig
from flask_security import Security, SQLAlchemyUserDatastore, hash_password

def create_app():
    app=Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    datastore=SQLAlchemyUserDatastore(db, User, Role)
    app.security=Security(app, datastore)
    app.app_context().push()
    return app

app=create_app()

with app.app_context():
    db.create_all()

    app.security.datastore.find_or_create_role(name="admin", description="super_user")
    app.security.datastore.find_or_create_role(name="user", description="normal_user")
    db.session.commit()

    if not app.security.datastore.find_user(username="admin@gmail.com"):
        app.security.datastore.create_user(username="admin@gmail.com", 
                                           full_name="admin",
                                           qualification="Graduation",
                                           dob=date(2004,12,16),
                                           password_hash=hash_password("987"),
                                           roles=['admin'])
        
    if not app.security.datastore.find_user(username="shivangsingh436@gmail.com"):
        app.security.datastore.create_user(username="shivangsingh436@gmail.com", 
                                           full_name="Shivang",
                                           qualification="Graduation",
                                           dob=date(2004,12,16),
                                           password_hash=hash_password("123"),
                                           roles=['user'])
    db.session.commit()

from application.routes import *

if __name__=="__main__":
    app.run()
