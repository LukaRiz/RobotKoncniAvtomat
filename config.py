# config.py - Configuration settings

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")

    # Če imaš MySQL: export DATABASE_URL="mysql+pymysql://user:pass@localhost/robot_fsm"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "robot_fsm.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
