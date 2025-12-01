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

FEEDBACK_INTENT = "Provide action / speech feedback"


@dataclass
class RobotFSM:
    state: str = S0_GREETING
    step_count: int = 0
    escalation_counts: dict = field(default_factory=lambda: defaultdict(int))

    def to_dict(self):
        return {
            "state": self.state,
            "step_count": self.step_count,
            "escalation_counts": dict(self.escalation_counts),
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
        return fsm

    def update_state(self, inferred_intent: str) -> str:
        """
        Zelo enostavna logika prehodov med stanji.
        Tu imaš prostor, da jo kasneje nadgradiš.
        """
        current = self.state
        next_state = current

        if current == S0_GREETING:
            # Po pozdravu se premaknemo v razlago naloge
            next_state = S1_EXPLANATION

        elif current == S1_EXPLANATION:
            if inferred_intent == "Positive affect":
                next_state = S2_EXERCISE
            elif inferred_intent in NEGATIVE_INTENTS:
                # ostanemo v razlagi, dodatna pojasnila
                next_state = S1_EXPLANATION
            else:
                next_state = S2_EXERCISE

        elif current == S2_EXERCISE:
            if inferred_intent in NEGATIVE_INTENTS:
                next_state = S3_BREAK
            elif inferred_intent == FEEDBACK_INTENT:
                # recimo da feedback ob koncu vaje vodi v zaključek
                next_state = S4_FEEDBACK
            else:
                next_state = S2_EXERCISE

        elif current == S3_BREAK:
            # po odmoru nazaj na vajo, lahko pa k feedbacku
            if inferred_intent == "Positive affect":
                next_state = S2_EXERCISE
            elif inferred_intent == FEEDBACK_INTENT:
                next_state = S4_FEEDBACK

        elif current == S4_FEEDBACK:
            # končno stanje – ostanemo tam
            next_state = S4_FEEDBACK

        # eskalacije
        if inferred_intent in NEGATIVE_INTENTS:
            self.escalation_counts[inferred_intent] += 1

        self.state = next_state
        self.step_count += 1
        return next_state

    def total_escalations(self) -> int:
        return sum(self.escalation_counts.values())

    def is_final(self) -> bool:
        return self.state == S4_FEEDBACK
