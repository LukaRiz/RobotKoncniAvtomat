# fsm.py - Finite State Machine implementation

from dataclasses import dataclass, field
from collections import defaultdict

# Osnovna stanja (lahko poimenuješ tudi drugače, samo konsistentno)
S0_GREETING = "S0_GREETING"               # pozdrav
S1_EXPLANATION = "S1_EXPLANATION"         # razlaga naloge
S2_EXERCISE = "S2_EXERCISE"               # izvajanje vaje (cikel)
S3_BREAK = "S3_BREAK"                     # odmor / preusmeritev pozornosti
S4_FEEDBACK = "S4_FEEDBACK"               # povratna informacija / zaključek

NEGATIVE_INTENTS = {
    "User frustrated / overloaded",
    "Disengagement risk",
}

POSITIVE_INTENTS = {
    "Positive affect",
}

FEEDBACK_INTENT = "Provide action / speech feedback"

# Konfiguracija za zaključek
MAX_ESCALATIONS = 3          # Po 3 eskalacijah ponudi zaključek
MAX_SUCCESS_STEPS = 5        # Po 5 uspešnih korakih v S2_EXERCISE → zaključek


@dataclass
class RobotFSM:
    state: str = S0_GREETING
    step_count: int = 0
    escalation_counts: dict = field(default_factory=lambda: defaultdict(int))
    success_steps: int = 0                 # Števec uspešnih korakov v S2_EXERCISE
    positive_interactions: int = 0         # Skupno pozitivnih interakcij
    negative_interactions: int = 0         # Skupno negativnih interakcij
    should_suggest_end: bool = False       # Ali naj robot predlaga zaključek
    end_reason: str = ""                   # Razlog za predlog zaključka

    def to_dict(self):
        return {
            "state": self.state,
            "step_count": self.step_count,
            "escalation_counts": dict(self.escalation_counts),
            "success_steps": self.success_steps,
            "positive_interactions": self.positive_interactions,
            "negative_interactions": self.negative_interactions,
            "should_suggest_end": self.should_suggest_end,
            "end_reason": self.end_reason,
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return cls()
        fsm = cls()
        fsm.state = data.get("state", S0_GREETING)
        fsm.step_count = data.get("step_count", 0)
        esc = data.get("escalation_counts", {})
        fsm.escalation_counts = defaultdict(int, esc)
        fsm.success_steps = data.get("success_steps", 0)
        fsm.positive_interactions = data.get("positive_interactions", 0)
        fsm.negative_interactions = data.get("negative_interactions", 0)
        fsm.should_suggest_end = data.get("should_suggest_end", False)
        fsm.end_reason = data.get("end_reason", "")
        return fsm

    def update_state(self, inferred_intent: str) -> str:
        """
        Logika prehodov med stanji z izboljšano logiko zaključka.
        
        Zaključek se sproži:
        - Po MAX_ESCALATIONS eskalacijah (predlog zaključka)
        - Po MAX_SUCCESS_STEPS uspešnih korakih v S2_EXERCISE
        - Ob eksplicitnem feedback intentu
        - Ob timeout-u (obravnava se v app.py)
        """
        current = self.state
        next_state = current
        self.should_suggest_end = False
        self.end_reason = ""

        # Štej pozitivne/negativne interakcije
        if inferred_intent in POSITIVE_INTENTS:
            self.positive_interactions += 1
        elif inferred_intent in NEGATIVE_INTENTS:
            self.negative_interactions += 1
            self.escalation_counts[inferred_intent] += 1

        # ----- PREHODI MED STANJI -----

        if current == S0_GREETING:
            # Po pozdravu se premaknemo v razlago naloge
            next_state = S1_EXPLANATION

        elif current == S1_EXPLANATION:
            if inferred_intent in POSITIVE_INTENTS:
                next_state = S2_EXERCISE
            elif inferred_intent in NEGATIVE_INTENTS:
                # ostanemo v razlagi, dodatna pojasnila
                next_state = S1_EXPLANATION
            else:
                next_state = S2_EXERCISE

        elif current == S2_EXERCISE:
            # Štej uspešne korake (ko ni negativen intent)
            if inferred_intent not in NEGATIVE_INTENTS:
                self.success_steps += 1

            if inferred_intent in NEGATIVE_INTENTS:
                next_state = S3_BREAK
            elif inferred_intent == FEEDBACK_INTENT:
                next_state = S4_FEEDBACK
            elif self.success_steps >= MAX_SUCCESS_STEPS:
                # Avtomatski zaključek po N uspešnih korakih
                next_state = S4_FEEDBACK
                self.end_reason = "success_steps"
            else:
                next_state = S2_EXERCISE

        elif current == S3_BREAK:
            # Reset success_steps po odmoru
            self.success_steps = 0
            
            if inferred_intent in POSITIVE_INTENTS:
                next_state = S2_EXERCISE
            elif inferred_intent == FEEDBACK_INTENT:
                next_state = S4_FEEDBACK
            else:
                # Ostanemo v odmoru, če ni pozitivnega signala
                next_state = S3_BREAK

        elif current == S4_FEEDBACK:
            # končno stanje – ostanemo tam
            next_state = S4_FEEDBACK

        # ----- PREVERJANJE ESKALACIJ -----
        total_esc = self.total_escalations()
        if total_esc >= MAX_ESCALATIONS and not self.is_final():
            self.should_suggest_end = True
            self.end_reason = "max_escalations"

        self.state = next_state
        self.step_count += 1
        return next_state
    
    def force_end(self) -> str:
        """Prisili zaključek seje."""
        self.state = S4_FEEDBACK
        self.end_reason = "forced"
        return S4_FEEDBACK

    def total_escalations(self) -> int:
        return sum(self.escalation_counts.values())

    def is_final(self) -> bool:
        return self.state == S4_FEEDBACK
    
    def get_statistics(self) -> dict:
        """Vrne statistiko seje za UI in evalvacijo."""
        total_interactions = self.positive_interactions + self.negative_interactions
        return {
            "step_count": self.step_count,
            "positive_interactions": self.positive_interactions,
            "negative_interactions": self.negative_interactions,
            "total_escalations": self.total_escalations(),
            "escalation_breakdown": dict(self.escalation_counts),
            "success_steps": self.success_steps,
            "current_state": self.state,
            "is_final": self.is_final(),
            "positive_ratio": round(self.positive_interactions / total_interactions, 2) if total_interactions > 0 else 0,
            "should_suggest_end": self.should_suggest_end,
            "end_reason": self.end_reason,
        }
    
    def get_state_info(self) -> dict:
        """Vrne informacije o trenutnem stanju za vizualizacijo."""
        state_descriptions = {
            S0_GREETING: {"name": "Pozdrav", "color": "blue", "icon": "👋"},
            S1_EXPLANATION: {"name": "Razlaga", "color": "purple", "icon": "📖"},
            S2_EXERCISE: {"name": "Vaja", "color": "green", "icon": "🎯"},
            S3_BREAK: {"name": "Odmor", "color": "orange", "icon": "☕"},
            S4_FEEDBACK: {"name": "Zaključek", "color": "teal", "icon": "✅"},
        }
        return state_descriptions.get(self.state, {"name": "Neznano", "color": "gray", "icon": "❓"})
