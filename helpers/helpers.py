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
    Tvoje gumbe razdelimo na pozitivne / nevtralne / negativne.
    Preprosto na podlagi trigger stringov.
    """
    triggers = rules.get_triggers()

    positive = []
    neutral = []
    negative = []

    for t in triggers:
        lt = t.lower()
        # Positive triggers
        if any(kw in lt for kw in ["smiles", "laughs", "greet", "positive"]):
            positive.append(t)
        # Negative triggers
        elif any(kw in lt for kw in ["stressed", "leans back", "crosses arms", 
                                      "error", "silence", "still", "away"]):
            negative.append(t)
        # Neutral triggers
        else:
            neutral.append(t)

    return {
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "final": [],  # če je prazno, index.html pokaže default gumbe
    }

