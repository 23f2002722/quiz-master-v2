import os
from celery import Celery
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import *
from application.security import jwt

def make_celery():
    broker = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    backend = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery = Celery(__name__, broker=broker, backend=backend)
    celery.conf.timezone = "Asia/Kolkata"
    celery.conf.broker_connection_retry_on_startup = True
    return celery

celery = make_celery()

def create_app_context():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
    app.app_context().push()
    return app