from services.nlp_engine import (
    normalize_text,
)


CATEGORY_KEYWORDS = {

    "Payment & Billing": [
        "payment",
        "billing",
        "bill",
        "invoice",
        "charged",
        "charge",
        "refund",
        "transaction",
        "price",
        "payment failed",
    ],

    "Delivery & Logistics": [
        "delivery",
        "shipping",
        "shipment",
        "package",
        "parcel",
        "late",
        "delay",
        "courier",
        "tracking",
    ],

    "Product Quality": [
        "quality",
        "defective",
        "damaged",
        "broken",
        "faulty",
        "product",
        "manufacturing",
    ],

    "Technical": [
        "app",
        "website",
        "login",
        "crash",
        "error",
        "bug",
        "technical",
        "server",
        "password",
        "software",
    ],

    "Customer Support": [
        "support",
        "agent",
        "representative",
        "help",
        "response",
        "service",
        "call center",
    ],

    "Account": [
        "account",
        "profile",
        "registration",
        "verification",
        "password",
        "login",
    ],

    "Service Quality": [
        "service",
        "experience",
        "slow",
        "waiting",
        "response",
        "poor service",
    ],
}


def detect_category(text):

    text = normalize_text(text)

    if not text:

        return {
            "category": "Unclassified",
            "confidence": 0,
        }

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1

        scores[category] = score

    best_category = max(
        scores,
        key=scores.get,
    )

    best_score = scores[
        best_category
    ]

    if best_score == 0:

        return {
            "category": "Other",
            "confidence": 0,
        }

    confidence = min(
        100,
        best_score * 25,
    )

    return {
        "category": best_category,
        "confidence": confidence,
    }