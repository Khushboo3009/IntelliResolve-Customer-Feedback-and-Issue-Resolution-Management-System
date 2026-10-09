from services.text_preprocessor import (
    clean_text,
    extract_keywords,
)

from services.sentiment_engine import (
    analyze_sentiment,
)

from services.issue_engine import (
    detect_issue,
)

from services.severity_engine import (
    calculate_severity,
)


def analyze_feedback(feedback_text, existing_category=None):

    text = clean_text(feedback_text)

    sentiment = analyze_sentiment(text)

    issue = detect_issue(text)

    severity = calculate_severity(
        text,
        sentiment["label"],
        issue["issue"],
    )

    keywords = extract_keywords(text)

    # --------------------------------------------------
    # CATEGORY
    # --------------------------------------------------

    if existing_category:
        category = existing_category
        category_confidence = 100

    elif issue["issue"] != "Other":
        category = issue["issue"]
        category_confidence = int(
            issue["confidence"] * 100
        )

    else:
        category = "Other"
        category_confidence = 0

    # --------------------------------------------------
    # PRIORITY
    # --------------------------------------------------

    priority_map = {
        "Critical": 100,
        "High": 75,
        "Medium": 50,
        "Low": 25,
    }

    priority_score = priority_map.get(
        severity,
        25,
    )

    # --------------------------------------------------
    # COMPLAINT
    # --------------------------------------------------

    is_complaint = (
        sentiment["label"] == "Negative"
        or issue["issue"] != "Other"
    )

    return {
        "sentiment": sentiment["label"],

        "sentiment_score": int(
            sentiment["score"] * 100
        ),

        "detected_category": category,

        "category_confidence":
            category_confidence,

        "priority": severity,

        "priority_score":
            priority_score,

        "is_complaint":
            is_complaint,

        "keywords":
            keywords,

        "evidence":
            issue["evidence"],

        "issue_type":
            issue["issue"],

        "issue_confidence":
            issue["confidence"],
    }