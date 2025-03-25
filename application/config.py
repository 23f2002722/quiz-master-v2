class Config():
    DEBUG=False
    SQLALCHEMY_TRACK_MODIFICATIONS=True

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite3"
    DEBUG=True

    SECRET_KEY="12345"
    SECURITY_PASSWORD_HASH="bcrypt"
    SECURITY_PASSWORD_SALT="12345"
    WTF_CSRF_ENABLED=False
    SECURITY_TOKEN_AUTHENTICATION_HEADER="Authentication-Token"