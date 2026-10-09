from datetime import date, datetime, time
import os
import smtplib
from email.message import EmailMessage

from sqlalchemy import select

from db.engine import SessionLocal
from db.models import (
    Issue,
    IssueIntervention,
    User,
    Role,
)


# ============================================================
# CONSTANTS
# ============================================================

ADMIN_ROLE_NAMES = {
    "Administrator",
    "Admin",
}

ACTIVE_TASK_STATUSES = {
    "open",
    "in_progress",
}


# ============================================================
# HELPERS
# ============================================================

def _to_datetime(value):
    """
    Convert Streamlit date_input values into datetime values.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    return value


def _is_admin(user):
    """
    Check whether a User ORM object or dictionary represents
    an administrator.
    """

    if user is None:
        return False

    if isinstance(user, dict):
        role = user.get("role")

        if isinstance(role, dict):
            role = role.get("name")

        return str(role or "").strip() in ADMIN_ROLE_NAMES

    role = getattr(user, "role", None)

    if role is not None:
        role_name = getattr(role, "name", None)

        if role_name:
            return (
                str(role_name).strip()
                in ADMIN_ROLE_NAMES
            )

    return False


def _clean_text(value):
    """
    Safely convert a value to stripped text.
    """

    return str(value or "").strip()


# ============================================================
# EMAIL
# ============================================================

def _send_assignment_email(
    employee,
    issue,
    intervention,
):
    """
    Send one assignment email to the selected employee.

    The database assignment is already committed before this
    function is called. Therefore, an SMTP failure does not
    remove the database assignment.
    """

    smtp_host = os.getenv(
        "SMTP_HOST",
        "",
    ).strip()

    try:
        smtp_port = int(
            os.getenv(
                "SMTP_PORT",
                "587",
            )
        )
    except (TypeError, ValueError):
        smtp_port = 587

    smtp_username = os.getenv(
        "SMTP_USERNAME",
        "",
    ).strip()

    smtp_password = os.getenv(
        "SMTP_PASSWORD",
        "",
    )

    # Support both variable names so the service works with
    # existing project configurations.
    smtp_sender = (
        os.getenv("SMTP_FROM", "").strip()
        or os.getenv("SMTP_FROM_EMAIL", "").strip()
        or smtp_username
    )

    if not smtp_host:
        return (
            False,
            (
                "Task assigned successfully, but email delivery "
                "is not configured. Set SMTP_HOST."
            ),
        )

    if not smtp_sender:
        return (
            False,
            (
                "Task assigned successfully, but the sender email "
                "is not configured. Set SMTP_FROM or SMTP_FROM_EMAIL."
            ),
        )

    employee_email = _clean_text(
        getattr(employee, "email", None)
    )

    if not employee_email:
        return (
            False,
            (
                "Task assigned successfully, but the selected "
                "employee has no email address."
            ),
        )

    issue_key = (
        getattr(issue, "issue_key", None)
        or f"ISS-{issue.id}"
    )

    due_date = getattr(
        intervention,
        "due_date",
        None,
    )

    due_text = (
        due_date.strftime("%d %B %Y")
        if due_date
        else "Not specified"
    )

    employee_name = (
        getattr(employee, "full_name", None)
        or "Employee"
    )

    message = EmailMessage()

    message["Subject"] = (
        f"New IntelliResolve Task Assigned - {issue_key}"
    )

    message["From"] = smtp_sender
    message["To"] = employee_email

    message.set_content(
        f"""
Hello {employee_name},

A new task has been assigned to you in IntelliResolve.

Issue:
{issue_key}

Issue Title:
{getattr(issue, "title", "Not specified")}

Task Type:
{getattr(intervention, "intervention_type", "Not specified")}

Priority:
{getattr(intervention, "priority", "Not specified")}

Department:
{getattr(intervention, "assigned_department", "Not specified")}

Task Description:
{getattr(intervention, "description", "")}

Action Plan:
{getattr(intervention, "action_plan", "")}

Due Date:
{due_text}

Status:
{getattr(intervention, "status", "open")}

Please log in to IntelliResolve to review and complete the task.

