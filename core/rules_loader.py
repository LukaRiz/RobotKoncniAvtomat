# core/rules_loader.py
"""
RuleEngine z vsemi pravili iz robot_rules.xlsx.

Vsako pravilo ima:
- Trigger: ime gumba / dogodka
- Inferred Intent: kaj "razume" robot
- Priority: Critical / High / Medium / Low
- ConfidenceThrs.: prag zaupanja
- Escalated Action: eskalacijska akcija
- escalationCount: število eskalacij
- Robot Speech Act: tip odgovora
- RobotText: dejanski tekst, ki ga robot pove
"""

from typing import List, Dict

PRIORITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}

# *** PRAVILA IZ EXCELA (robot_rules.xlsx) ***
RULES: List[Dict] = [
    {
        "Trigger": "Long silence after robot prompt",
        "Inferred Intent": "User confused / waiting",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Directive (clarify)",
        "RobotText": "Do you want me to repeat that?",
    },
    {
        "Trigger": "User face stressed",
        "Inferred Intent": "User frustrated / overloaded",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Expressive + Commissive",
        "RobotText": "You look stressed — shall I slow down?",
    },
    {
        "Trigger": "Hand raised while looking at robot",
        "Inferred Intent": "Request to speak/help",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Acknowledgement + Directive",
        "RobotText": "Yes, go ahead — what do you need?",
    },
    {
        "Trigger": "User looks away to another person",
        "Inferred Intent": "Attention shift",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Assertive",
        "RobotText": "I'll wait while you talk to them.",
    },
    {
        "Trigger": "User smiles/laughs",
        "Inferred Intent": "Positive affect",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Expressive",
        "RobotText": "Haha, that's funny!",
    },
    {
        "Trigger": "User leans back / crosses arms",
        "Inferred Intent": "Disengagement risk",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Commissive/Expressive",
        "RobotText": "Should we take a short break?",
    },
    {
        "Trigger": "greet",
        "Inferred Intent": "Positive affect",
        "Priority": "High",
        "ConfidenceThrs.": 0.75,
        "Escalated Action": "Call for help",
        "escalationCount": None,
        "Robot Speech Act": "Commissive/Expressive",
        "RobotText": "Hello! Nice to see you!",
    },
    {
        "Trigger": "assist",
        "Inferred Intent": "Request to speak/help",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": "Call for help",
        "escalationCount": None,
        "Robot Speech Act": "Expressive",
        "RobotText": "I'm here to help. What do you need?",
    },
    {
        "Trigger": "error",
        "Inferred Intent": "Request to speak/help",
        "Priority": "Critical",
        "ConfidenceThrs.": 0.90,
        "Escalated Action": "Shutdown safely",
        "escalationCount": None,
        "Robot Speech Act": "Commissive/Expressive",
        "RobotText": "An error occurred. Retrying operation...",
    },
    {
        "Trigger": "long time being still",
        "Inferred Intent": "User confused / waiting",
        "Priority": "High",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Commissive/Expressive",
        "RobotText": "You've been still for a while. Do you need help?",
    },
    {
        "Trigger": "end of user speech",
        "Inferred Intent": "Provide action / speech feedback",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Expressive + Commissive",
        "RobotText": "I understand. Let me continue with the next step.",
    },
    {
        "Trigger": "end of user movement",
        "Inferred Intent": "Provide action / speech feedback",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Expressive + Commissive",
        "RobotText": "Good movement! Here's what's next.",
    },
    {
        "Trigger": "system event: cognitive game phase X",
        "Inferred Intent": "Provide action / speech feedback",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Expressive + Commissive",
        "RobotText": "Let's proceed to the next phase of the cognitive game.",
    },
    {
        "Trigger": "system event: IoT / Smart home event",
        "Inferred Intent": "Provide action / speech feedback",
        "Priority": "Medium",
        "ConfidenceThrs.": 0.60,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Expressive + Commissive",
        "RobotText": "I detected a smart home event. Processing...",
    },
]


class RuleEngine:
    def __init__(self):
        # Namesto DataFrame zdaj uporabljamo navaden Python seznam
        self.rules: List[Dict] = RULES

    def get_triggers(self) -> list:
        """
        Vrne seznam unikatnih triggerjev, ki jih UI uporabi za gumbe.
        """
        return sorted({r["Trigger"] for r in self.rules})

    def select_rule(self, trigger: str):
        """
        Najde pravilo za izbran trigger.
        Če jih je več, vzamemo tistega z najvišjo prioriteto.
        """
        matches = [r for r in self.rules if r["Trigger"] == trigger]
        if not matches:
            return None

        matches.sort(
            key=lambda r: PRIORITY_ORDER.get(r.get("Priority", "Low"), 1),
            reverse=True,
        )
        row = matches[0]

        return {
            "trigger": row["Trigger"],
            "inferred_intent": row.get("Inferred Intent"),
            "priority": row.get("Priority"),
            "confidence_thrs": row.get("ConfidenceThrs."),
            "escalated_action": row.get("Escalated Action"),
            "escalation_count": row.get("escalationCount"),
            "speech_act": row.get("Robot Speech Act"),
            "robot_text": row.get("RobotText"),
        }




