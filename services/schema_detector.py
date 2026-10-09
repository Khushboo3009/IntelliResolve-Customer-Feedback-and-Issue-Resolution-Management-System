import re
import unicodedata


# ============================================================
# COLUMN NAME NORMALIZATION
# ============================================================

def normalize_column_name(column):
    """
    Convert a column name into a normalized representation.

    Examples:
        "Customer Feedback" -> "customer_feedback"
        "Review Text"       -> "review_text"
        "Customer-ID"       -> "customer_id"
        "Submitted Date"    -> "submitted_date"
    """

    if column is None:
        return ""

    try:
        value = str(column).strip().lower()
    except Exception:
        return ""

    # Normalize unicode characters.
    value = unicodedata.normalize(
        "NFKD",
        value,
    )

    # Remove accents where possible.
    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    # Replace punctuation/separators with spaces.
    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    # Normalize whitespace.
    value = re.sub(
        r"\s+",
        " ",
        value,
    ).strip()

    # Convert to application-friendly form.
    return value.replace(
        " ",
        "_",
    )


# ============================================================
# ALIAS DEFINITIONS
# ============================================================

FEEDBACK_ALIASES = [
    # Direct names
    "feedback",
    "feedback_text",
    "feedback_message",
    "feedback_comment",
    "feedback_description",

    # Reviews
    "review",
    "review_text",
    "review_comment",
    "review_description",
    "customer_review",
    "customer_reviews",
    "product_review",
    "product_reviews",

    # Comments
    "comment",
    "comments",
    "comment_text",
    "customer_comment",
    "customer_comments",

    # Complaints
    "complaint",
    "complaints",
    "complaint_text",
    "complaint_description",
    "customer_complaint",
    "customer_complaints",

    # Messages
    "message",
    "messages",
    "message_text",
    "customer_message",

    # Description
    "description",
    "details",
    "detail",
    "remarks",
    "remark",
    "notes",
    "note",

    # Issues / problems
    "issue",
    "issues",
    "issue_description",
    "issue_text",
    "problem",
    "problem_description",
    "problem_text",

    # Text
    "text",
    "text_content",
    "content",
    "response",
    "customer_response",
    "customer_feedback_text",
]


CUSTOMER_ALIASES = [
    "customer_id",
    "customerid",
    "cust_id",
    "custid",
    "client_id",
    "clientid",
    "user_id",
    "userid",
    "member_id",
    "account_id",
    "customer_number",
    "customer_no",
    "client_number",
    "client_no",
    "user_number",
    "user_no",
    "customer",
    "customer_name",
    "client",
    "client_name",
    "user",
    "user_name",
    "customer_identifier",
]


CATEGORY_ALIASES = [
    "category",
    "categories",
    "issue_category",
    "feedback_category",
    "complaint_category",
    "review_category",
    "issue_type",
    "issue_types",
    "complaint_type",
    "complaint_types",
    "feedback_type",
    "feedback_types",
    "type",
    "classification",
    "class",
    "topic",
    "topics",
    "reason",
    "issue_reason",
    "department",
    "department_name",
    "business_category",
]


SOURCE_ALIASES = [
    "source",
    "sources",
    "channel",
    "channels",
    "source_channel",
    "feedback_channel",
    "submission_channel",
    "contact_channel",
    "platform",
    "platform_name",
    "submitted_via",
    "submission_source",
    "origin",
    "origin_source",
    "origin_channel",
]


DATE_ALIASES = [
    "date",
    "datetime",
    "timestamp",
    "time",
    "created_at",
    "created_date",
    "creation_date",
    "submitted_at",
    "submitted_date",
    "submission_date",
    "feedback_date",
    "feedback_time",
    "review_date",
    "review_time",
    "complaint_date",
    "complaint_time",
    "received_at",
    "received_date",
    "recorded_at",
    "recorded_date",
    "updated_at",
    "updated_date",
]


RATING_ALIASES = [
    "rating",
    "ratings",
    "score",
    "scores",
    "review_score",
    "customer_rating",
    "product_rating",
    "feedback_rating",
    "star_rating",
    "stars",
    "star",
    "rate",
    "satisfaction_score",
    "satisfaction_rating",
    "csat",
    "nps",
]


PRODUCT_ALIASES = [
    "product",
    "product_name",
    "product_id",
    "product_code",
    "item",
    "item_name",
    "item_id",
    "service",
    "service_name",
    "service_id",
    "model",
    "model_name",
    "sku",
    "sku_id",
]


REGION_ALIASES = [
    "region",
    "area",
    "location",
    "city",
    "state",
    "state_name",
    "country",
    "country_name",
    "zone",
    "territory",
    "region_name",
    "geography",
    "geographic_area",
]


# ============================================================
# ALIAS GROUPS
# ============================================================

FIELD_ALIASES = {
    "feedback_text": FEEDBACK_ALIASES,
    "customer_id": CUSTOMER_ALIASES,
    "category": CATEGORY_ALIASES,
    "source": SOURCE_ALIASES,
    "date": DATE_ALIASES,
    "rating": RATING_ALIASES,
    "product": PRODUCT_ALIASES,
    "region": REGION_ALIASES,
}


