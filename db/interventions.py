"""
Compatibility module.

IssueIntervention is defined centrally in db.models.
This module re-exports it so older imports continue to work
without creating a second SQLAlchemy model for the same table.
"""

from db.models import IssueIntervention

__all__ = [
    "IssueIntervention",
]