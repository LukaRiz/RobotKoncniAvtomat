# routes/evaluate.py - Route za pregled sej

from flask import Blueprint, render_template, jsonify

from db import SessionLog, InteractionLog
from evaluation import generate_functional_evaluation, classify_session, get_all_scenarios

evaluate_bp = Blueprint("evaluate", __name__)


@evaluate_bp.route("/evaluate", methods=["GET"])
def evaluate_page():
    """
    Stran za pregled preteklih sej.
    """
    return render_template("evaluate.html")


@evaluate_bp.route("/api/all-sessions", methods=["GET"])
def get_all_sessions():
    """
    Vrne vse seje za analizo (samo tiste z vsaj eno interakcijo).
    """
    sessions = SessionLog.query.order_by(SessionLog.started_at.desc()).limit(50).all()
    
    result = []
    for s in sessions:
        interactions = InteractionLog.query.filter_by(session_id=s.id).all()
        
        # Preskoči prazne seje (brez interakcij)
        if not interactions:
            continue
        
        # Izračunaj statistiko
        escalation_count = max([i.escalation_count for i in interactions], default=0)
        triggers_used = set([i.trigger for i in interactions])
        
        # Klasifikacija scenarija
        scenario_id, confidence = classify_session(interactions)
        
        result.append({
            "id": s.id,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "step_count": len(interactions),
            "escalation_count": escalation_count,
            "triggers_used": list(triggers_used),
            "completed": s.ended_at is not None,
            "has_evaluation": s.rating_supportive is not None,
            "scenario_type": scenario_id,
            "scenario_confidence": round(confidence),
        })
    
    return jsonify(result)


def is_positive_trigger(trigger):
    """Preveri, ali je trigger pozitiven (uporablja isto logiko kot helpers.py)."""
    if not trigger:
        return False
    lt = trigger.lower()
    return any(kw in lt for kw in ["smiles", "laughs", "greet", "positive"])


def is_negative_trigger(trigger):
    """Preveri, ali je trigger negativen (uporablja isto logiko kot helpers.py)."""
    if not trigger:
        return False
    lt = trigger.lower()
    return any(kw in lt for kw in ["stressed", "leans back", "crosses arms", 
                                    "error", "silence", "still", "away", "frustrated", 
                                    "overloaded", "disengagement", "decreasing engagement"])


@evaluate_bp.route("/api/session/<int:session_id>", methods=["GET"])
def get_session_details(session_id):
    """
    Vrne podrobnosti posamezne seje vključno s funkcionalno evalvacijo.
    """
    session = SessionLog.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    interactions = InteractionLog.query.filter_by(session_id=session_id).order_by(InteractionLog.step_number).all()
    
    # Izračunaj statistiko - uporabljamo triggerje (ne intente), kot v glavnem chatu
    positive_count = sum(1 for i in interactions if is_positive_trigger(i.trigger))
    negative_count = sum(1 for i in interactions if is_negative_trigger(i.trigger))
    total = len(interactions)
    escalation_count = max([i.escalation_count for i in interactions], default=0)
    triggers_used = set([i.trigger for i in interactions])
    
    statistics = {
        "step_count": total,
        "positive_interactions": positive_count,
        "negative_interactions": negative_count,
        "total_escalations": escalation_count,
        "positive_ratio": positive_count / total if total > 0 else 0,
        "unique_triggers": len(triggers_used),
    }
    
    # Funkcionalna evalvacija
    functional_evaluation = generate_functional_evaluation(interactions)
    
    # Sestavi odgovor
    return jsonify({
        "session": {
            "id": session.id,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "completed": session.ended_at is not None,
            "rating_supportive": session.rating_supportive,
            "rating_understandable": session.rating_understandable,
            "rating_non_intrusive": session.rating_non_intrusive,
            "evaluated_at": session.evaluated_at.isoformat() if session.evaluated_at else None,
        },
        "interactions": [
            {
                "step_number": i.step_number,
                "trigger": i.trigger,
                "inferred_intent": i.inferred_intent,
                "state_before": i.state_before,
                "state_after": i.state_after,
                "robot_utterance": i.robot_utterance,
                "speech_act": i.robot_speech_act,
                "escalation_count": i.escalation_count,
                "timestamp": i.timestamp.isoformat() if i.timestamp else None,
            }
            for i in interactions
        ],
        "statistics": statistics,
        "functional_evaluation": functional_evaluation,
    })


@evaluate_bp.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    """
    Vrne vse referenčne scenarije.
    """
    return jsonify(get_all_scenarios())
