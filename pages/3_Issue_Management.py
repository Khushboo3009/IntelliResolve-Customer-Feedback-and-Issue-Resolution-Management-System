import streamlit as st
from sqlalchemy import select

from db.engine import SessionLocal
from db.models import Issue

from services.issue_engine import generate_issues

from styles.theme import apply_theme

apply_theme()

st.title("Issue Management")

st.caption("Automatic issue detection from real customer feedback.")

if st.button("Generate Issues", type="primary"):

    created = generate_issues()

    st.success(f"{created} issues created.")

st.divider()

with SessionLocal() as db:

    issues = db.scalars(
        select(Issue).order_by(
            Issue.id.desc()
        )
    ).all()

    if issues:

        for issue in issues:

            with st.container(border=True):

                c1, c2, c3 = st.columns([3,1,1])

                c1.subheader(issue.title)

                c2.metric("Severity", issue.severity.title())

                c3.metric("Count", issue.occurrence_count)

                st.write(issue.description)

                st.caption(f"Category: {issue.category}")