"""Chat with the churn database. Run:  streamlit run app.py"""
import streamlit as st
from churn_llm import ask_database

st.set_page_config(page_title="Bank Churn Assistant", page_icon="🏦")
st.title("🏦 Bank Churn Assistant")
st.caption("Ask questions about the customer database in plain English.")

examples = ["What is the overall churn rate?",
            "Churn rate by country",
            "Churn rate by number of products",
            "Average age of customers who churned vs stayed",
            "Top 10 customers with highest balance who churned"]
with st.sidebar:
    st.subheader("Try these")
    for e in examples:
        if st.button(e, use_container_width=True):
            st.session_state["q"] = e

q = st.chat_input("Ask about churn...") or st.session_state.pop("q", None)
if q:
    st.chat_message("user").write(q)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                sql, df, answer = ask_database(q)
            st.write(answer)
            st.dataframe(df, use_container_width=True)
            with st.expander("SQL used"):
                st.code(sql, language="sql")
        except Exception as ex:
            st.error(f"Could not answer: {ex}")
