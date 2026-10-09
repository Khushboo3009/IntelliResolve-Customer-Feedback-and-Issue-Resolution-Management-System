import streamlit as st
from sqlalchemy import select

from db.engine import SessionLocal
from db.models import (
    IssueIntervention,
    InterventionOutcome,
)

from styles.theme import apply_theme


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="IntelliResolve - Intervention Outcomes",
    page_icon="📈",
    layout="wide",
)

apply_theme()


st.title("Intervention Outcomes")

st.caption(
    "Measure the real effect of operational interventions."
)


# ============================================================
# LOAD INTERVENTIONS
# ============================================================

with SessionLocal() as db:

    interventions = db.scalars(
        select(IssueIntervention)
        .order_by(
            IssueIntervention.id.desc()
        )
    ).all()


if not interventions:

    st.info(
        "No interventions found."
    )

    st.stop()


# ============================================================
# SELECT
# ============================================================

selected = st.selectbox(
    "Intervention",
    interventions,
    format_func=lambda item: (
        f"#{item.id} — "
        f"{item.intervention_type} — "
        f"{item.owner}"
    ),
)


st.write(
    f"**Department:** "
    f"{selected.assigned_department}"
)

st.write(
    f"**Priority:** {selected.priority}"
)

st.write(
    f"**Status:** {selected.status}"
)

st.write(
    f"**Action Plan:** {selected.action_plan}"
)


st.divider()


# ============================================================
# MEASUREMENT
# ============================================================

st.subheader(
    "Outcome Measurement"
)

before = st.number_input(
    "Complaint Count Before",
    min_value=0,
    value=0,
    step=1,
)


after = st.number_input(
    "Complaint Count After",
    min_value=0,
    value=0,
    step=1,
)


remarks = st.text_area(
    "Remarks",
    placeholder=(
        "Describe the observed outcome "
        "after the intervention."
    ),
)


# ============================================================
# CALCULATE
# ============================================================

if before > 0:

    improvement = (
        (before - after)
        / before
    ) * 100.0

else:

    improvement = 0.0


st.metric(
    "Calculated Improvement",
    f"{improvement:.1f}%",
)


# ============================================================
# SAVE
# ============================================================

if st.button(
    "Measure Outcome",
    type="primary",
    width="stretch",
):

    with SessionLocal() as db:

        intervention = db.get(
            IssueIntervention,
            selected.id,
        )

        if intervention is None:

            st.error(
                "The selected intervention "
                "no longer exists."
            )

            st.stop()

        outcome = InterventionOutcome(
            intervention_id=intervention.id,
            metric_name="Issue Occurrence Count",
            before_count=int(before),
            after_count=int(after),
            improvement_percentage=float(
                improvement
            ),
            remarks=remarks.strip()
            if remarks
            else None,
        )

        db.add(outcome)

        db.commit()

    st.success(
        "Outcome recorded successfully."
    )

    st.rerun()


# ============================================================
# PREVIOUS MEASUREMENTS
# ============================================================

st.divider()

st.subheader(
    "Previous Measurements"
)

with SessionLocal() as db:

    outcomes = db.scalars(
        select(InterventionOutcome)
        .where(
            InterventionOutcome.intervention_id
            == selected.id
        )
        .order_by(
            InterventionOutcome.measured_at.desc()
        )
    ).all()


if outcomes:

    rows = [
        {
            "Measured At": item.measured_at,
            "Before": item.before_count,
            "After": item.after_count,
            "Improvement %": (
                item.improvement_percentage
            ),
            "Remarks": item.remarks or "",
        }
        for item in outcomes
    ]

    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No outcome measurements have been recorded."
    )