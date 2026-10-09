from services.text_preprocessor import (
    clean_text,
)


POSITIVE_WORDS = {
    "good",
    "great",
    "excellent",
    "amazing",
    "happy",
    "satisfied",
    "helpful",
    "fast",
    "easy",
    "perfect",
    "love",
    "resolved",
    "thank",
    "thanks",
    "best",
    "awesome",
}


NEGATIVE_WORDS = {
    "bad",
    "poor",
    "terrible",
    "horrible",
    "angry",
    "unhappy",
    "slow",
    "late",
    "delay",
    "delayed",
    "broken",
    "failed",
    "failure",
    "problem",
    "issue",
    "complaint",
    "refund",
    "cancelled",
    "cancel",
    "wrong",
    "fraud",
    "error",
    "unacceptable",
    "disappointed",
}


def analyze_sentiment(text):
    """
    Explainable local sentiment analysis.
    """

    text = clean_text(text).lower()

    words = text.split()

    positive_count = sum(
        1
        for word in words
        if word in POSITIVE_WORDS
    )

    negative_count = sum(
        1
        for word in words
        if word in NEGATIVE_WORDS
    )

    total = (
        positive_count
        + negative_count
    )

    if total == 0:

        return {
            "label": "Neutral",
            "score": 0.0,
            "positive_count": 0,
            "negative_count": 0,
        }

    score = (
        positive_count - negative_count
    ) / total

    if score > 0.20:

        label = "Positive"

    elif score < -0.20:

        label = "Negative"

    else:

        label = "Neutral"

    return {
        "label": label,
        "score": round(score, 4),
        "positive_count": positive_count,
        "negative_count": negative_count,
    }