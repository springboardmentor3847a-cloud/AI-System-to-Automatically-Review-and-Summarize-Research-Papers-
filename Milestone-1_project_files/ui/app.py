# Minimal Streamlit skeleton for later expansion
import streamlit as st

st.set_page_config(page_title="AI Paper Reviewer", layout="wide")
st.title("AI System to Review and Summarize Research Papers")

st.sidebar.header("Pipeline")
st.sidebar.write("1. Search papers")
st.sidebar.write("2. Download PDFs")
st.sidebar.write("3. Extract text")
st.sidebar.write("4. Analyze text")
st.sidebar.write("5. Generate review draft")
st.sidebar.write("6. Critique draft")

st.info("This is a placeholder UI. Modules will be wired up later.")
