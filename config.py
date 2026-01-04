# config.py - Configuration settings

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")

    # Podpira SQLite (lokalno), MySQL in PostgreSQL (production)
    # Render nastavi DATABASE_URL z PostgreSQL connection stringom
    # Če imaš MySQL: export DATABASE_URL="mysql+pymysql://user:pass@localhost/robot_fsm"
    # Če imaš PostgreSQL: export DATABASE_URL="postgresql://user:pass@host/dbname"
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Render PostgreSQL connection string včasih začne z postgres://, mora biti postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback na SQLite za lokalni razvoj
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "robot_fsm.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
