import streamlit as st

from sqlalchemy import select, func

from styles.theme import apply_theme

from db.engine import SessionLocal

from db.models import (
    Issue,
    Department,
    User,
)

from services.lifecycle_service import (
    transition_issue,
    assign_department,
    assign_user,
    assign_sla,
    get_sla_status,
    ALLOWED_TRANSITIONS,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="IntelliResolve - Operations Control",
    page_icon="⚙️",
    layout="wide",
)

apply_theme()


from ui.header import app_header

app_header("⚙️ Operations Control")

st.caption(
    "Real operational issue lifecycle, ownership and SLA management"
)


# ============================================================
# METRICS
# ============================================================

with SessionLocal() as db:

    total = db.scalar(
        select(func.count(Issue.id))
    ) or 0

    open_count = db.scalar(
        select(func.count(Issue.id))
        .where(
            Issue.status != "closed"
        )
    ) or 0

    assigned_count = db.scalar(
        select(func.count(Issue.id))
        .where(
            Issue.assigned_user_id.is_not(None)
        )
    ) or 0

    breached = 0

    issues_for_sla = db.scalars(
        select(Issue)
        .where(
            Issue.status != "closed"
        )
    ).all()

    for issue in issues_for_sla:

        if (
            get_sla_status(issue)
            == "Breached"
        ):

            breached += 1


c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Issues",
        total,
    )

with c2:
    st.metric(
        "Active Issues",
        open_count,
    )

with c3:
    st.metric(
        "Assigned",
        assigned_count,
    )

with c4:
    st.metric(
        "SLA Breached",
        breached,
    )


st.divider()


# ============================================================
# LOAD ISSUES
# ============================================================

with SessionLocal() as db:

    issues = db.scalars(
        select(Issue)
        .order_by(
            Issue.priority_score.desc(),
            Issue.updated_at.desc(),
        )
        .limit(500)
    ).all()

    departments = db.scalars(
        select(Department)
        .order_by(
            Department.name
        )
    ).all()

    users = db.scalars(
        select(User)
        .where(
            User.active == True
        )
        .order_by(
            User.full_name
        )
    ).all()


# ============================================================
# ISSUE SELECTOR
# ============================================================

if not issues:

    st.info(
        "No real operational issues are currently "
        "available in MySQL."
    )

    st.stop()


issue_options = {
    f"{issue.issue_key} — {issue.title}":
        issue.id
    for issue in issues
}


selected_label = st.selectbox(
    "Select an issue",
    list(issue_options.keys()),
)

selected_issue_id = (
    issue_options[selected_label]
)


selected_issue = next(
    issue
    for issue in issues
    if issue.id == selected_issue_id
)


# ============================================================
# ISSUE INFORMATION
# ============================================================

st.subheader(
    "Issue Information"
)

c1, c2, c3 = st.columns(3)

with c1:

    st.write(
        f"**Issue:** "
        f"{selected_issue.issue_key}"
    )

    st.write(
        f"**Category:** "
        f"{selected_issue.category}"
    )

with c2:

    st.write(
        f"**Severity:** "
        f"{selected_issue.severity}"
    )

    st.write(
        f"**Priority Score:** "
        f"{selected_issue.priority_score}"
    )

with c3:

    st.write(
        f"**Status:** "
        f"{selected_issue.status}"
    )

    st.write(
        f"**Occurrences:** "
        f"{selected_issue.occurrence_count}"
    )


st.divider()


# ============================================================
# SLA
# ============================================================

st.subheader(
    "SLA Monitoring"
)

sla_status = get_sla_status(
    selected_issue
)

st.write(
    f"**Current SLA Status:** "
    f"{sla_status}"
)

if selected_issue.sla_deadline:

    st.write(
        f"**Deadline:** "
        f"{selected_issue.sla_deadline}"
    )

else:

    if st.button(
        "Assign SLA",
        key="assign_sla",
    ):

        try:

            assign_sla(
                selected_issue.id
            )

            st.success(
                "SLA assigned successfully."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                str(exc)
            )


# ============================================================
# DEPARTMENT ASSIGNMENT
# ============================================================

st.divider()

st.subheader(
    "Department Assignment"
)

department_map = {
    department.name:
        department.id
    for department in departments
}


current_department = "Unassigned"

if selected_issue.department_id:

    for department in departments:

        if (
            department.id
            == selected_issue.department_id
        ):

            current_department = (
                department.name
            )

            break


selected_department = st.selectbox(
    "Department",
    ["Unassigned"]
    + list(department_map.keys()),
    index=(
        0
        if current_department
        == "Unassigned"
        else (
            list(department_map.keys())
            .index(current_department)
            + 1
        )
    ),
)


if st.button(
    "Assign Department",
):

    if selected_department == "Unassigned":

        st.warning(
            "Select a department."
        )

    else:

        try:

            assign_department(
                selected_issue.id,
                department_map[
                    selected_department
                ],
            )

            st.success(
                f"Issue assigned to "
                f"{selected_department}."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                str(exc)
            )


# ============================================================
# USER ASSIGNMENT
# ============================================================

st.subheader(
    "Responsible User"
)

user_map = {
    f"{user.full_name} ({user.email})":
        user.id
    for user in users
}


selected_user = st.selectbox(
    "Assign to",
    list(user_map.keys())
    if user_map
    else ["No active users"],
)


if st.button(
    "Assign Responsible User",
):

    if not user_map:

        st.warning(
            "No active users are available."
        )

    else:

        try:

            assign_user(
                selected_issue.id,
                user_map[
                    selected_user
                ],
            )

            st.success(
                "Responsible user assigned."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                str(exc)
            )


# ============================================================
# LIFECYCLE
# ============================================================

st.divider()

st.subheader(
    "Issue Lifecycle"
)

current_status = (
    selected_issue.status
    or "open"
)

allowed_next = (
    ALLOWED_TRANSITIONS.get(
        current_status,
        [],
    )
)


st.write(
    f"Current status: **{current_status}**"
)

if allowed_next:

    new_status = st.selectbox(
        "Move issue to",
        allowed_next,
    )

    resolution_notes = ""

    if new_status == "resolved":

        resolution_notes = st.text_area(
            "Resolution Notes",
            placeholder=(
                "Enter the actual resolution "
                "performed by the responsible team."
            ),
        )

    if st.button(
        "Update Issue Status",
        use_container_width=True,
    ):

        try:

            transition_issue(
                selected_issue.id,
                new_status,
                resolution_notes
                if resolution_notes
                else None,
            )

            st.success(
                f"Issue moved from "
                f"{current_status} "
                f"to {new_status}."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                str(exc)
            )

else:

    st.info(
        "This issue has reached the end of its "
        "current lifecycle."
    )