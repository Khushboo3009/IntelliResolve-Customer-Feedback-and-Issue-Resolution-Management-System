import streamlit as st
from datetime import date

from sqlalchemy import select

from db.engine import SessionLocal
from db.models import (
    Issue,
    IssueIntervention,
    User,
    Role,
)

from services.intervention_service import (
    create_intervention,
    update_intervention_status,
    get_user_interventions,
)

from styles.theme import apply_theme


# ============================================================
# THEME
# ============================================================

apply_theme()


# ============================================================
# PAGE
# ============================================================

st.title("🛠️ Interventions")

st.caption(
    "Administrator-controlled task assignment "
    "and intervention management."
)


# ============================================================
# SESSION USER
# ============================================================

current_user = st.session_state.get(
    "user"
)

if current_user is None:
    st.error(
        "You must sign in to access Interventions."
    )
    st.stop()


# ============================================================
# CURRENT USER ID
# ============================================================

if isinstance(current_user, dict):

    USER_ID = current_user.get(
        "id"
    )

else:

    USER_ID = getattr(
        current_user,
        "id",
        None,
    )


if USER_ID is None:
    st.error(
        "Unable to determine the logged-in user."
    )
    st.stop()


try:
    USER_ID = int(USER_ID)
except (TypeError, ValueError):
    st.error(
        "Invalid logged-in user."
    )
    st.stop()


# ============================================================
# LOAD CURRENT USER AND ROLE
# ============================================================

with SessionLocal() as db:

    logged_user = db.get(
        User,
        USER_ID,
    )

    if logged_user is None:
        st.error(
            "Logged-in user was not found."
        )
        st.stop()

    role_name = db.scalar(
        select(Role.name)
        .where(
            Role.id
            == logged_user.role_id
        )
    )


# ============================================================
# ADMIN CHECK
# ============================================================

is_admin = (
    str(role_name or "").strip()
    in {
        "Administrator",
        "Admin",
    }
)


# ============================================================
# EMPLOYEE VIEW
# ============================================================

if not is_admin:

    st.info(
        "Task assignment is restricted to "
        "Administrators. You can only view "
        "and update tasks assigned to you."
    )

    st.subheader(
        "📋 My Assigned Tasks"
    )

    try:

        tasks = get_user_interventions(
            USER_ID
        )

    except Exception as exc:

        st.error(
            "Unable to load your assigned tasks."
        )

        st.exception(exc)

        st.stop()

    if not tasks:

        st.success(
            "You currently have no assigned tasks."
        )

    else:

        for task in tasks:

            with st.container(
                border=True
            ):

                # ====================================================
                # TASK HEADER
                # ====================================================

                header_col1, header_col2 = (
                    st.columns([4, 2])
                )

                with header_col1:

                    st.markdown(
                        f"### {task.intervention_type}"
                    )

                    st.write(
                        f"**Task ID:** #{task.id}"
                    )

                with header_col2:

                    st.write(
                        f"**Status:** "
                        f"{(task.status or 'open').title()}"
                    )

                # ====================================================
                # TASK DETAILS
                # ====================================================

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Department:** "
                        f"{task.assigned_department or 'Not specified'}"
                    )

                    st.write(
                        f"**Priority:** "
                        f"{task.priority or 'Medium'}"
                    )

                with col2:

                    if task.due_date:

                        st.write(
                            "**Due Date:** "
                            + task.due_date.strftime(
                                "%d %B %Y"
                            )
                        )

                    else:

                        st.write(
                            "**Due Date:** Not specified"
                        )

                    st.write(
                        f"**Owner:** "
                        f"{task.owner or 'Assigned employee'}"
                    )

                # ====================================================
                # DESCRIPTION
                # ====================================================

                st.markdown(
                    "**Description**"
                )

                st.write(
                    task.description
                    or "No description provided."
                )

                # ====================================================
                # ACTION PLAN
                # ====================================================

                st.markdown(
                    "**Action Plan**"
                )

                st.write(
                    task.action_plan
                    or "No action plan provided."
                )

                # ====================================================
                # STATUS UPDATE
                # ====================================================

                current_status = (
                    task.status or "open"
                )

                status_options = [
                    "open",
                    "in_progress",
                    "completed",
                ]

                if current_status not in status_options:
                    current_status = "open"

                new_status = st.selectbox(
                    "Update Status",
                    status_options,
                    index=status_options.index(
                        current_status
                    ),
                    key=(
                        f"employee_status_"
                        f"{task.id}"
                    ),
                )

                if st.button(
                    "Update Task",
                    key=(
                        f"update_task_"
                        f"{task.id}"
                    ),
                    width="stretch",
                ):

                    try:

                        update_intervention_status(
                            task.id,
                            new_status,
                        )

                        st.success(
                            "Task status updated."
                        )

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            "Unable to update task."
                        )

                        st.exception(exc)

    st.stop()


