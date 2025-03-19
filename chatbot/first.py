import streamlit as st
import random

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
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
if "selected_language" not in st.session_state:
    st.session_state.selected_language = None

# Predefined quiz questions and explanations
quiz_data = {
    "Python": [
        {"question": "What is the output of `print(2 ** 3)`?", "options": ["5", "6", "8", "10"], "answer": "8",
         "explanation": "2 to the power of 3 is 8."},
        {"question": "Which data type is mutable?", "options": ["Tuple", "String", "List", "Integer"], "answer": "List",
         "explanation": "Lists are mutable, meaning they can be changed after creation."},
        {"question": "What keyword is used to define a function?", "options": ["func", "def", "function", "define"], "answer": "def",
         "explanation": "Python uses `def` to define functions."},
        {"question": "What is the index of the first element in a Python list?", "options": ["1", "0", "-1", "Depends"], "answer": "0",
         "explanation": "In Python, list indices start at 0."},
        {"question": "Which library is used for data manipulation in Python?", "options": ["numpy", "pandas", "matplotlib", "seaborn"], "answer": "pandas",
         "explanation": "Pandas is commonly used for data manipulation and analysis."},
    ],
    "Java": [
        {"question": "Which keyword is used to inherit a class?", "options": ["implements", "extends", "inherits", "super"], "answer": "extends",
         "explanation": "In Java, `extends` is used for class inheritance."},
        {"question": "What is the default value of an int variable?", "options": ["0", "null", "undefined", "1"], "answer": "0",
         "explanation": "Java initializes `int` variables with 0 by default."},
        {"question": "Which method is called when an object is created?", "options": ["constructor", "main", "init", "start"], "answer": "constructor",
         "explanation": "Constructors are called when an object is instantiated."},
    ],
    "C++": [
        {"question": "Which operator is used for dynamic memory allocation?", "options": ["malloc", "new", "alloc", "create"], "answer": "new",
         "explanation": "The `new` operator is used for dynamic memory allocation in C++."},
        {"question": "Which is the correct file extension for C++ programs?", "options": [".c", ".cpp", ".java", ".py"], "answer": ".cpp",
         "explanation": "C++ files usually have the `.cpp` extension."},
    ],
    "JavaScript": [
        {"question": "Which keyword is used to declare a constant?", "options": ["var", "let", "const", "static"], "answer": "const",
         "explanation": "`const` is used to declare constants in JavaScript."},
        {"question": "Which function converts a string to an integer?", "options": ["parseInt()", "toInteger()", "stringToInt()", "int()"], "answer": "parseInt()",
         "explanation": "`parseInt()` converts a string to an integer in JavaScript."},
    ]
}

# Programming language resources
resources = {
    "Python": {
        "Books": ["Python Crash Course", "Automate the Boring Stuff", "Fluent Python"],
        "Websites": ["https://docs.python.org", "https://realpython.com", "https://www.geeksforgeeks.org/python"],
        "Videos": ["https://www.youtube.com/watch?v=_uQrJ0TkZlc", "https://www.youtube.com/watch?v=rfscVS0vtbw"]
    },
    "Java": {
        "Books": ["Effective Java", "Head First Java", "Java: The Complete Reference"],
        "Websites": ["https://docs.oracle.com/en/java/", "https://www.geeksforgeeks.org/java"],
        "Videos": ["https://www.youtube.com/watch?v=grEKMHGYyns", "https://www.youtube.com/watch?v=eIrMbAQSU34"]
    }
}

# Chatbot title
st.title("🤖 CodeMate - Your AI Chatbot")

# Display chat history
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# User input
user_input = st.chat_input("Type a message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Greetings
    greetings = ["hi", "hello", "hey"]
    if any(greet in user_input.lower() for greet in greetings):
        response = "Hello! How can I assist you today?"

    # Detect language and ask for intent
    elif any(lang.lower() in user_input.lower() for lang in quiz_data.keys()):
        for lang in quiz_data.keys():
            if lang.lower() in user_input.lower():
                st.session_state.selected_language = lang
                break
        response = f"Do you want to learn {st.session_state.selected_language} or attempt a quiz?"

    # Provide learning resources
    elif "learn" in user_input.lower() and st.session_state.selected_language:
        lang = st.session_state.selected_language
        response = f"Here are some learning resources for {lang}:\n\n"
        response += "**Books:**\n" + "\n".join(f"- {book}" for book in resources[lang]["Books"]) + "\n\n"
        response += "**Websites:**\n" + "\n".join(f"- {site}" for site in resources[lang]["Websites"]) + "\n\n"
        response += "**Videos:**\n" + "\n".join(f"- {video}" for video in resources[lang]["Videos"])

    # Start a quiz
    elif "quiz" in user_input.lower() and st.session_state.selected_language:
        lang = st.session_state.selected_language
        st.session_state.quiz_questions = random.sample(quiz_data[lang], min(10, len(quiz_data[lang])))
        st.session_state.quiz_started = True
        st.session_state.quiz_completed = False
        st.session_state.score = 0
        st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}
        response = f"Starting {lang} quiz. Answer the following questions:"

    # Answer quiz questions
    elif st.session_state.quiz_started and not st.session_state.quiz_completed:
        for q in st.session_state.quiz_questions:
            selected_answer = st.radio(q["question"], q["options"], key=q["question"])
            st.session_state.quiz_answers[q["question"]] = selected_answer

        if st.button("Submit Quiz"):
            st.session_state.score = sum(
                1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
            )
            st.session_state.quiz_completed = True
            response = f"🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}"

    # Provide explanations
    elif "explain" in user_input.lower():
        for q in st.session_state.quiz_questions:
            if q["question"] in user_input:
                response = f"Explanation: {q['explanation']}"
                break

    # Default response
    else:
        response = "I'm not sure how to respond to that. Try asking about programming languages, learning, or quizzes."

    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
