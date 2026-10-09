CRITICAL_TERMS = {
    "fraud",
    "unsafe",
    "security",
    "data breach",
    "injury",
    "danger",
    "emergency",
    "legal",
}

HIGH_TERMS = {
    "payment failed",
    "refund",
    "fraud",
    "account locked",
    "not delivered",
    "damaged",
    "broken",
    "complaint",
}

MEDIUM_TERMS = {
    "delay",
    "late",
    "problem",
    "issue",
    "error",
    "slow",
}


def calculate_severity(
    text,
    sentiment,
    issue,
):
    """
    Determine operational severity.
    """

    text = str(
        text or ""
    ).lower()

    # Critical
    for term in CRITICAL_TERMS:

        if term in text:

            return "Critical"

    # High
    for term in HIGH_TERMS:

        if term in text:

            return "High"

    # Negative sentiment + recognized issue
    if (
        sentiment == "Negative"
        and issue != "Other"
    ):

        return "High"

    # Medium
    for term in MEDIUM_TERMS:

        if term in text:

            return "Medium"

    return "Low"