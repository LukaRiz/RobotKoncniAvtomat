# evaluation/__init__.py - Glavni modul za evalvacijo

"""
Modul za strokovno evalvacijo sej glede na FSM in vzorce vedenja.
"""

from .scenarios import REFERENCE_SCENARIOS
from .categories import INTENT_CATEGORIES
from .functions import (
    classify_session,
    calculate_session_stats,
    calculate_scenario_match,
    evaluate_fsm_efficiency,
    generate_functional_evaluation,
    generate_summary,
    get_all_scenarios,
    get_attr,
)

__all__ = [
    "REFERENCE_SCENARIOS",
    "INTENT_CATEGORIES",
    "classify_session",
    "calculate_session_stats",
    "calculate_scenario_match",
    "evaluate_fsm_efficiency",
    "generate_functional_evaluation",
    "generate_summary",
    "get_all_scenarios",
    "get_attr",
]

