# evaluation/functions.py - Funkcije za evalvacijo

"""
Funkcije za analizo in evalvacijo sej.
"""

from .scenarios import REFERENCE_SCENARIOS
from .categories import INTENT_CATEGORIES


def classify_session(interactions):
    """
    Klasificira sejo v enega od referenčnih scenarijev.
    Vrne najboljše ujemanje in confidence score.
    """
    if not interactions:
        return None, 0
    
    # Izračunaj statistiko seje
    stats = calculate_session_stats(interactions)
    
    best_match = None
    best_score = 0
    
    for scenario_id, scenario in REFERENCE_SCENARIOS.items():
        score = calculate_scenario_match(stats, scenario)
        if score > best_score:
            best_score = score
            best_match = scenario_id
    
    return best_match, best_score


def get_attr(obj, key, default=None):
    """Pridobi atribut iz objekta ali slovarja."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def calculate_session_stats(interactions):
    """Izračuna statistiko seje iz interakcij."""
    if not interactions:
        return {}
    
    intents = [get_attr(i, "inferred_intent") for i in interactions]
    triggers = [get_attr(i, "trigger") for i in interactions]
    
    # Štej kategorije
    positive_count = sum(1 for i in intents if i in INTENT_CATEGORIES["positive"])
    negative_count = sum(1 for i in intents if i in INTENT_CATEGORIES["negative"])
    total = len(intents)
    
    # Escalations
    escalations = [get_attr(i, "escalation_count", 0) for i in interactions]
    max_escalations = max(escalations) if escalations else 0
    
    # Stanja
    states = [get_attr(i, "state_after") for i in interactions]
    final_state = states[-1] if states else None
    
    return {
        "positive_ratio": positive_count / total if total > 0 else 0,
        "negative_ratio": negative_count / total if total > 0 else 0,
        "total_steps": total,
        "max_escalations": max_escalations,
        "final_state": final_state,
        "intents": intents,
        "triggers": triggers,
        "unique_intents": set(intents),
    }


def calculate_scenario_match(stats, scenario):
    """
    Izračuna ujemanje seje s scenarijem (0-100).
    """
    score = 0
    max_score = 0
    chars = scenario.get("characteristics", {})
    
    # Positive ratio check
    if "positive_ratio_min" in chars:
        max_score += 25
        if stats["positive_ratio"] >= chars["positive_ratio_min"]:
            score += 25
        else:
            # Delna točka
            score += 25 * (stats["positive_ratio"] / chars["positive_ratio_min"])
    
    if "positive_ratio_max" in chars:
        max_score += 25
        if stats["positive_ratio"] <= chars["positive_ratio_max"]:
            score += 25
        else:
            # Delna točka
            diff = stats["positive_ratio"] - chars["positive_ratio_max"]
            score += max(0, 25 - diff * 50)
    
    # Escalation check
    if "max_escalations" in chars:
        max_score += 25
        if stats["max_escalations"] <= chars["max_escalations"]:
            score += 25
        else:
            diff = stats["max_escalations"] - chars["max_escalations"]
            score += max(0, 25 - diff * 10)
    
    if "min_escalations" in chars:
        max_score += 25
        if stats["max_escalations"] >= chars["min_escalations"]:
            score += 25
    
    # Final state check
    if "expected_final_state" in chars:
        max_score += 25
        if stats["final_state"] == chars["expected_final_state"]:
            score += 25
    
    # Typical intents check
    if "typical_intents" in chars:
        max_score += 25
        matching_intents = set(chars["typical_intents"]) & stats["unique_intents"]
        if matching_intents:
            score += 25 * (len(matching_intents) / len(chars["typical_intents"]))
    
    return (score / max_score * 100) if max_score > 0 else 50


def evaluate_fsm_efficiency(interactions):
    """
    Evalvira učinkovitost FSM prehodov.
    """
    if not interactions:
        return {}
    
    states = [get_attr(i, "state_after") for i in interactions]
    
    # Štej prehode
    state_counts = {}
    for s in states:
        state_counts[s] = state_counts.get(s, 0) + 1
    
    # Izračunaj metrke
    total_steps = len(states)
    unique_states = len(set(states))
    reached_final = "S4_FEEDBACK" in states
    
    # Linearnost (kako direkten je bil prehod skozi stanja)
    expected_order = ["S0_GREETING", "S1_EXPLANATION", "S2_EXERCISE", "S3_BREAK", "S4_FEEDBACK"]
    last_index = -1
    forward_moves = 0
    backward_moves = 0
    
    for s in states:
        if s in expected_order:
            idx = expected_order.index(s)
            if idx > last_index:
                forward_moves += 1
            elif idx < last_index:
                backward_moves += 1
            last_index = idx
    
    linearity = forward_moves / (forward_moves + backward_moves) if (forward_moves + backward_moves) > 0 else 1
    
    # Učinkovitost (koraki do zaključka)
    if reached_final:
        min_steps = 5  # Minimalno potrebnih korakov
        efficiency = min(1.0, min_steps / total_steps)
    else:
        efficiency = 0
    
    return {
        "state_distribution": state_counts,
        "total_steps": total_steps,
        "unique_states_visited": unique_states,
        "reached_final_state": reached_final,
        "linearity_score": round(linearity * 100),
        "efficiency_score": round(efficiency * 100),
        "forward_progress": forward_moves,
        "backward_moves": backward_moves,
    }


def generate_functional_evaluation(interactions):
    """
    Generira popolno funkcionalno evalvacijo seje.
    """
    if not interactions:
        return {
            "scenario_classification": None,
            "confidence": 0,
            "fsm_metrics": {},
            "summary": "Seja nima interakcij.",
        }
    
    # Klasifikacija scenarija
    scenario_id, confidence = classify_session(interactions)
    scenario = REFERENCE_SCENARIOS.get(scenario_id, {})
    
    # FSM metrike
    fsm_metrics = evaluate_fsm_efficiency(interactions)
    
    # Statistika
    stats = calculate_session_stats(interactions)
    
    # Generiraj povzetek
    summary = generate_summary(scenario_id, confidence, fsm_metrics, stats)
    
    return {
        "scenario_classification": {
            "id": scenario_id,
            "name": scenario.get("name", "Neznano"),
            "icon": scenario.get("icon", "❓"),
            "description": scenario.get("description", ""),
        },
        "confidence": round(confidence),
        "fsm_metrics": fsm_metrics,
        "session_stats": {
            "positive_ratio": round(stats["positive_ratio"] * 100),
            "negative_ratio": round(stats["negative_ratio"] * 100),
            "total_steps": stats["total_steps"],
            "max_escalations": stats["max_escalations"],
        },
        "summary": summary,
    }


def generate_summary(scenario_id, confidence, fsm_metrics, stats):
    """Generira tekstovni povzetek evalvacije."""
    parts = []
    
    # Scenarij
    scenario = REFERENCE_SCENARIOS.get(scenario_id, {})
    if confidence >= 70:
        parts.append(f"Seja ustreza profilu '{scenario.get('name', 'neznan')}' z visoko zanesljivostjo.")
    elif confidence >= 50:
        parts.append(f"Seja delno ustreza profilu '{scenario.get('name', 'neznan')}'.")
    else:
        parts.append("Seja ne ustreza nobenemu tipičnemu profilu.")
    
    # FSM učinkovitost
    if fsm_metrics.get("reached_final_state"):
        if fsm_metrics.get("efficiency_score", 0) >= 70:
            parts.append("Prehod skozi stanja je bil učinkovit.")
        else:
            parts.append("Prehod skozi stanja je bil podaljšan.")
    else:
        parts.append("Seja ni dosegla zaključnega stanja.")
    
    # Linearnost
    if fsm_metrics.get("backward_moves", 0) > 2:
        parts.append(f"Zaznanih {fsm_metrics['backward_moves']} povratkov v prejšnja stanja.")
    
    return " ".join(parts)


def get_all_scenarios():
    """Vrne vse referenčne scenarije."""
    return {
        sid: {
            "id": sid,
            "name": s["name"],
            "description": s["description"],
            "icon": s["icon"],
        }
        for sid, s in REFERENCE_SCENARIOS.items()
    }

