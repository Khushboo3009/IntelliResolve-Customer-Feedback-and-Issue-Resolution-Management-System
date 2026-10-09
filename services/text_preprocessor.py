import re


STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "is",
    "are",
    "was",
    "were",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "this",
    "that",
    "it",
    "my",
    "i",
    "we",
    "you",
    "they",
    "have",
    "has",
    "had",
}


def clean_text(text):
    """
    Normalize customer feedback text.
    """

    if text is None:
        return ""

    text = str(text)

    # Remove excessive whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    # Remove control characters
    text = re.sub(
        r"[\x00-\x1f\x7f]",
        " ",
        text,
    )

    return text.strip()


def tokenize(text):
    """
    Basic explainable tokenization.
    """

    text = clean_text(text)

    tokens = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower(),
    )

    return [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]


def extract_keywords(
    text,
    limit=10,
):
    """
    Extract meaningful words from feedback.
    """

    tokens = tokenize(text)

    frequency = {}

    for token in tokens:

        frequency[token] = (
            frequency.get(token, 0) + 1
        )

    sorted_words = sorted(
        frequency.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        word
        for word, _ in sorted_words[:limit]
    ]