# ============================================================
# ADMIN VIEW
# ============================================================

st.success(
    "Administrator access confirmed. "
    "You can assign tasks to employees."
)


# ============================================================
# LOAD OPEN ISSUES
# ============================================================

with SessionLocal() as db:

    issues = db.scalars(
        select(Issue)
        .where(
            Issue.status.not_in(
                [
                    "closed",
                    "resolved",
                ]
            )
        )
        .order_by(
            Issue.id.desc()
        )
    ).all()


# ============================================================
# LOAD ACTIVE EMPLOYEES
# ============================================================

with SessionLocal() as db:

    employees = db.scalars(
        select(User)
        .join(
            Role,
            User.role_id
            == Role.id,
        )
        .where(
            User.active.is_(True),
            Role.name.not_in(
                [
                    "Administrator",
                    "Admin",
                ]
            ),
        )
        .order_by(
            User.full_name.asc()
        )
    ).all()


# ============================================================
# ASSIGN TASK
# ============================================================

st.subheader(
    "➕ Assign New Task"
)


if not issues:

    st.warning(
        "No open issues are available for assignment."
    )


elif not employees:

    st.warning(
        "No active employees are available."
    )


else:

    with st.form(
        "administrator_assignment_form"
    ):

        # ====================================================
        # ISSUE
        # ====================================================

        selected_issue = st.selectbox(
            "Select Issue",
            issues,
            format_func=lambda item: (
                f"{item.issue_key or f'ISS-{item.id}'}"
                f" — {item.title}"
            ),
        )

        # ====================================================
        # EMPLOYEE
        # ====================================================

        selected_employee = st.selectbox(
            "Assign To Employee",
            employees,
            format_func=lambda item: (
                f"{item.full_name}"
                f" ({item.email or 'No email'})"
            ),
        )

        # ====================================================
        # DEPARTMENT
        # ====================================================

        department = st.selectbox(
            "Department",
            [
                "Customer Support",
                "Engineering",
                "Finance",
                "Operations",
                "Product",
                "Logistics",
                "Quality",
                "HR",
            ],
        )

        # ====================================================
        # TASK TYPE
        # ====================================================

        intervention_type = st.selectbox(
            "Task Type",
            [
                "Corrective Action",
                "Preventive Action",
                "Investigation",
                "Customer Follow-up",
                "Technical Fix",
                "Process Improvement",
                "Escalation",
                "Other",
            ],
        )

        # ====================================================
        # PRIORITY
        # ====================================================

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High",
                "Critical",
            ],
        )

        # ====================================================
        # DESCRIPTION
        # ====================================================

        description = st.text_area(
            "Task Description",
            placeholder=(
                "Clearly describe what the employee "
                "needs to complete."
            ),
        )

        # ====================================================
        # ACTION PLAN
        # ====================================================

        action_plan = st.text_area(
            "Action Plan",
            placeholder=(
                "Explain the steps that should be "
                "followed to complete the task."
            ),
        )

        # ====================================================
        # DUE DATE
        # ====================================================

        due_date = st.date_input(
            "Due Date",
            value=date.today(),
            min_value=date.today(),
        )

        # ====================================================
        # SUBMIT
        # ====================================================

        assign = st.form_submit_button(
            "📤 Assign Task",
            type="primary",
            width="stretch",
        )


    # ========================================================
    # PROCESS ASSIGNMENT
    # ========================================================

    if assign:

        description = (
            description or ""
        ).strip()

        action_plan = (
            action_plan or ""
        ).strip()

        if not description:

            st.error(
                "Task description is required."
            )

        elif not action_plan:

            st.error(
                "Action plan is required."
            )

        elif selected_issue is None:

            st.error(
                "Please select an issue."
            )

        elif selected_employee is None:

            st.error(
                "Please select an employee."
            )

        else:

            try:

                result = create_intervention(
                    issue_id=selected_issue.id,
                    department=department,
                    owner=selected_employee.full_name,
                    priority=priority,
                    action_plan=action_plan,
                    due_date=due_date,
                    assigned_user_id=selected_employee.id,
                    intervention_type=intervention_type,
                    description=description,
                    assigned_by_user_id=USER_ID,
                )

                # =================================================
                # DUPLICATE ASSIGNMENT
                # =================================================

                if result.get(
                    "duplicate"
                ):

                    st.warning(
                        result.get(
                            "email_message",
                            (
                                "This task is already assigned "
                                "to this employee."
                            ),
                        )
                    )

                # =================================================
                # NEW ASSIGNMENT
                # =================================================

                else:

                    st.success(
                        "Task assigned successfully."
                    )

                    if result.get(
                        "email_sent"
                    ):

                        st.success(
                            result.get(
                                "email_message",
                                "Assignment email sent.",
                            )
                        )

                    else:

                        st.warning(
                            result.get(
                                "email_message",
                                (
                                    "Task was assigned, "
                                    "but no email was sent."
                                ),
                            )
                        )

                # IMPORTANT:
                # Do not immediately rerun here.
                #
                # Keeping the current page state allows the
                # success/duplicate message to remain visible.
                #
                # The next normal Streamlit interaction will
                # refresh the page naturally.

            except PermissionError as exc:

                st.error(
                    str(exc)
                )

            except ValueError as exc:

                st.error(
                    str(exc)
                )

            except Exception as exc:

                st.error(
                    "Unable to assign the task."
                )

                st.exception(exc)


