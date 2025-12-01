# rules_loader.py
"""
RuleEngine brez Excela – pravila so hardcodana v tej datoteki.

Vsako pravilo ima:
- Trigger: ime gumba / dogodka
- Inferred Intent: kaj "razume" robot
- Priority: High / Medium / Low
- Robot Speech Act: tip odgovora
- RobotText: dejanski tekst, ki ga robot pove

Če boš kasneje rabil več pravil, samo dodaš nove vnose v RULES spodaj.
"""

from typing import List, Dict

PRIORITY_ORDER = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}

# *** TUKAJ SI DEFINIRAŠ SVOJA PRAVILA ***
# Trigger je točno to, kar bo pisalo na gumbu v UI.
RULES: List[Dict] = [
    {
        "Trigger": "Pozdrav uporabniku",
        "Inferred Intent": "Positive affect",
        "Priority": "High",
        "ConfidenceThrs.": None,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Greeting",
        "RobotText": "Živjo! Vesel sem, da sva se srečala. Danes bova skupaj delala na kratki vaji za koncentracijo.",
    },
    {
        "Trigger": "Razloži nalogo",
        "Inferred Intent": "Provide task explanation",
        "Priority": "High",
        "ConfidenceThrs.": None,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Task explanation",
        "RobotText": "Naloga je preprosta: sledil_a boš mojim navodilom in poskusil_a čim bolj zbrano odgovarjati. Če bo kaj nejasno, mi samo sporoči.",
    },
    {
        "Trigger": "Uporabnik motiviran",
        "Inferred Intent": "Positive affect",
        "Priority": "High",
        "ConfidenceThrs.": None,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Encouragement",
        "RobotText": "Super, vidim, da ti gre dobro! Nadaljujeva v istem ritmu. Osredotoči se na naslednjo nalogo.",
    },
    {
        "Trigger": "Uporabnik preobremenjen",
        "Inferred Intent": "User frustrated / overloaded",
        "Priority": "High",
        "ConfidenceThrs.": None,
        "Escalated Action": "Offer break",
        "escalationCount": 1,
        "Robot Speech Act": "Soothing / support",
        "RobotText": "Vidim, da ti je malo naporno. Ni panike – vzameva si trenutek, upočasniva in greva korak za korakom.",
    },
    {
        "Trigger": "Predlagaj odmor",
        "Inferred Intent": "Disengagement risk",
        "Priority": "High",
        "ConfidenceThrs.": None,
        "Escalated Action": None,
        "escalationCount": 1,
        "Robot Speech Act": "Break suggestion",
        "RobotText": "Predlagam kratek odmor. Zapri oči, globoko vdihni in izdihni nekajkrat. Ko boš pripravljen_a, nadaljujeva.",
    },
    {
        "Trigger": "Nadaljuj z vajo",
        "Inferred Intent": "Positive affect",
        "Priority": "Medium",
        "ConfidenceThrs.": None,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Continue task",
        "RobotText": "Odlično, nadaljujeva! Zdaj se še enkrat osredotoči na nalogo pred tabo.",
    },
    {
        "Trigger": "Povzetek vaje",
        "Inferred Intent": "Provide action / speech feedback",
        "Priority": "High",
        "ConfidenceThrs.": None,
        "Escalated Action": None,
        "escalationCount": None,
        "Robot Speech Act": "Feedback / summary",
        "RobotText": "To je to za danes! Zelo dobro ti je šlo. Pomembno je, da vajo vzameš kot trening – vsakič bo šlo lažje.",
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
