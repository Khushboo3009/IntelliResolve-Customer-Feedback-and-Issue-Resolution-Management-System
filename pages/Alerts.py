import streamlit as st

from services.alert_service import generate_alerts

from styles.theme import apply_theme

apply_theme()

st.title("Live Operational Alerts")

alerts = generate_alerts()

if not alerts:

    st.success("No active alerts.")
    st.stop()

for alert in alerts:

    if alert["level"] == "Critical":
        st.error(f"🚨 {alert['title']}")
    else:
        st.warning(f"⚠ {alert['title']}")

    st.write(alert["message"])
    st.divider()