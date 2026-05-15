"""
GeoCivic Insight — ML Pipeline
Lightweight implementations of summarize, classify, and sentiment functions.
No heavy ML models, no internet APIs.
"""

import re


def summarize(text):
    """
    Extractive summarization: split text into sentences and return up to 3.

    Args:
        text (str or None): Input text to summarize

    Returns:
        list: List of summary sentence strings
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return ["No achievements data available."]

    # Split on sentence boundaries (period, exclamation, question mark)
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in raw if s.strip()]

    if not sentences:
        return ["No achievements data available."]

    # Return max 3 sentences
    return sentences[:3]


def classify_achievement(text):
    """
    Classify an achievement string into a single category using keyword matching.

    Args:
        text (str or None): Achievement text to classify

    Returns:
        str: One of Infrastructure, Education, Healthcare,
             Women_Empowerment, Agriculture, Youth, Unknown
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return "Unknown"

    text_lower = text.lower()

    keywords = {
        "Education":         ["school", "student", "college", "education"],
        "Healthcare":        ["hospital", "health", "medical"],
        "Infrastructure":    ["road", "bridge", "water", "metro", "highway"],
        "Women_Empowerment": ["women", "self-help", "female"],
        "Agriculture":       ["farming", "farmer", "agriculture"],
        "Youth":             ["youth", "skill", "jobs", "training"],
    }

    for category, words in keywords.items():
        if any(w in text_lower for w in words):
            return category

    return "Unknown"


def sentiment_score(headlines):
    """
    Analyse sentiment of a list of news headlines.

    Args:
        headlines (list): List of headline strings

    Returns:
        dict: {label, score, positive, negative, neutral, breakdown}
    """
    if not headlines or not isinstance(headlines, list) or len(headlines) == 0:
        return {
            "label": "Neutral",
            "score": 0.0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "breakdown": {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0},
        }

    positive_words = ["excellent", "praised", "award", "outstanding", "development", "good"]
    negative_words = ["corruption", "protest", "fails", "scandal", "bad"]

    pos_count = 0
    neg_count = 0
    neu_count = 0

    for headline in headlines:
        h = headline.lower()
        has_pos = any(w in h for w in positive_words)
        has_neg = any(w in h for w in negative_words)

        if has_pos and not has_neg:
            pos_count += 1
        elif has_neg and not has_pos:
            neg_count += 1
        else:
            neu_count += 1

    total = len(headlines)
    raw_score = pos_count - neg_count

    # Normalize score to [-1.0, 1.0]
    if total > 0:
        score = max(-1.0, min(1.0, raw_score / total))
    else:
        score = 0.0

    if pos_count > neg_count:
        label = "Positive"
    elif neg_count > pos_count:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "label": label,
        "score": score,
        "positive": pos_count,
        "negative": neg_count,
        "neutral": neu_count,
        "breakdown": {
            "compound": score,
            "pos": pos_count / total if total else 0.0,
            "neg": neg_count / total if total else 0.0,
            "neu": neu_count / total if total else 1.0,
        },
    }