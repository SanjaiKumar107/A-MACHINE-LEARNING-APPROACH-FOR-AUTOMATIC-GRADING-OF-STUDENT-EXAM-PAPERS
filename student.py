import json
import os
import streamlit as st
from streamlit import session_state
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from time import sleep
load_dotenv()




safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0



def get_text_from_image(image):
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY_1"))
        image = Image.open(image)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(["Please analyze the handwritten text in the provided image and provide the corresponding text.", image], safety_settings=safety_settings)
        return response.text
    except Exception as e:
        st.error(f"Error getting text from image: {e}")
        return None
    
def evaluate(question, answer_key, student_answer):
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY_2"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""Question: {question}\n\nAnswer Key: {answer_key}\n\nStudent Answer: {student_answer}\n\nPlease read the question and the answer key provided below to understand the context. Then, evaluate the student's answer based on the answer key. Give feedback on the student's answer. Do not give suggested answers. Do not write heading at start of the response.      
        """
        response = model.generate_content(prompt,safety_settings=safety_settings)
        return response.text

    except Exception as e:
        st.error(f"Error getting marks: {e}")
        return None
    
    
def get_marks(question, answer_key, student_answer, total_marks):
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY_3"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""Question: {question}\n\nAnswer Key: {answer_key}\n\nStudent Answer: {student_answer}\n\nTotal Marks: {total_marks}\n\nPlease read the question and the answer key provided below to understand the context. Then, evaluate the student's answer based on the answer key and allocate marks accordingly from the total marks given. Give the marks obtained by the student for the question as an integer value and do not write any additional text.
        
        For example, if the student obtained 5 marks out of 10, you should enter 5 as the response.     
        """
        response = model.generate_content(prompt,safety_settings=safety_settings)
        return response.text

    except Exception as e:
        st.error(f"Error getting marks: {e}")
        return None