Regards,
IntelliResolve
Operations Team
""".strip()
    )

    try:

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=20,
        ) as server:

            server.ehlo()

            # Gmail and most SMTP providers use STARTTLS
            # on port 587.
            if smtp_port != 25:
                server.starttls()
                server.ehlo()

            if smtp_username and smtp_password:
                server.login(
                    smtp_username,
                    smtp_password,
                )

            server.send_message(message)

        return (
            True,
            f"Assignment email sent to {employee_email}.",
        )

    except Exception as exc:

        return (
            False,
            (
                "Task was assigned successfully, but the "
                f"assignment email could not be sent: {exc}"
            ),
        )


# ============================================================
# FIND EXISTING ACTIVE ASSIGNMENT
# ============================================================

def _find_existing_active_assignment(
    db,
    issue_id,
    employee_id,
):
    """
    Find the most recent active task assigned to the same
    employee for the same issue.

    This prevents accidental duplicate assignments and,
    therefore, prevents duplicate assignment emails.
    """

    if employee_id is None:
        return None

    return db.scalar(
        select(IssueIntervention)
        .where(
            IssueIntervention.issue_id
            == int(issue_id),

            IssueIntervention.assigned_user_id
            == int(employee_id),

            IssueIntervention.status.in_(
                ACTIVE_TASK_STATUSES
            ),
        )
        .order_by(
            IssueIntervention.id.desc()
        )
    )


# ============================================================
# CREATE INTERVENTION
# ============================================================

def create_intervention(
    issue_id,
    department,
    owner="",
    priority="Medium",
    action_plan="",
    due_date=None,
    assigned_user_id=None,
    intervention_type="Corrective Action",
    description=None,
    assigned_by_user_id=None,
    assigned_by=None,
):
    """
    Create a new intervention/task.

    Only Administrators can create assignments.

    Important duplicate protection:
    If the same issue is already assigned to the same employee
    and the existing task is still open/in progress, no new
    intervention is created and no additional email is sent.
    """

    # --------------------------------------------------------
    # BACKWARD-COMPATIBLE ASSIGNMENT ALIAS
    # --------------------------------------------------------

    if assigned_by_user_id is None:
        assigned_by_user_id = assigned_by

    # --------------------------------------------------------
    # DATABASE SESSION
    # --------------------------------------------------------

    with SessionLocal() as db:

        # ====================================================
        # ADMIN AUTHORIZATION
        # ====================================================

        if assigned_by_user_id is None:
            raise PermissionError(
                "Only Administrators can assign tasks."
            )

        try:
            assigning_user_id = int(
                assigned_by_user_id
            )
        except (TypeError, ValueError):
            raise PermissionError(
                "Invalid administrator user ID."
            )

        assigning_user = db.get(
            User,
            assigning_user_id,
        )

        if assigning_user is None:
            raise PermissionError(
                "The assigning user could not be found."
            )

        # Explicit database role check.
        role_name = db.scalar(
            select(Role.name)
            .where(
                Role.id
                == assigning_user.role_id
            )
        )

        if (
            str(role_name or "").strip()
            not in ADMIN_ROLE_NAMES
        ):
            raise PermissionError(
                "Only Administrators can assign tasks."
            )

        # ====================================================
        # VALIDATE ISSUE
        # ====================================================

        try:
            selected_issue_id = int(issue_id)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid issue selected."
            )

        issue = db.get(
            Issue,
            selected_issue_id,
        )

        if issue is None:
            raise ValueError(
                "The selected issue does not exist."
            )

        # ====================================================
        # VALIDATE EMPLOYEE
        # ====================================================

        employee = None

        if assigned_user_id is not None:

            try:
                selected_employee_id = int(
                    assigned_user_id
                )
            except (TypeError, ValueError):
                raise ValueError(
                    "Invalid employee selected."
                )

            employee = db.get(
                User,
                selected_employee_id,
            )

            if employee is None:
                raise ValueError(
                    "The selected employee does not exist."
                )

            if not employee.active:
                raise ValueError(
                    "The selected employee is inactive."
                )

            # =================================================
            # DUPLICATE ASSIGNMENT PROTECTION
            # =================================================
            #
            # This is the important fix for repeated emails.
            #
            # If this issue is already assigned to this employee
            # and the existing task is still open/in progress,
            # return the existing task instead of creating another
            # intervention and sending another email.
            # =================================================

            existing_intervention = (
                _find_existing_active_assignment(
                    db=db,
                    issue_id=issue.id,
                    employee_id=employee.id,
                )
            )

            if existing_intervention is not None:

                return {
                    "success": True,
                    "duplicate": True,
                    "intervention": (
                        existing_intervention
                    ),
                    "email_sent": False,
                    "email_message": (
                        f"This issue is already assigned "
                        f"to {employee.full_name}. "
                        "No duplicate task was created "
                        "and no additional email was sent."
                    ),
                }

        # ====================================================
        # NORMALIZE VALUES
        # ====================================================

        department = _clean_text(
            department
        )

        if not department:
            raise ValueError(
                "A department must be selected."
            )

        priority = _clean_text(
            priority
        ) or "Medium"

        intervention_type = (
            _clean_text(
                intervention_type
            )
            or "Corrective Action"
        )

        action_plan = _clean_text(
            action_plan
        )

        if description is None:
            description = action_plan

        description = _clean_text(
            description
        )

        owner = _clean_text(
            owner
        )

        if not owner and employee is not None:
            owner = _clean_text(
                employee.full_name
            )

        # The legacy database requires description to be
        # populated, so never insert NULL/empty description.
        if not description:
            description = (
                "Operational task assigned "
                f"for issue {issue.title}."
            )

        # ====================================================
        # CREATE INTERVENTION
        # ====================================================

        now = datetime.utcnow()

        intervention = IssueIntervention(
            issue_id=issue.id,

            assigned_department=department,

            assigned_user_id=(
                employee.id
                if employee is not None
                else None
            ),

            owner=owner,

            intervention_type=intervention_type,

            description=description,

            priority=priority,

            action_plan=action_plan,

            status="open",

            due_date=_to_datetime(
                due_date
            ),

            started_at=None,

            completed_at=None,

            created_at=now,

            updated_at=now,
        )

        db.add(intervention)

        # Generate ID and validate the INSERT before commit.
        db.flush()

        # ====================================================
        # UPDATE ISSUE
        # ====================================================

        if employee is not None:
            issue.assigned_user_id = (
                employee.id
            )

        issue.updated_at = datetime.utcnow()

        # ====================================================
        # COMMIT ASSIGNMENT
        # ====================================================

        db.commit()

        db.refresh(intervention)

        # ====================================================
        # SEND ASSIGNMENT EMAIL
        # ====================================================

        email_sent = False

        email_message = (
            "No employee email was sent."
        )

        if employee is not None:

            email_sent, email_message = (
                _send_assignment_email(
                    employee=employee,
                    issue=issue,
                    intervention=intervention,
                )
            )

        # ====================================================
        # RETURN RESULT
        # ====================================================

        return {
            "success": True,
            "duplicate": False,
            "intervention": intervention,
            "email_sent": email_sent,
            "email_message": email_message,
        }


# ============================================================
# UPDATE INTERVENTION STATUS
# ============================================================

def update_intervention_status(
    intervention_id,
    status,
):
    """
    Update the status of an intervention.
    """

    allowed_statuses = {
        "open",
        "in_progress",
        "completed",
        "cancelled",
    }

    status = (
        str(status or "")
        .strip()
        .lower()
    )

    if status not in allowed_statuses:
        raise ValueError(
            "Invalid intervention status."
        )

    try:
        intervention_id = int(
            intervention_id
        )
    except (TypeError, ValueError):
        raise ValueError(
            "Invalid intervention ID."
        )

    with SessionLocal() as db:

        intervention = db.get(
            IssueIntervention,
            intervention_id,
        )

        if intervention is None:
            raise ValueError(
                "Intervention not found."
            )

        now = datetime.utcnow()

        intervention.status = status
        intervention.updated_at = now

        if status == "in_progress":

            if intervention.started_at is None:
                intervention.started_at = now

        elif status == "completed":

            if intervention.started_at is None:
                intervention.started_at = now

            intervention.completed_at = now

        elif status == "cancelled":

            intervention.completed_at = None

        elif status == "open":

            # If reopened, keep the historical start time,
            # but remove the completion timestamp.
            intervention.completed_at = None

        db.commit()

        return True


# ============================================================
# GET ALL INTERVENTIONS
# ============================================================

def get_interventions():
    """
    Return all interventions, newest first.
    """

    with SessionLocal() as db:

        return db.scalars(
            select(IssueIntervention)
            .order_by(
                IssueIntervention.id.desc()
            )
        ).all()


# ============================================================
# GET INTERVENTIONS FOR ISSUE
# ============================================================

def get_issue_interventions(
    issue_id,
):
    """
    Return all interventions for an issue.
    """

    with SessionLocal() as db:

        return db.scalars(
            select(IssueIntervention)
            .where(
                IssueIntervention.issue_id
                == int(issue_id)
            )
            .order_by(
                IssueIntervention.id.desc()
            )
        ).all()


# ============================================================
# GET TASKS ASSIGNED TO EMPLOYEE
# ============================================================

def get_user_interventions(
    user_id,
):
    """
    Return all tasks assigned to a specific employee.
    """

    with SessionLocal() as db:

        return db.scalars(
            select(IssueIntervention)
            .where(
                IssueIntervention.assigned_user_id
                == int(user_id)
            )
            .order_by(
                IssueIntervention.id.desc()
            )
        ).all()