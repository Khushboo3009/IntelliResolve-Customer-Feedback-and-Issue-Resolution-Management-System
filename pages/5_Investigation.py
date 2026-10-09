import streamlit as st

from services.investigation_service import (
    get_open_issues,
    create_investigation,
    update_investigation,
)

from styles.theme import apply_theme

apply_theme()

st.title("Root Cause Investigation")

issues = get_open_issues()

if not issues:

    st.info("No open issues available.")

    st.stop()

selected = st.selectbox(
    "Select Issue",
    issues,
    format_func=lambda x: f"#{x.id} - {x.title}",
)

if st.button("Create Investigation"):

    inv = create_investigation(
        selected.id,
        st.session_state.user["id"],
    )

    st.success(f"Investigation #{inv.id} created.")

st.divider()

st.subheader("Investigation Report")

root = st.text_area("Root Cause")

evidence = st.text_area("Evidence")

findings = st.text_area("Findings")

if st.button("Complete Investigation", type="primary"):

    inv = create_investigation(
        selected.id,
        st.session_state.user["id"],
    )

    update_investigation(
        inv.id,
        root,
        evidence,
        findings,
    )

    st.success("Investigation completed.")