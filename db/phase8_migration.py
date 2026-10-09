from sqlalchemy import text

from db.engine import engine


def migrate():

    print("=" * 65)
    print("IntelliResolve - Phase 8 Migration")
    print("=" * 65)

    statements = [

        """
        CREATE TABLE IF NOT EXISTS issue_predictions (

            id INT AUTO_INCREMENT PRIMARY KEY,

            issue_id INT NOT NULL,

            risk_score FLOAT NOT NULL DEFAULT 0,

            risk_level VARCHAR(30) NOT NULL,

            occurrence_score FLOAT DEFAULT 0,

            growth_score FLOAT DEFAULT 0,

            severity_score FLOAT DEFAULT 0,

            sla_score FLOAT DEFAULT 0,

            recurrence_score FLOAT DEFAULT 0,

            business_impact_score FLOAT DEFAULT 0,

            trend_direction VARCHAR(30),

            predicted_status VARCHAR(50),

            recommendation TEXT,

            calculated_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_prediction_issue(issue_id),

            INDEX idx_prediction_risk(risk_score),

            INDEX idx_prediction_level(risk_level),

            FOREIGN KEY(issue_id)
                REFERENCES issues(id)
                ON DELETE CASCADE
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS issue_trends (

            id INT AUTO_INCREMENT PRIMARY KEY,

            issue_id INT NOT NULL,

            observation_date DATE NOT NULL,

            occurrence_count INT DEFAULT 0,

            growth_percentage FLOAT DEFAULT 0,

            trend_direction VARCHAR(30),

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_trend_issue(issue_id),

            INDEX idx_trend_date(observation_date),

            FOREIGN KEY(issue_id)
                REFERENCES issues(id)
                ON DELETE CASCADE
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS preventive_actions (

            id INT AUTO_INCREMENT PRIMARY KEY,

            issue_id INT NOT NULL,

            action_title VARCHAR(255) NOT NULL,

            action_description TEXT,

            priority VARCHAR(30),

            reason TEXT,

            status VARCHAR(50)
                DEFAULT 'recommended',

            created_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            completed_at DATETIME NULL,

            INDEX idx_action_issue(issue_id),

            INDEX idx_action_status(status),

            FOREIGN KEY(issue_id)
                REFERENCES issues(id)
                ON DELETE CASCADE
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS customer_risk_scores (

            id INT AUTO_INCREMENT PRIMARY KEY,

            customer_id VARCHAR(255) NOT NULL,

            feedback_count INT DEFAULT 0,

            unresolved_count INT DEFAULT 0,

            critical_count INT DEFAULT 0,

            repeated_issue_count INT DEFAULT 0,

            risk_score FLOAT DEFAULT 0,

            risk_level VARCHAR(30),

            calculated_at DATETIME
                DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_customer_risk(customer_id),

            INDEX idx_customer_score(risk_score)
        )
        """
    ]

    with engine.begin() as connection:

        for statement in statements:

            connection.execute(
                text(statement)
            )

    print()
    print("[READY] issue_predictions")
    print("[READY] issue_trends")
    print("[READY] preventive_actions")
    print("[READY] customer_risk_scores")

    print()
    print("Phase 8 migration completed successfully.")


if __name__ == "__main__":
    migrate()