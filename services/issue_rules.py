ISSUE_STATUS_OPEN = "open"

SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def normalize_severity(value):
    """
    Normalize severity values before storing them.
    """

    if not value:
        return "medium"

    value = str(value).strip().lower()

    if value not in SEVERITY_RANK:
        return "medium"

    return value


def higher_severity(first, second):
    """
    Return the more severe of two severity values.
    """

    first = normalize_severity(first)
    second = normalize_severity(second)

    if (
        SEVERITY_RANK[first]
        >= SEVERITY_RANK[second]
    ):
        return first

    return second