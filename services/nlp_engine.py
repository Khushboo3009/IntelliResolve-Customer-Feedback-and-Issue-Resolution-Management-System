import re


POSITIVE_WORDS = {
    "good",
    "great",
    "excellent",
    "amazing",
    "helpful",
    "fast",
    "easy",
    "satisfied",
    "happy",
    "perfect",
    "love",
    "improved",
    "resolved",
    "quick",
}

NEGATIVE_WORDS = {
    "bad",
    "poor",
    "worst",
    "terrible",
    "awful",
    "slow",
    "broken",
    "failed",
    "failure",
    "problem",
    "issue",
    "complaint",
    "angry",
    "unhappy",
    "refund",
    "delay",
    "late",
    "error",
    "wrong",
    "unacceptable",
}


def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def tokenize(text):

    text = normalize_text(text)

    return re.findall(
        r"\b[a-zA-Z]+\b",
        text,
    )


def calculate_sentiment(text):

    tokens = tokenize(text)

    if not tokens:

        return {
            "sentiment": "neutral",
            "score": 0,
        }

    positive = sum(
        1
        for token in tokens
        if token in POSITIVE_WORDS
    )

    negative = sum(
        1
        for token in tokens
        if token in NEGATIVE_WORDS
    )

    raw_score = positive - negative

    if raw_score > 0:

        sentiment = "positive"

    elif raw_score < 0:

        sentiment = "negative"

    else:

        sentiment = "neutral"

    score = max(
        -100,
        min(
            100,
            raw_score * 20,
        ),
    )

    return {
        "sentiment": sentiment,
        "score": score,
    }