# ============================================================
# ADMIN: RECENT ASSIGNMENTS
# ============================================================

st.divider()

st.subheader(
    "📋 Recent Task Assignments"
)


try:

    with SessionLocal() as db:

        assignments = db.scalars(
            select(IssueIntervention)
            .order_by(
                IssueIntervention.id.desc()
            )
            .limit(50)
        ).all()

except Exception as exc:

    st.error(
        "Unable to load recent task assignments."
    )

    st.exception(exc)

    assignments = []


# ============================================================
# DISPLAY ASSIGNMENTS
# ============================================================

if not assignments:

    st.info(
        "No task assignments have been created yet."
    )

else:

    for task in assignments:

        with st.container(
            border=True
        ):

            col1, col2, col3 = (
                st.columns([4, 2, 2])
            )

            # =================================================
            # TASK INFORMATION
            # =================================================

            with col1:

                st.markdown(
                    f"**#{task.id} — "
                    f"{task.intervention_type or 'Intervention'}**"
                )

                st.write(
                    f"Employee: "
                    f"{task.owner or 'Unassigned'}"
                )

                st.write(
                    f"Department: "
                    f"{task.assigned_department or 'Not specified'}"
                )

            # =================================================
            # PRIORITY / STATUS
            # =================================================

            with col2:

                st.write(
                    f"Priority: "
                    f"{task.priority or 'Medium'}"
                )

                st.write(
                    f"Status: "
                    f"{(task.status or 'open').title()}"
                )

            # =================================================
            # DUE DATE
            # =================================================

            with col3:

                if task.due_date:

                    st.write(
                        "Due: "
                        + task.due_date.strftime(
                            "%d %b %Y"
                        )
                    )

                else:

                    st.write(
                        "Due: Not specified"
                    )

            # =================================================
            # DESCRIPTION
            # =================================================

            if task.description:

                st.caption(
                    task.description
                )

            # =================================================
            # ACTION PLAN
            # =================================================

            if task.action_plan:

                with st.expander(
                    "View Action Plan"
                ):

                    st.write(
                        task.action_plan
                    )