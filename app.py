# app.py - Main Flask application


import os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session as flask_session,
)

from config import Config
from models import db, SessionLog, InteractionLog
from fsm import RobotFSM
from rules_loader import RuleEngine

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Ustvari tabele
with app.app_context():
    db.create_all()

# Naloži pravila iz Excela
rules = RuleEngine()

# --- Helperji ----------------------------------------------------


def get_or_create_session():
    """
    Poskrbi, da imamo SessionLog v bazi in ID v Flask sessionu.
    """
    sid = flask_session.get("session_id")
    if sid is not None:
        session_obj = SessionLog.query.get(sid)
        if session_obj:
            return session_obj

    # nova seja
    session_obj = SessionLog()
    db.session.add(session_obj)
    db.session.commit()

    flask_session["session_id"] = session_obj.id
    return session_obj


def get_fsm():
    data = flask_session.get("fsm_state")
    return RobotFSM.from_dict(data)


def save_fsm(fsm: RobotFSM):
    flask_session["fsm_state"] = fsm.to_dict()


def get_conversation():
    conv = flask_session.get("conversation")
    if conv is None:
        # začetno sporočilo robota
        conv = [
            {
                "sender": "robot",
                "text": "Pozdravljeni! Sem robot za kognitivni trening. "
                        "Začniva – izberi trigger na desni strani.",
            }
        ]
        flask_session["conversation"] = conv
    return conv


def save_conversation(conv):
    flask_session["conversation"] = conv


def build_trigger_groups():
    """
    Tvoje gumbe razdelimo na pozitivne / nevtralne / negativne.
    Preprosto na podlagi trigger stringov.
    """
    triggers = rules.get_triggers()

    positive = []
    neutral = []
    negative = []

    for t in triggers:
        lt = t.lower()
        if "smiles" in lt or "laughs" in lt or "greet" in lt:
            positive.append(t)
        elif "stressed" in lt or "leans back" in lt or "disengagement" in lt:
            negative.append(t)
        else:
            neutral.append(t)

    return {
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "final": [],  # če je prazno, index.html pokaže default gumbe
    }


# --- Routes ------------------------------------------------------


@app.route("/", methods=["GET"])
def index():
    get_or_create_session()
    fsm = get_fsm()
    conv = get_conversation()
    trigger_groups = build_trigger_groups()

    return render_template(
        "index.html",
        conversation=conv,
        current_state=fsm.state,
        escalation=fsm.total_escalations(),
        step_count=fsm.step_count,
        triggers=trigger_groups,
    )


@app.route("/trigger", methods=["POST"])
def handle_trigger():
    data = request.get_json()
    trigger = data.get("trigger")

    if not trigger:
        return jsonify({"error": "Missing trigger"}), 400

    session_obj = get_or_create_session()
    fsm = get_fsm()
    conv = get_conversation()

    # 1) Izberi pravilo
    rule = rules.select_rule(trigger)
    if rule is None:
        robot_text = "Nisem prepričan, kako naj reagiram na ta trigger."
        inferred_intent = "Unknown"
        speech_act = None
        priority = None
    else:
        robot_text = rule["robot_text"]
        inferred_intent = rule["inferred_intent"]
        speech_act = rule["speech_act"]
        priority = rule["priority"]

    # 2) FSM prehod
    state_before = fsm.state
    new_state = fsm.update_state(inferred_intent)
    total_escalations = fsm.total_escalations()
    step_number = fsm.step_count

    # 3) Posodobi conversation (za UI)
    conv.append({"sender": "user", "text": f"[Trigger] {trigger}"})
    conv.append({"sender": "robot", "text": robot_text})
    save_conversation(conv)
    save_fsm(fsm)

    # 4) Log v bazo
    interaction = InteractionLog(
        session_id=session_obj.id,
        step_number=step_number,
        state_before=state_before,
        state_after=new_state,
        trigger=trigger,
        inferred_intent=inferred_intent,
        robot_speech_act=speech_act,
        robot_utterance=robot_text,
        priority=priority,
        escalation_count=total_escalations,
    )
    db.session.add(interaction)

    # če smo v final state, označimo konec seje
    if fsm.is_final() and session_obj.ended_at is None:
        session_obj.ended_at = datetime.utcnow()

    db.session.commit()

    return jsonify(
        {
            "conversation": conv,
            "current_state": fsm.state,
            "escalation": total_escalations,
            "step_count": step_number,
            "is_final": fsm.is_final(),
        }
    )


@app.route("/reset", methods=["POST"])
def reset():
    """
    Reset seje: nov SessionLog, reset FSM & conversation.
    """
    # Zaključi staro sejo (če ni zaključena)
    sid = flask_session.get("session_id")
    if sid:
        s = SessionLog.query.get(sid)
        if s and s.ended_at is None:
            s.ended_at = datetime.utcnow()
            db.session.commit()

    # Počisti session
    flask_session.clear()

    # Ustvari novo sejo
    get_or_create_session()
    fsm = RobotFSM()
    save_fsm(fsm)
    save_conversation(None)

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)
