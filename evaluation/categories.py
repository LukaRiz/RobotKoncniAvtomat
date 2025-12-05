# evaluation/categories.py - Kategorizacija intentov

"""
Definicije kategorij intentov za analizo vedenja uporabnika.
"""

INTENT_CATEGORIES = {
    "positive": ["Engaged", "Positive Affect", "Acknowledgment", "Ready", "Completion", "Greeting"],
    "negative": ["Confusion", "Stress", "Frustration", "Disengagement", "Overload", "Error"],
    "neutral": ["Waiting", "Hesitation", "Attention Shift", "Transition", "Unknown"],
}

