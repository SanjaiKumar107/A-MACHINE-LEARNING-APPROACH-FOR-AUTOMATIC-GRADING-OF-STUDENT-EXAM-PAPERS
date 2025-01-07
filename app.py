import streamlit as st
import os

def main():
    st.title("Automatic Handwritten Answer Script Evaluation System")
    st.write("Welcome to the Automatic Handwritten Answer Script Evaluation System. Please login or signup to continue.")
    page = st.radio(
        "Login or Signup as:",
        ("Evaluator", "Student"),        key="login_signup",
    )
    if st.button("Login"):
        if page == "Evaluator":
            os.system('streamlit run evaluator.py')
        else:
            os.system('streamlit run student.py')

if __name__ == "__main__":
    main()
