from sqlalchemy import text

from db.engine import engine


TABLES = {

    "issue_investigations": """
        CREATE TABLE IF NOT EXISTS issue_investigations (

            id INT AUTO_INCREMENT PRIMARY KEY,

            issue_id INT NOT NULL,

            investigation_type VARCHAR(100)
                NOT NULL DEFAULT 'root_cause',

            root_cause TEXT NULL,

            evidence TEXT NULL,

            contributing_factors TEXT NULL,

            confidence_score INT NULL,

            investigator_id INT NULL,

            status VARCHAR(50)
                NOT NULL DEFAULT 'open',

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            updated_at DATETIME
                DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

            INDEX idx_investigation_issue(issue_id),

            FOREIGN KEY(issue_id)
                REFERENCES issues(id),

            FOREIGN KEY(investigator_id)
                REFERENCES users(id)
        )
    """,

    "interventions": """
        CREATE TABLE IF NOT EXISTS interventions (

            id INT AUTO_INCREMENT PRIMARY KEY,

            issue_id INT NOT NULL,

            investigation_id INT NULL,

            intervention_type VARCHAR(100)
                NOT NULL,

            action_title VARCHAR(255)
                NOT NULL,

            action_description TEXT NULL,

            assigned_user_id INT NULL,

            department_id INT NULL,

            status VARCHAR(50)
                NOT NULL DEFAULT 'planned',

            started_at DATETIME NULL,

            completed_at DATETIME NULL,

            expected_outcome TEXT NULL,

            actual_outcome TEXT NULL,

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            updated_at DATETIME
                DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

            INDEX idx_intervention_issue(issue_id),

            FOREIGN KEY(issue_id)
                REFERENCES issues(id),

            FOREIGN KEY(investigation_id)
                REFERENCES issue_investigations(id),

            FOREIGN KEY(assigned_user_id)
                REFERENCES users(id),

            FOREIGN KEY(department_id)
                REFERENCES departments(id)
        )
    """,

    "intervention_outcomes": """
        CREATE TABLE IF NOT EXISTS intervention_outcomes (

            id INT AUTO_INCREMENT PRIMARY KEY,

            intervention_id INT NOT NULL,

            metric_name VARCHAR(150)
                NOT NULL,

            baseline_value VARCHAR(100) NULL,

            current_value VARCHAR(100) NULL,

            target_value VARCHAR(100) NULL,

            measurement_unit VARCHAR(50) NULL,

            outcome_status VARCHAR(50) NULL,

            measured_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            notes TEXT NULL,

            INDEX idx_outcome_intervention(
                intervention_id
            ),

            FOREIGN KEY(intervention_id)
                REFERENCES interventions(id)
        )
    """,
}


def migrate():

    print("=" * 60)
    print("IntelliResolve - Phase 6 Migration")
    print("=" * 60)

    with engine.begin() as connection:

        for name, sql in TABLES.items():

            connection.execute(
                text(sql)
            )

            print(
                f"[READY] {name}"
            )

    print()
    print(
        "Phase 6 database migration completed."
    )


if __name__ == "__main__":
    migrate()