"""
Agent-modifiable target file.

Only edit this file during optimization loops.
"""

from __future__ import annotations


def predict_label(text: str) -> str:
    """
    Baseline classifier used by prepare.py.

    Return exactly "positive" or "negative".
    """
    lowered = text.lower()

    positive_tokens = ("good", "great", "love", "excellent", "helpful", "fast")
    negative_tokens = ("bad", "terrible", "hate", "awful", "slow", "broken")

    pos_hits = sum(token in lowered for token in positive_tokens)
    neg_hits = sum(token in lowered for token in negative_tokens)

    return "positive" if pos_hits >= neg_hits else "negative"