# ============================================================
# GENERIC TOKEN HELPERS
# ============================================================

def _tokens(value):
    """
    Convert normalized column name into individual tokens.

    Example:
        customer_feedback_text
        ->
        {"customer", "feedback", "text"}
    """

    normalized = normalize_column_name(
        value
    )

    if not normalized:
        return set()

    return {
        token
        for token in normalized.split("_")
        if token
    }


def _exact_match(
    normalized_column,
    aliases,
):
    """
    Check for an exact alias match.
    """

    return normalized_column in {
        normalize_column_name(alias)
        for alias in aliases
    }


def _contains_phrase(
    normalized_column,
    aliases,
):
    """
    Check whether a known alias appears as part of a
    normalized column name.
    """

    column_tokens = _tokens(
        normalized_column
    )

    if not column_tokens:
        return False

    for alias in aliases:

        alias_normalized = normalize_column_name(
            alias
        )

        alias_tokens = _tokens(
            alias_normalized
        )

        if not alias_tokens:
            continue

        if alias_tokens.issubset(
            column_tokens
        ):
            return True

    return False


# ============================================================
# SCORING
# ============================================================

def _score_column(
    normalized_column,
    field_name,
    aliases,
):
    """
    Calculate a confidence score for a column/field match.

    Higher score = stronger match.
    """

    if not normalized_column:
        return 0

    score = 0

    # --------------------------------------------------------
    # Exact alias
    # --------------------------------------------------------

    if _exact_match(
        normalized_column,
        aliases,
    ):
        score += 100


    # --------------------------------------------------------
    # Token-based match
    # --------------------------------------------------------

    column_tokens = _tokens(
        normalized_column
    )

    for alias in aliases:

        alias_normalized = normalize_column_name(
            alias
        )

        alias_tokens = _tokens(
            alias_normalized
        )

        if not alias_tokens:
            continue

        if alias_tokens.issubset(
            column_tokens
        ):
            score = max(
                score,
                70 + (
                    len(alias_tokens) * 5
                ),
            )


    # --------------------------------------------------------
    # Field-specific semantic detection
    # --------------------------------------------------------

    if field_name == "feedback_text":

        feedback_tokens = {
            "feedback",
            "review",
            "comment",
            "complaint",
            "message",
            "description",
            "remarks",
            "issue",
            "problem",
            "response",
            "text",
            "content",
        }

        if column_tokens & feedback_tokens:
            score = max(
                score,
                45,
            )

        if (
            "customer" in column_tokens
            and (
                column_tokens
                & feedback_tokens
            )
        ):
            score = max(
                score,
                85,
            )


    elif field_name == "customer_id":

        customer_tokens = {
            "customer",
            "client",
            "user",
            "member",
            "account",
        }

        identifier_tokens = {
            "id",
            "identifier",
            "number",
            "no",
        }

        if (
            "customer" in column_tokens
            and (
                column_tokens
                & identifier_tokens
            )
        ):
            score = max(
                score,
                80,
            )

        if (
            column_tokens
            & customer_tokens
        ):
            score = max(
                score,
                45,
            )


    elif field_name == "category":

        category_tokens = {
            "category",
            "type",
            "classification",
            "class",
            "topic",
            "reason",
            "department",
        }

        if (
            column_tokens
            & category_tokens
        ):
            score = max(
                score,
                55,
            )


    elif field_name == "source":

        source_tokens = {
            "source",
            "channel",
            "platform",
            "origin",
            "submission",
        }

        if (
            column_tokens
            & source_tokens
        ):
            score = max(
                score,
                55,
            )


    elif field_name == "date":

        date_tokens = {
            "date",
            "time",
            "timestamp",
            "created",
            "submitted",
            "received",
            "recorded",
            "updated",
        }

        if (
            column_tokens
            & date_tokens
        ):
            score = max(
                score,
                55,
            )


    elif field_name == "rating":

        rating_tokens = {
            "rating",
            "score",
            "star",
            "stars",
            "csat",
            "nps",
            "satisfaction",
        }

        if (
            column_tokens
            & rating_tokens
        ):
            score = max(
                score,
                60,
            )


    elif field_name == "product":

        product_tokens = {
            "product",
            "item",
            "service",
            "model",
            "sku",
        }

        if (
            column_tokens
            & product_tokens
        ):
            score = max(
                score,
                55,
            )


    elif field_name == "region":

        region_tokens = {
            "region",
            "area",
            "location",
            "city",
            "state",
            "country",
            "zone",
            "territory",
        }

        if (
            column_tokens
            & region_tokens
        ):
            score = max(
                score,
                55,
            )

    return score


# ============================================================
# FIND BEST COLUMN
# ============================================================

