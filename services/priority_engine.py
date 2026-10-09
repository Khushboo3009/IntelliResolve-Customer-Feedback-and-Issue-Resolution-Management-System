from services.nlp_engine import (
    normalize_text,
)


HIGH_PRIORITY_WORDS = {
    "fraud",
    "security",
    "unsafe",
    "danger",
    "critical",
    "urgent",
    "broken",
    "failed",
    "failure",
    "unacceptable",
    "refund",
    "complaint",
}


def calculate_priority(
    text,
    sentiment_score,
    category_confidence,
):

    text = normalize_text(text)

    score = 0

    # Negative sentiment
    if sentiment_score < 0:

        score += abs(
            sentiment_score
        )

    # High-risk keywords
    for word in HIGH_PRIORITY_WORDS:

        if word in text:

            score += 20

    # Confidence contribution
    score += int(
        category_confidence * 0.2
    )

    score = min(
        100,
        score,
    )

    if score >= 75:

        priority = "critical"

    elif score >= 50:

        priority = "high"

    elif score >= 25:

        priority = "medium"

    else:

        priority = "low"

    return {
        "priority": priority,
        "score": score,
    }