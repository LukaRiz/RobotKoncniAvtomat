# helpers/helpers.py - Pomožne funkcije za upravljanje seje, FSM in pogovora

from flask import session as flask_session
from db import db, SessionLog
from core import RobotFSM


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
    """Vrne FSM iz seje."""
    data = flask_session.get("fsm_state")
    return RobotFSM.from_dict(data)


def save_fsm(fsm: RobotFSM):
    """Shrani FSM v sejo."""
    flask_session["fsm_state"] = fsm.to_dict()


def get_conversation():
    """Vrne pogovor iz seje, če ne obstaja ga ustvari."""
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
    """Shrani pogovor v sejo."""
    flask_session["conversation"] = conv


def build_trigger_groups(rules):
    """
    Gumbe razdelimo na pozitivne / nevtralne / negativne / feedback
    na podlagi Inferred Intent iz pravil.
    
    Grupiranje:
    - Pozitivni: Positive affect
    - Nevtralni: Attention shift, Request to speak/help (razen error)
    - Negativni: User frustrated/overloaded, Disengagement risk, User confused/waiting, error
    - Feedback: Provide action / speech feedback
    """
    positive = []
    neutral = []
    negative = []
    feedback = []
    
    # Mapiranje intentov na skupine
    POSITIVE_INTENTS = {"Positive affect"}
    NEUTRAL_INTENTS = {"Attention shift", "Request to speak/help"}
    NEGATIVE_INTENTS = {"User frustrated / overloaded", "Disengagement risk", "User confused / waiting"}
    FEEDBACK_INTENT = "Provide action / speech feedback"

    for rule in rules.rules:
        trigger = rule["Trigger"]
        intent = rule.get("Inferred Intent", "")
        
        # Posebni primer: "error" trigger je negativen, čeprav ima Request to speak/help intent
        if trigger == "error":
            negative.append(trigger)
        elif intent == FEEDBACK_INTENT:
            feedback.append(trigger)
        elif intent in POSITIVE_INTENTS:
            positive.append(trigger)
        elif intent in NEGATIVE_INTENTS:
            negative.append(trigger)
        elif intent in NEUTRAL_INTENTS:
            neutral.append(trigger)
        else:
            # Neznani intenti gredo v nevtralne
            neutral.append(trigger)

    return {
        "positive": sorted(positive),
        "neutral": sorted(neutral),
        "negative": sorted(negative),
        "feedback": sorted(feedback),
    }