def _find_best_column(
    columns,
    field_name,
    aliases,
    used_columns,
):
    """
    Find the strongest matching column for a field.

    A column already assigned to another field is not reused
    unless there is no other possible candidate.
    """

    candidates = []

    for original in columns:

        normalized = normalize_column_name(
            original
        )

        if not normalized:
            continue

        score = _score_column(
            normalized,
            field_name,
            aliases,
        )

        if score <= 0:
            continue

        candidates.append(
            (
                score,
                original,
            )
        )

    if not candidates:
        return None

    # Highest confidence first.
    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    # Prefer an unused column.
    for score, original in candidates:

        if original not in used_columns:
            return original

    # If every candidate is already used, don't
    # automatically reuse it for another field.
    return None


# ============================================================
# FEEDBACK-SPECIFIC FALLBACK
# ============================================================

def _find_feedback_column(columns):
    """
    More aggressive fallback for feedback text.

    This is intentionally limited to text-like semantic names
    and avoids treating columns such as customer_id or rating
    as feedback.
    """

    feedback_keywords = [
        "feedback",
        "review",
        "comment",
        "complaint",
        "message",
        "remarks",
        "description",
        "response",
        "issue",
        "problem",
        "text",
        "content",
        "details",
        "narrative",
        "experience",
        "suggestion",
    ]

    candidates = []

    for original in columns:

        normalized = normalize_column_name(
            original
        )

        tokens = _tokens(
            normalized
        )

        if not tokens:
            continue

        # Explicit semantic matches.
        keyword_count = sum(
            1
            for keyword in feedback_keywords
            if keyword in tokens
        )

        if keyword_count == 0:
            continue

        score = keyword_count * 20

        # Strong combinations.
        if (
            "customer" in tokens
            and (
                tokens
                & {
                    "feedback",
                    "review",
                    "comment",
                    "complaint",
                }
            )
        ):
            score += 30

        if "text" in tokens:
            score += 15

        if "description" in tokens:
            score += 15

        candidates.append(
            (
                score,
                original,
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


# ============================================================
# MAIN SCHEMA DETECTOR
# ============================================================

def detect_schema(columns):
    """
    Automatically detect useful fields from arbitrary dataset
    column names.

    Existing application mapping keys are preserved:

        feedback_text
        customer_id
        category
        source

    Additional optional fields:

        date
        rating
        product
        region

    Returns:

        {
            "mapping": {...},
            "columns": [...],
            "normalized_columns": {...},
            "confidence": {...},
            "detected_fields": [...],
            "missing_fields": [...]
        }
    """

    if columns is None:
        columns = []

    # --------------------------------------------------------
    # Convert to a stable list.
    # --------------------------------------------------------

    original_columns = []

    for column in columns:

        if column is None:
            continue

        try:
            value = str(column).strip()
        except Exception:
            continue

        if not value:
            continue

        original_columns.append(
            value
        )


    # --------------------------------------------------------
    # Remove duplicate column names while preserving order.
    # --------------------------------------------------------

    unique_columns = []

    seen = set()

    for column in original_columns:

        key = column.lower()

        if key in seen:
            continue

        seen.add(key)

        unique_columns.append(
            column
        )


    # --------------------------------------------------------
    # Normalized representation.
    # --------------------------------------------------------

    normalized_columns = {
        column: normalize_column_name(
            column
        )
        for column in unique_columns
    }


    mapping = {}
    confidence = {}
    used_columns = set()


    # ========================================================
    # DETECTION ORDER
    # ========================================================
    #
    # Feedback is detected first because it is the most
    # important field for IntelliResolve.
    #
    # ========================================================

    detection_order = [
        "feedback_text",
        "customer_id",
        "category",
        "source",
        "date",
        "rating",
        "product",
        "region",
    ]


    for field_name in detection_order:

        aliases = FIELD_ALIASES.get(
            field_name,
            [],
        )

        column = _find_best_column(
            unique_columns,
            field_name,
            aliases,
            used_columns,
        )

        if column is not None:

            normalized = normalize_column_name(
                column
            )

            score = _score_column(
                normalized,
                field_name,
                aliases,
            )

            # Only accept reasonably confident matches.
            if score >= 45:

                mapping[field_name] = column

                confidence[field_name] = score

                used_columns.add(
                    column
                )


    # ========================================================
    # FEEDBACK FALLBACK
    # ========================================================

    if "feedback_text" not in mapping:

        fallback = _find_feedback_column(
            unique_columns
        )

        if fallback is not None:

            mapping[
                "feedback_text"
            ] = fallback

            confidence[
                "feedback_text"
            ] = 40

            used_columns.add(
                fallback
            )


    # ========================================================
    # BUILD RESULT INFORMATION
    # ========================================================

    detected_fields = list(
        mapping.keys()
    )

    missing_fields = [
        field
        for field in FIELD_ALIASES
        if field not in mapping
    ]


    return {
        "mapping": mapping,

        "columns": unique_columns,

        "normalized_columns": (
            normalized_columns
        ),

        "confidence": confidence,

        "detected_fields": (
            detected_fields
        ),

        "missing_fields": (
            missing_fields
        ),
    }