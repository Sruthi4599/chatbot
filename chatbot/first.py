import streamlit as st
import google.generativeai as genai
import random

# API Configuration
API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferred_language" not in st.session_state:
    st.session_state.preferred_language = None
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "score" not in st.session_state:
    st.session_state.score = 0
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 10  # Default to 10 questions

# Predefined quiz questions (extend this list)
quiz_data = {
    "Python": [
        {"question": "What is the output of `print(2 ** 3)`?", "options": ["5", "6", "8", "10"], "answer": "8"},
        {"question": "Which data type is mutable?", "options": ["Tuple", "String", "List", "Integer"], "answer": "List"},
        {"question": "Which keyword is used to define a function?", "options": ["func", "def", "function", "define"], "answer": "def"},
        {"question": "What is the correct file extension for Python files?", "options": [".py", ".java", ".cpp", ".txt"], "answer": ".py"},
        {"question": "Which operator is used for floor division?", "options": ["/", "//", "%", "**"], "answer": "//"},
        {"question": "Which function is used to get user input?", "options": ["input()", "scan()", "get()", "read()"], "answer": "input()"},
        {"question": "Which data structure uses key-value pairs?", "options": ["List", "Tuple", "Dictionary", "Set"], "answer": "Dictionary"},
        {"question": "Which module is used for regular expressions?", "options": ["re", "regex", "pyre", "reg"], "answer": "re"},
        {"question": "What does `len()` return?", "options": ["Size of a list", "Memory address", "Last element", "None"], "answer": "Size of a list"},
        {"question": "What is the default return value of a function?", "options": ["0", "None", "Empty string", "False"], "answer": "None"},
    ],
    "Java": [
        {"question": "Which keyword is used to inherit a class?", "options": ["implements", "extends", "inherits", "super"], "answer": "extends"},
        {"question": "What is the default value of an int variable?", "options": ["0", "null", "undefined", "1"], "answer": "0"},
        {"question": "Which method is the entry point in a Java program?", "options": ["start()", "main()", "run()", "begin()"], "answer": "main()"},
        {"question": "Which keyword is used to define a constant?", "options": ["final", "const", "static", "immutable"], "answer": "final"},
        {"question": "Which Java collection allows duplicates?", "options": ["Set", "List", "Map", "Queue"], "answer": "List"},
        {"question": "What does JVM stand for?", "options": ["Java Virtual Machine", "Java Variable Memory", "Java Version Manager", "Java Visual Mode"], "answer": "Java Virtual Machine"},
        {"question": "Which loop is used when the number of iterations is known?", "options": ["for", "while", "do-while", "foreach"], "answer": "for"},
        {"question": "Which exception is thrown when a null object is accessed?", "options": ["NullPointerException", "IOException", "ArithmeticException", "RuntimeException"], "answer": "NullPointerException"},
        {"question": "What is used to create an object in Java?", "options": ["new", "create", "malloc", "alloc"], "answer": "new"},
        {"question": "Which access modifier allows visibility only within the same class?", "options": ["public", "private", "protected", "default"], "answer": "private"},
    ]
}

# Display chatbot UI
st.title("🤖 AI Programming Assistant")
st.write("Welcome! Ask me about programming languages, tutorials, or quizzes.")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process user input
if user_input := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response_text = ""

    # Greetings
    if user_input.lower() in ["hello", "hi", "hey"]:
        response_text = "Hello! How can I assist you today?"

    # Detect language request
    elif any(lang.lower() in user_input.lower() for lang in quiz_data.keys()):
        detected_lang = next(lang for lang in quiz_data.keys() if lang.lower() in user_input.lower())
        st.session_state.preferred_language = detected_lang
        response_text = f"Do you want to **learn** about {detected_lang} or attempt a **quiz**?"

    # Start quiz
    elif "quiz" in user_input.lower() and st.session_state.preferred_language:
        lang = st.session_state.preferred_language
        st.session_state.quiz_started = True
        st.session_state.quiz_questions = random.sample(quiz_data[lang], min(st.session_state.num_questions, len(quiz_data[lang])))
        st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}
        response_text = f"Starting a **{lang}** quiz! Answer the following {st.session_state.num_questions} questions:"

    # Allow user to request more questions
    elif any(word in user_input.lower() for word in ["more", "increase", "add"]):
        st.session_state.num_questions += 5  # Increase by 5
        response_text = f"Okay! Your next quiz will have **{st.session_state.num_questions}** questions."

    # Handle quiz questions
    if st.session_state.quiz_started:
        for q in st.session_state.quiz_questions:
            selected_answer = st.radio(q["question"], q["options"], key=q["question"])
            st.session_state.quiz_answers[q["question"]] = selected_answer

        if st.button("Submit Quiz"):
            st.session_state.score = sum(
                1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
            )
            response_text = f"🎉 Your Final Score: **{st.session_state.score}/{len(st.session_state.quiz_questions)}**\n\n"
            response_text += "Would you like another quiz?"

    # Store and display assistant response
    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
