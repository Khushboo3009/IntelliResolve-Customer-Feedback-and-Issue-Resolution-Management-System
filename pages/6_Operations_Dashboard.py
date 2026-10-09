import streamlit as st
from sqlalchemy import select, func

from db.engine import SessionLocal
from db.models import (
    Feedback,
    Issue,
    IssueIntervention,
    InterventionOutcome,
    Dataset,
)

from styles.theme import apply_theme

apply_theme()

st.title("Executive Operations Dashboard")
st.caption("Enterprise Operational Intelligence")

with SessionLocal() as db:

    feedback = db.scalar(select(func.count(Feedback.id))) or 0
    issues = db.scalar(select(func.count(Issue.id))) or 0

    critical = db.scalar(
        select(func.count(Issue.id))
        .where(Issue.severity=="critical")
    ) or 0

    interventions = db.scalar(
        select(func.count(IssueIntervention.id))
    ) or 0

    outcomes = db.scalar(
        select(func.count(InterventionOutcome.id))
    ) or 0

    datasets = db.scalar(
        select(func.count(Dataset.id))
    ) or 0


c1,c2,c3,c4 = st.columns(4)

c1.metric("Feedback", feedback)
c2.metric("Issues", issues)
c3.metric("Critical", critical)
c4.metric("Datasets", datasets)

st.divider()

c5,c6 = st.columns(2)

c5.metric("Interventions", interventions)
c6.metric("Measured Outcomes", outcomes)

st.divider()

st.subheader("Operational Status")

if critical > 0:
    st.error(f"{critical} critical operational issues require attention.")
else:
    st.success("No critical issues.")