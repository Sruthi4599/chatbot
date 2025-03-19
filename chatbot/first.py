import streamlit as st
import google.generativeai as genai
import re

# API Configuration
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state variables
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferred_language" not in st.session_state:
    st.session_state.preferred_language = None
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "score" not in st.session_state:
    st.session_state.score = 0

st.title("🤖 BookMate - Your AI Assistant")
st.write("Tell me what programming language you want to learn!")

# Step 1: User enters a sentence to specify the programming language
prompt = st.text_input("Type something like: 'I want to learn Python' or 'Teach me Java'.")

# Function to detect programming language from user input
def detect_language(text):
    languages = ["Python", "Java", "C++", "JavaScript"]
    for lang in languages:
        if re.search(rf"\b{lang}\b", text, re.IGNORECASE):
            return lang
    return None

if prompt:
    detected_language = detect_language(prompt)
    if detected_language:
        st.session_state.preferred_language = detected_language
        st.session_state.quiz_started = False
        st.session_state.quiz_completed = False
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.score = 0
        st.write(f"Great! You want to learn **{detected_language}**. Here are some resources:")

        recommendations = {
            "Python": ["Python Crash Course", "Automate the Boring Stuff", "LeetCode Python Challenges"],
            "Java": ["Effective Java", "Head First Java", "Java Programming on GeeksforGeeks"],
            "C++": ["The C++ Programming Language", "Accelerated C++", "C++ Primer"],
            "JavaScript": ["Eloquent JavaScript", "JavaScript: The Good Parts", "You Don't Know JS"]
        }

        for rec in recommendations[detected_language]:
            st.write(f"- {rec}")

        if st.button("Start Quiz"):
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.score = 0

            quiz_data = {
                "Python": [
                    {"question": "What is the output of `print(2 ** 3)`?", "options": ["5", "6", "8", "10"], "answer": "8"},
                    {"question": "Which data type is mutable?", "options": ["Tuple", "String", "List", "Integer"], "answer": "List"}
                ],
                "Java": [
                    {"question": "Which keyword is used to inherit a class?", "options": ["implements", "extends", "inherits", "super"], "answer": "extends"},
                    {"question": "What is the default value of an int variable?", "options": ["0", "null", "undefined", "1"], "answer": "0"}
                ],
                "C++": [
                    {"question": "Which operator is used for dynamic memory allocation?", "options": ["malloc", "new", "alloc", "create"], "answer": "new"},
                    {"question": "Which is the correct file extension for C++ programs?", "options": [".c", ".cpp", ".java", ".py"], "answer": ".cpp"}
                ],
                "JavaScript": [
                    {"question": "Which keyword is used to declare a constant?", "options": ["var", "let", "const", "static"], "answer": "const"},
                    {"question": "Which function converts a string to an integer?", "options": ["parseInt()", "toInteger()", "stringToInt()", "int()"], "answer": "parseInt()"}
                ]
            }

            st.session_state.quiz_questions = quiz_data[detected_language]
            st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}

# Step 3: Display Quiz
if st.session_state.quiz_started and not st.session_state.quiz_completed:
    st.write("### Quiz Time! Choose the correct answers:")

    for q in st.session_state.quiz_questions:
        selected_answer = st.radio(q["question"], q["options"], key=q["question"])
        st.session_state.quiz_answers[q["question"]] = selected_answer

    if st.button("Submit Quiz"):
        # Calculate Score
        st.session_state.score = sum(
            1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
        )
        st.session_state.quiz_completed = True

# Step 4: Display Final Score
if st.session_state.quiz_completed:
    st.write(f"### 🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}")
    if st.button("Retry"):
        st.session_state.quiz_started = False
        st.session_state.quiz_completed = False
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.score = 0
