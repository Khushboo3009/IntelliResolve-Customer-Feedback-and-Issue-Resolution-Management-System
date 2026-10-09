import streamlit as st
from sqlalchemy import select

from db.engine import SessionLocal

from db.models import (
    Dataset,
    Issue,
    IssueIntervention,
    InterventionOutcome,
)

from styles.theme import apply_theme


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="IntelliResolve - History",
    page_icon="🗂️",
    layout="wide",
)

apply_theme()


st.title("Enterprise History")

st.caption(
    "Historical records stored in the IntelliResolve database."
)


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "Datasets",
        "Issues",
        "Interventions",
        "Outcomes",
    ]
)


# ============================================================
# DATASETS
# ============================================================

with tabs[0]:

    with SessionLocal() as db:

        datasets = db.scalars(
            select(Dataset)
            .order_by(
                Dataset.id.desc()
            )
        ).all()

    rows = []

    for item in datasets:

        rows.append(
            {
                "ID": item.id,
                "File Name": item.file_name,
                "Source": item.source,
                "Rows": item.row_count,
                "Processed": item.processed_rows,
                "Duplicates": item.duplicate_rows,
                "Failed": item.failed_rows,
                "Status": item.status,
                "Processing": item.processing_status,
                "Uploaded At": item.uploaded_at,
                "Processed At": item.processed_at,
            }
        )

    if rows:

        st.dataframe(
            rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No dataset history available."
        )


# ============================================================
# ISSUES
# ============================================================

with tabs[1]:

    with SessionLocal() as db:

        issues = db.scalars(
            select(Issue)
            .order_by(
                Issue.id.desc()
            )
        ).all()

    rows = []

    for item in issues:

        rows.append(
            {
                "ID": item.id,
                "Issue Key": item.issue_key,
                "Title": item.title,
                "Category": item.category,
                "Severity": item.severity,
                "Priority Score": item.priority_score,
                "Status": item.status,
                "Occurrences": item.occurrence_count,
                "SLA Deadline": item.sla_deadline,
                "Created At": item.created_at,
                "Updated At": item.updated_at,
            }
        )

    if rows:

        st.dataframe(
            rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No issue history available."
        )


# ============================================================
# INTERVENTIONS
# ============================================================

with tabs[2]:

    with SessionLocal() as db:

        interventions = db.scalars(
            select(IssueIntervention)
            .order_by(
                IssueIntervention.id.desc()
            )
        ).all()

    rows = []

    for item in interventions:

        rows.append(
            {
                "ID": item.id,
                "Issue ID": item.issue_id,
                "Type": item.intervention_type,
                "Department": item.assigned_department,
                "Owner": item.owner,
                "Priority": item.priority,
                "Status": item.status,
                "Action Plan": item.action_plan,
                "Due Date": item.due_date,
                "Started": item.started_at,
                "Completed": item.completed_at,
                "Created": item.created_at,
            }
        )

    if rows:

        st.dataframe(
            rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No intervention history available."
        )


# ============================================================
# OUTCOMES
# ============================================================

with tabs[3]:

    with SessionLocal() as db:

        outcomes = db.scalars(
            select(InterventionOutcome)
            .order_by(
                InterventionOutcome.id.desc()
            )
        ).all()

    rows = []

    for item in outcomes:

        rows.append(
            {
                "ID": item.id,
                "Intervention ID": item.intervention_id,
                "Before Count": item.before_count,
                "After Count": item.after_count,
                "Improvement %": (
                    item.improvement_percentage
                ),
                "Remarks": item.remarks,
                "Measured At": item.measured_at,
            }
        )

    if rows:

        st.dataframe(
            rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No outcome history available."
        )