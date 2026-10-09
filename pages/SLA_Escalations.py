import streamlit as st

from services.sla_service import get_sla_records

from styles.theme import apply_theme

apply_theme()

st.title("SLA & Escalations")

records = get_sla_records()

if not records:
    st.info("No SLA records.")
    st.stop()

for r in records:

    with st.container(border=True):

        c1,c2,c3 = st.columns([2,1,1])

        c1.markdown(f"### {r['department']}")
        c2.metric("Priority", r["priority"])
        c3.metric("SLA", r["sla"])

        st.write(f"Owner: {r['owner']}")
        st.caption(f"Due: {r['due_date']}")