def signup(json_file_path="students.json"):
    st.title("Student Signup Page")
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

        for user in data["students"]:
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
    json_file_path="students.json", question_paper="question_paper.json"
):
    try:
        if not os.path.exists(json_file_path):
            data = {"students": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
        if not os.path.exists(question_paper):
            data = {"subjects": []}
            with open(question_paper, "w") as json_file:
                json.dump(data, json_file)
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(name, email, age, sex, password, json_file_path="students.json"):
    try:
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"students": []}
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
            "exams": None,
        }

        data["students"].append(user_info)

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
            for user in data["students"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None


def render_dashboard(user_info, json_file_path="evaluator.json"):
    try:
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("Student Information")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def main(json_file_path="students.json", question_paper="question_paper.json"):
    st.title("Evaluator Dashboard")
    page = st.sidebar.radio(
        "Go to",
        (
            "Signup/Login",
            "Dashboard",
            "Attempt Exam",
        ),
        key="page",
    )
    # page = st.sidebar.radio(
    #     "Go to",
    #     (
    #         "Signup/Login",
    #         "Dashboard",
    #         "Attempt Exam",
    #         "View Previous Exams",
    #     ),
    #     key="page",
    # )

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

    elif page == "Attempt Exam":
        if session_state.get("logged_in"):

            st.title("Attempt Exam")
            user_info = session_state["user_info"]
            with open("question_paper.json", "r") as question_data_json_file:
                question_data = json.load(question_data_json_file)
            codes = [subject["Subject_name"] +" - " +subject["Subject_code"] for subject in question_data["subjects"]]
            codes.insert(0, "--Select--")
            subject_code = st.selectbox(
                "Select a subject code to attempt the exam:", codes
            )
            if subject_code != "--Select--":
                subject_code = subject_code.split(" - ")[1]
                subject_code_ = next(
                    (
                        i
                        for i, subject in enumerate(question_data["subjects"])
                        if subject["Subject_code"] == subject_code
                    ),
                    None,
                )
                if subject_code_ is not None:
                    exam = question_data["subjects"][subject_code_]
                    questions = exam["questions"]
                    st.write(f"Subject: {exam['Subject_name']}")
                    st.write(f"Subject Code: {exam['Subject_code']}")
                    number_of_questions = len(questions)
                    question_details = []
                    with st.form("exam_form"):
                        for i in range(number_of_questions):
                            st.write(f"Question {i+1}: {questions[i]['question']}")
                            answer = st.file_uploader(f"Upload your answer for Question {i+1}:", type=["jpg", "jpeg", "png"])
                            question_details.append(
                                {
                                    "question": questions[i]["question"],
                                    "answer": answer,
                                    "answer_key" :questions[i]["answer"],
                                    "total_marks": questions[i]["marks"],
                                }
                            )
                        if st.form_submit_button("Submit Exam"):
                            final_details = {
                                "Subject_name": exam["Subject_name"],
                                "Subject_code": exam["Subject_code"],
                                "Number_of_questions": number_of_questions,
                                "questions": [],
                            }
                            for response in question_details:
                                question = response["question"]
                                answer_key = response["answer_key"]
                                student_answer = get_text_from_image(response["answer"])
                                total_marks = response["total_marks"]
                                evaluation = evaluate(question, answer_key, student_answer)
                                marks = get_marks(question, answer_key, student_answer, total_marks)
                                response["marks"] = marks
                                final_details["questions"].append({
                                    "question": question,
                                    "answer": student_answer,
                                    "answer_key": answer_key,
                                    "total_marks": total_marks,
                                    "evaluation": evaluation,
                                    "marks": marks,
                                })
                                sleep(1)

                            with open("students.json", "r+") as json_file_student:
                                student_data = json.load(json_file_student)
                                student_email = next(
                                    (
                                        i
                                        for i, student in enumerate(student_data["students"])
                                        if student["email"] == user_info["email"]
                                    ),
                                    None,
                                )
                                if student_email is not None:
                                    if student_data["students"][student_email]["exams"] is None:
                                        student_data["students"][student_email]["exams"] = []
                                    student_data["students"][student_email]["exams"].append(
                                        final_details
                                    )
                                    json_file_student.seek(0)
                                    json.dump(student_data, json_file_student, indent=4)
                                    json_file_student.truncate()
                                    st.success("Exam submitted successfully!")
                else:
                    st.error("Invalid subject code. Please try again.")
        
    # elif page == "View Previous Exams":
    #     if session_state.get("logged_in"):
    #         st.title("View Previous Exams")
    #         with open("students.json", "r") as json_file:
    #             data = json.load(json_file)
    #             student = next(
    #                 (
    #                     i
    #                     for i, student in enumerate(data["students"])
    #                     if student["email"] == session_state["user_info"]["email"]
    #                 ),
    #                 None,
    #             )
    #             if student is not None:
    #                 if data["students"][student]["exams"] is not None:
    #                     for exam in data["students"][student]["exams"]:
    #                         st.write(f"Subject: {exam['Subject_name']}")
    #                         st.write(f"Subject Code: {exam['Subject_code']}")
    #                         st.write(f"Number of Questions: {exam['Number_of_questions']}")
    #                         for i in range(exam["Number_of_questions"]):
    #                             st.write(f"Question {i+1}: {exam['questions'][i]['question']}")
    #                             st.write(f"Answer: {exam['questions'][i]['answer']}")
    #                             st.write(f"Answer Key: {exam['questions'][i]['answer_key']}")
    #                             st.write(f"Marks: {exam['questions'][i]['marks']}")
    #                             st.write('\n')
    #                         st.write('\n')
    #                 else:
    #                     st.error("No exams found. Please attempt an exam.")
    #             else:
    #                 st.error("No exams found. Please attempt an exam.")
            
    #     else:
    #         st.warning("Please login/signup to access this page.")


if __name__ == "__main__":

    initialize_database()
    main()
