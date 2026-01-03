# routes/main.py - Glavne route aplikacije

from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session as flask_session

from db import db, SessionLog, InteractionLog
from core import RobotFSM
from helpers import (
    get_or_create_session,
    get_fsm,
    save_fsm,
    get_conversation,
    save_conversation,
    build_trigger_groups,
)

main_bp = Blueprint("main", __name__)

# Reference na rules engine - nastavi se v app.py
rules = None


def init_rules(rules_engine):
    """Inicializira rules engine za ta blueprint."""
    global rules
    rules = rules_engine


@main_bp.route("/", methods=["GET"])
def index():
    # NE ustvarjamo seje ob obisku - seja se ustvari šele ob prvem triggerju
    fsm = get_fsm()
    conv = get_conversation()
    trigger_groups = build_trigger_groups(rules)

    return render_template(
        "index.html",
        conversation=conv,
        current_state=fsm.state,
        state_info=fsm.get_state_info(),
        escalation=fsm.total_escalations(),
        step_count=fsm.step_count,
        statistics=fsm.get_statistics(),
        triggers=trigger_groups,
    )


@main_bp.route("/trigger", methods=["POST"])
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
    new_state = fsm.update_state(inferred_intent, trigger=trigger)
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

    # Če naj robot predlaga zaključek (preveč eskalacij)
    suggest_end_message = None
    if fsm.should_suggest_end and fsm.end_reason == "max_escalations":
        suggest_end_message = "Opazil sem, da imaš težave. Želiš, da zaključiva ali nadaljujeva z odmorom?"
        conv.append({"sender": "robot", "text": suggest_end_message, "type": "suggestion"})
        save_conversation(conv)

    return jsonify(
        {
            "conversation": conv,
            "current_state": fsm.state,
            "state_info": fsm.get_state_info(),
            "escalation": total_escalations,
            "step_count": step_number,
            "statistics": fsm.get_statistics(),
            "is_final": fsm.is_final(),
            "should_suggest_end": fsm.should_suggest_end,
            "end_reason": fsm.end_reason,
            "speech_act": speech_act,
        }
    )


@main_bp.route("/reset", methods=["POST"])
def reset():
    """
    Reset seje: zaključi staro, počisti stanje.
    Nova seja se ustvari šele ob prvem triggerju.
    """
    # Zaključi staro sejo (če ni zaključena in če ima vsaj eno interakcijo)
    sid = flask_session.get("session_id")
    if sid:
        s = SessionLog.query.get(sid)
        if s and s.ended_at is None:
            # Preveri če ima seja vsaj eno interakcijo
            has_interactions = InteractionLog.query.filter_by(session_id=s.id).first() is not None
            if has_interactions:
                s.ended_at = datetime.utcnow()
                db.session.commit()
            else:
                # Prazna seja - izbriši jo
                db.session.delete(s)
                db.session.commit()

    # Počisti flask session (NE ustvarjamo nove seje v bazi)
    flask_session.clear()

    return jsonify({"ok": True})


@main_bp.route("/force-end", methods=["POST"])
def force_end():
    """
    Prisili zaključek seje (uporabnik želi končati).
    """
    fsm = get_fsm()
    conv = get_conversation()

    fsm.force_end()
    robot_text = "V redu, zaključujeva. Hvala za sodelovanje! 👋"
    conv.append({"sender": "robot", "text": robot_text})
    save_conversation(conv)
    save_fsm(fsm)

    # Zaključi sejo v bazi samo če obstaja
    sid = flask_session.get("session_id")
    if sid:
        session_obj = SessionLog.query.get(sid)
        if session_obj and session_obj.ended_at is None:
            session_obj.ended_at = datetime.utcnow()
            db.session.commit()

    return jsonify({
        "conversation": conv,
        "current_state": fsm.state,
        "state_info": fsm.get_state_info(),
        "statistics": fsm.get_statistics(),
        "is_final": True,
    })


@main_bp.route("/statistics", methods=["GET"])
def get_statistics():
    """
    Vrne statistiko trenutne seje.
    """
    fsm = get_fsm()
    return jsonify(fsm.get_statistics())


@main_bp.route("/api/evaluate-session", methods=["POST"])
def evaluate_session():
    """
    Shrani uporabniško evalvacijo za trenutno sejo.
    """
    data = request.get_json()
    
    sid = flask_session.get("session_id")
    if not sid:
        return jsonify({"error": "No active session"}), 400
    
    session_obj = SessionLog.query.get(sid)
    if not session_obj:
        return jsonify({"error": "Session not found"}), 404
    
    # Shrani ocene (lahko so None če uporabnik ni ocenil)
    session_obj.rating_supportive = data.get("supportive")
    session_obj.rating_understandable = data.get("understandable")
    session_obj.rating_non_intrusive = data.get("non_intrusive")
    session_obj.evaluated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({"ok": True})
