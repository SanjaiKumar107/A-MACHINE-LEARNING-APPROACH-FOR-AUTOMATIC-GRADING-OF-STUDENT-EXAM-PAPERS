import json
import os
import streamlit as st
from streamlit import session_state
import streamlit as st

session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0


def signup(json_file_path="evaluator.json"):
    st.title("Evaluator Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")

        if st.form_submit_button("Signup"):
            if password == confirm_password:
                user = create_account(name, email, age, sex, password, json_file_path)
                session_state["logged_in"] = True
                session_state["user_info"] = user
            else:
                st.error("Passwords do not match. Please try again.")


def check_login(username, password, json_file_path="evaluator.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["users"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                return user
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(
    json_file_path="evaluator.json", question_paper="question_paper.json", student = "students.json"
):
    try:
        if not os.path.exists(json_file_path):
            data = {"users": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
        if not os.path.exists(question_paper):
            data = {"subjects": []}
            with open(question_paper, "w") as json_file:
                json.dump(data, json_file)
        if not os.path.exists(student):
            data = {"students": []}
            with open(student, "w") as json_file:
                json.dump(data, json_file)
        
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(name, email, age, sex, password, json_file_path="evaluator.json"):
    try:
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"users": []}
        else:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

        # Append new user data to the JSON structure
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
        }

        data["users"].append(user_info)

        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        st.success("Account created successfully! You can now login.")
        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="evaluator.json", question_paper="question_paper.json"):
    st.title("Login Page")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password, json_file_path)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def get_user_info(email, json_file_path="evaluator.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["users"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None


def render_dashboard(user_info, json_file_path="evaluator.json"):
    try:
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("Evaluator Information")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def main(json_file_path="evaluator.json", question_paper="question_paper.json"):
    st.title("Evaluator Dashboard")
    page = st.sidebar.radio(
        "Go to",
        (
            "Signup/Login",
            "Dashboard",
            "Set Question Paper",
            "View Question Papers",
            "View Student Responses",
        ),
        key="page",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"])
        else:
            st.warning("Please login/signup to view the dashboard.")

    elif page == "Set Question Paper":
        if session_state.get("logged_in"):

            st.title("Set Question Paper")
            user_info = session_state["user_info"]
            Subject_name = st.text_input("Subject Name:")
            Subject_code = st.text_input("Subject Code:")
            Number_of_questions = st.number_input("Number of Questions:", min_value=0)
            with st.form("question_paper_form"):
                st.write("Fill in the details below to create a question paper:")
                questions = []
                for i in range(Number_of_questions):
                    question = st.text_input(f"Question {i+1}:")
                    answer = st.text_input(f"Answer for Question {i+1}:")
                    marks = st.number_input(f"Marks for Question {i+1}:", min_value=0)
                    questions.append((question, answer, marks))
                if st.form_submit_button("Create Question Paper"):
                    question_paper = {
                        "Subject_name": Subject_name,
                        "Subject_code": Subject_code,
                        "Number_of_questions": Number_of_questions,
                        "questions": [],
                    }
                    for i in range(Number_of_questions):
                        question, answer, marks = questions[i]
                        question_paper["questions"].append(
                            {"question": question, "answer": answer, "marks": marks}
                        )
                    with open("question_paper.json", "r+") as json_file:
                        data = json.load(json_file)
                        subject_code_ = next(
                            (
                                i
                                for i, subject in enumerate(data["subjects"])
                                if subject["Subject_code"] == Subject_code
                            ),
                            None,
                        )
                        if subject_code_ is None:
                            data["subjects"].append(question_paper)
                            json_file.seek(0)
                            json.dump(data, json_file, indent=4)
                            json_file.truncate()
                            st.success("Question paper created successfully!")
                        else:
                            st.error("Subject code already exists. Please try again.")
            if st.button("Clear all questions"):
                with open("question_paper.json", "r+") as json_file:
                    data = json.load(json_file)
                    data["subjects"] = []
                    json_file.seek(0)
                    json.dump(data, json_file, indent=4)
                    json_file.truncate()
                    st.success("All questions cleared successfully!")
        else:
            st.warning("Please login/signup to access this page.")
    elif page == "View Question Papers":
        if session_state.get("logged_in"):
            st.title("View Question Papers")
            with open("question_paper.json", "r") as json_file:
                data = json.load(json_file)
            if len(data["subjects"]) == 0:
                st.warning("No question papers found.")
                return
            for i in range(len(data["subjects"])):
                st.subheader(f"{data['subjects'][i]['Subject_name']} - {data['subjects'][i]['Subject_code']}")
                st.write(f"Number of Questions: {data['subjects'][i]['Number_of_questions']}")
                for j in range(data["subjects"][i]["Number_of_questions"]):
                    st.write(f"Question {j+1}: {data['subjects'][i]['questions'][j]['question']}")
                    st.write(f"Answer: {data['subjects'][i]['questions'][j]['answer']}")
                    st.write(f"Marks: {data['subjects'][i]['questions'][j]['marks']}")
                    st.write('\n')
                st.write('---')
        else:
            st.warning("Please login/signup to access this page.")
    
    elif page == "View Student Responses":
        if session_state.get("logged_in"):
            st.title("View Student Responses")
            with open("students.json", "r") as json_file:
                data = json.load(json_file)
            if len(data["students"]) == 0:
                st.warning("No student responses found.")
                return
            for i in range(len(data["students"])):
                if data["students"][i]["exams"] == None:
                    continue
                st.write(f"Student {i+1}:")
                st.write(f"Name: {data['students'][i]['name']}")
                st.write(f"Email: {data['students'][i]['email']}")
                for exam in data["students"][i]["exams"]:
                    st.write(f"Subject: {exam['Subject_name']}")
                    st.write(f"Subject Code: {exam['Subject_code']}")
                    st.write(f"Number of Questions: {exam['Number_of_questions']}")
                    total_marks = 0
                    obtained_marks = 0
                    for j in range(exam["Number_of_questions"]):
                        total_marks += int(exam['questions'][j]['total_marks'])
                        obtained_marks += int(exam['questions'][j]['marks'])
                    for j in range(exam["Number_of_questions"]):
                        st.write(f"Question {j+1}: {exam['questions'][j]['question']}")
                        st.write(f"Answer: {exam['questions'][j]['answer']}")
                        st.write(f"Evaluation: {exam['questions'][j]['evaluation']}")
                        st.write(f"Marks: {exam['questions'][j]['marks']}")
                        st.write('\n')
                    st.write('\n')
                    st.markdown(f"### Marks Obtained: {obtained_marks}/{total_marks}")
                st.write('---')
        else:
            st.warning("Please login/signup to access this page.")


if __name__ == "__main__":

    initialize_database()
    main()
