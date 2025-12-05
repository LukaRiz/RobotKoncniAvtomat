# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SessionLog(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    # Uporabniška evalvacija (1-5 Likert)
    rating_supportive = db.Column(db.Integer, nullable=True)      # Robot je podporen
    rating_understandable = db.Column(db.Integer, nullable=True)  # Robot je razumljiv
    rating_non_intrusive = db.Column(db.Integer, nullable=True)   # Robot je nevsiljiv
    evaluated_at = db.Column(db.DateTime, nullable=True)

    interactions = db.relationship("InteractionLog", backref="session", lazy=True)


class InteractionLog(db.Model):
    __tablename__ = "interactions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)

    step_number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    state_before = db.Column(db.String(50), nullable=False)
    state_after = db.Column(db.String(50), nullable=False)

    trigger = db.Column(db.String(255), nullable=False)
    inferred_intent = db.Column(db.String(255), nullable=True)
    robot_speech_act = db.Column(db.String(255), nullable=True)
    robot_utterance = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(50), nullable=True)

    escalation_count = db.Column(db.Integer, default=0)
