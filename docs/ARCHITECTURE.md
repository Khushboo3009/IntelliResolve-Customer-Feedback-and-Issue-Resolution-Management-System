# IntelliResolve Phase 1 Architecture

```text
Browser
   |
   v
Streamlit UI
   |
   +---- Authentication Service
   |
   +---- Operations Center
   |
   +---- Administration
   |
   v
Service Layer
   |
   v
SQLAlchemy
   |
   v
MySQL
```

Future architecture:

```text
Data Sources
    |
    v
Ingestion Layer
    |
    v
Incremental Processing
    |
    v
Background Queue
    |
    v
NLP / ML Workers
    |
    v
MySQL
    |
    +--> Issue Management
    +--> SLA
    +--> Interventions
    +--> Outcomes
    +--> Alerts
    |
    v
Operations Center
```

The Phase 1 implementation deliberately stops before these future capabilities and does not simulate them.
