# evaluation/scenarios.py - Referenčni scenariji

"""
Definicije referenčnih scenarijev za klasifikacijo sej.
"""

REFERENCE_SCENARIOS = {
    "calm": {
        "name": "Mirna seja",
        "description": "Uporabnik je pozitiven in sodelujoč skozi celoten trening.",
        "icon": "",
        "expected_triggers": [
            "greet", "User smiles/laughs", "User smiles/laughs", 
            "end of user speech", "User smiles/laughs"
        ],
        "characteristics": {
            "positive_ratio_min": 0.7,
            "max_escalations": 1,
            "expected_final_state": "S4_FEEDBACK",
        }
    },
    "confused": {
        "name": "Pogosto zmeden",
        "description": "Uporabnik potrebuje več ponovitev in pojasnil.",
        "icon": "",
        "expected_triggers": [
            "greet", "Long silence after robot prompt", "long time being still",
            "Hand raised while looking at robot", "User smiles/laughs"
        ],
        "characteristics": {
            "positive_ratio_min": 0.3,
            "positive_ratio_max": 0.6,
            "max_escalations": 3,
            "typical_intents": ["Confusion", "Hesitation", "Waiting"],
        }
    },
    "distracted": {
        "name": "Odvrača pozornost",
        "description": "Uporabnik pogosto gleda drugam, potrebuje preusmeritev.",
        "icon": "",
        "expected_triggers": [
            "greet", "User looks away to another person", "User smiles/laughs",
            "User looks away to another person", "end of user movement"
        ],
        "characteristics": {
            "positive_ratio_min": 0.4,
            "max_escalations": 2,
            "typical_intents": ["Disengagement", "Distraction"],
        }
    },
    "stressed": {
        "name": "Pod stresom",
        "description": "Uporabnik kaže znake stresa in preobremenjenosti.",
        "icon": "",
        "expected_triggers": [
            "greet", "User face stressed", "User leans back / crosses arms",
            "User face stressed", "User leans back / crosses arms"
        ],
        "characteristics": {
            "positive_ratio_max": 0.4,
            "min_escalations": 2,
            "typical_intents": ["Stress", "Frustration", "Overload"],
        }
    },
    "critical": {
        "name": "Kritična seja",
        "description": "Veliko eskalacij, seja zaključena predčasno.",
        "icon": "",
        "expected_triggers": [
            "greet", "User face stressed", "User face stressed",
            "error", "User leans back / crosses arms"
        ],
        "characteristics": {
            "positive_ratio_max": 0.3,
            "min_escalations": 3,
            "expected_end_reason": "max_escalations",
        }
    }
}

