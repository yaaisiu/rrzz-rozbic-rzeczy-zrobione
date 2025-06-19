import streamlit as st

st.title("rrzz-rozbic-rzeczy-zrobione")

note = st.text_area("Enter your note:")
if st.button("Submit"):
    st.write("Note submitted (stub)") 