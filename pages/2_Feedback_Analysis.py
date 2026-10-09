import streamlit as st

from sqlalchemy import (
    func,
    select,
)

from styles.theme import apply_theme

from services.analysis_service import (
    analyze_pending_feedback,
)

from db.engine import SessionLocal

from db.models import (
    Feedback,
    FeedbackAnalysis,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="IntelliResolve - Feedback Intelligence",
    page_icon="🧠",
    layout="wide",
)

apply_theme()


from ui.header import app_header

app_header(
    "🧠 Feedback Intelligence"
)

st.caption(
    "Real-time analysis of customer feedback "
    "stored in MySQL."
)


# ============================================================
# DATABASE SUMMARY
# ============================================================

with SessionLocal() as db:

    total_feedback = (
        db.scalar(
            select(
                func.count(
                    Feedback.id
                )
            )
        )
        or 0
    )

    analyzed_feedback = (
        db.scalar(
            select(
                func.count(
                    FeedbackAnalysis.id
                )
            )
        )
        or 0
    )

    pending_feedback = max(
        0,
        total_feedback
        - analyzed_feedback,
    )


# ============================================================
# METRICS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Feedback",
        total_feedback,
    )

with col2:

    st.metric(
        "Analyzed",
        analyzed_feedback,
    )

with col3:

    st.metric(
        "Pending Analysis",
        pending_feedback,
    )


st.divider()


# ============================================================
# ANALYSIS
# ============================================================

st.subheader(
    "Feedback Analysis Engine"
)


batch_size = st.number_input(
    "Records to process",
    min_value=1,
    max_value=5000,
    value=500,
    step=100,
)


if st.button(
    "▶ Analyze Pending Feedback",
    type="primary",
    width="stretch",
):

    try:

        with st.spinner(
            "Analyzing real feedback records..."
        ):

            result = analyze_pending_feedback(
                batch_size=int(batch_size)
            )

        st.success(
            f"Processed: {result.get('processed', 0)} | "
            f"Failed: {result.get('failed', 0)}"
        )

        st.rerun()

    except Exception as exc:

        st.error(
            f"Feedback analysis failed: {exc}"
        )


# ============================================================
# RESULTS
# ============================================================

st.subheader(
    "Recent Feedback Intelligence Results"
)


with SessionLocal() as db:

    results = db.execute(
        select(
            Feedback.id,
            Feedback.customer_id,
            Feedback.feedback_text,
            FeedbackAnalysis.sentiment,
            FeedbackAnalysis.sentiment_score,
            FeedbackAnalysis.detected_category,
            FeedbackAnalysis.category_confidence,
            FeedbackAnalysis.priority,
            FeedbackAnalysis.priority_score,
            FeedbackAnalysis.is_complaint,
        )
        .join(
            FeedbackAnalysis,
            FeedbackAnalysis.feedback_id
            == Feedback.id,
        )
        .order_by(
            FeedbackAnalysis.processed_at.desc()
        )
        .limit(100)
    ).all()


if results:

    table_data = []

    for row in results:

        table_data.append(
            {
                "Feedback ID": row.id,
                "Customer": (
                    row.customer_id
                    or "Unknown"
                ),
                "Feedback": row.feedback_text,
                "Sentiment": row.sentiment,
                "Sentiment Score": (
                    row.sentiment_score
                ),
                "Category": (
                    row.detected_category
                ),
                "Category Confidence": (
                    row.category_confidence
                ),
                "Priority": row.priority,
                "Priority Score": (
                    row.priority_score
                ),
                "Complaint": (
                    "Yes"
                    if row.is_complaint
                    else "No"
                ),
            }
        )

    st.dataframe(
        table_data,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No analyzed feedback available yet."
    )