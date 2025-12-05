# routes/evaluate.py - Route za pregled sej

from flask import Blueprint, render_template, jsonify

from models import SessionLog, InteractionLog

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
        
        result.append({
            "id": s.id,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "step_count": len(interactions),
            "escalation_count": escalation_count,
            "triggers_used": list(triggers_used),
            "completed": s.ended_at is not None,
            "has_evaluation": s.rating_supportive is not None,
        })
    
    return jsonify(result)


@evaluate_bp.route("/api/session/<int:session_id>", methods=["GET"])
def get_session_details(session_id):
    """
    Vrne podrobnosti posamezne seje.
    """
    session = SessionLog.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    interactions = InteractionLog.query.filter_by(session_id=session_id).order_by(InteractionLog.step_number).all()
    
    # Izračunaj statistiko
    positive_intents = ["Engaged", "Positive Affect", "Acknowledgment", "Ready", "Completion"]
    negative_intents = ["Confusion", "Stress", "Frustration", "Disengagement", "Overload"]
    
    positive_count = sum(1 for i in interactions if i.inferred_intent in positive_intents)
    negative_count = sum(1 for i in interactions if i.inferred_intent in negative_intents)
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
    })
