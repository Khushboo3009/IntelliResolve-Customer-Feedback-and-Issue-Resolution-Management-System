import streamlit as st
from sqlalchemy import select, func

from db.engine import SessionLocal
from db.models import (
    InterventionOutcome,
)

from styles.theme import apply_theme

apply_theme()

st.title("Predictive Intelligence")

with SessionLocal() as db:

    avg = db.scalar(
        select(
            func.avg(
                InterventionOutcome.improvement_percentage
            )
        )
    ) or 0

st.metric(
    "Average Improvement",
    f"{avg:.1f}%"
)

if avg >= 60:
    st.success("Operational trend is improving.")

elif avg >= 30:
    st.warning("Moderate operational improvement.")

else:
    st.error("Operational performance needs attention.")

st.info(
    "Future forecasting will use historical intervention outcomes rather than simulated values."
)