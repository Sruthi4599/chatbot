import streamlit as st
import google.generativeai as genai
import re

# API Configuration
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferred_language" not in st.session_state:
    st.session_state.preferred_language = None
if "tutorials" not in st.session_state:
    st.session_state.tutorials = []
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

st.title("🤖 BookMate - Your AI Tutor")
st.write("Chat with me! Ask for programming tutorials and quizzes.")

# Display conversation history
for message in st.session_state.messages:
    role, text = message
    if role == "user":
        st.text_input("You:", value=text, key=text, disabled=True)
    else:
        st.write(f"🤖 {text}")

# User input
user_input = st.text_input("Type your message here:")

# Function to detect programming language
def detect_language(text):
    languages = ["Python", "Java", "C++", "JavaScript"]
    for lang in languages:
        if re.search(rf"\b{lang}\b", text, re.IGNORECASE):
            return lang
    return None

# Function to get more tutorials
def get_more_tutorials(language):
    extra_resources = {
        "Python": ["Fluent Python", "Python Data Science Handbook", "Python for Everybody"],
        "Java": ["Java: The Complete Reference", "Spring in Action", "Java Concurrency in Practice"],
        "C++": ["More Effective C++", "C++ Templates", "Design Patterns in Modern C++"],
        "JavaScript": ["Secrets of the JavaScript Ninja", "JavaScript Patterns", "Functional JavaScript"]
    }
    return extra_resources.get(language, [])

if user_input:
    st.session_state.messages.append(("user", user_input))
    
    # Detect if the user is asking for a programming language
    detected_language = detect_language(user_input)
    
    if detected_language:
        st.session_state.preferred_language = detected_language
        st.session_state.tutorials = [
            "Python Crash Course", "Automate the Boring Stuff", "LeetCode Python Challenges"
        ] if detected_language == "Python" else [
            "Effective Java", "Head First Java", "Java Programming on GeeksforGeeks"
        ] if detected_language == "Java" else [
            "The C++ Programming Language", "Accelerated C++", "C++ Primer"
        ] if detected_language == "C++" else [
            "Eloquent JavaScript", "JavaScript: The Good Parts", "You Don't Know JS"
        ]
        
        bot_response = f"Great! You want to learn **{detected_language}**. Here are some tutorials:\n"
        for tutorial in st.session_state.tutorials:
            bot_response += f"- {tutorial}\n"
        bot_response += "\nIf you want more tutorials, just ask!"
        st.session_state.messages.append(("bot", bot_response))
    
    elif "more tutorials" in user_input.lower() and st.session_state.preferred_language:
        more_tuts = get_more_tutorials(st.session_state.preferred_language)
        if more_tuts:
            st.session_state.tutorials.extend(more_tuts)
            bot_response = "Here are more tutorials:\n"
            for tutorial in more_tuts:
                bot_response += f"- {tutorial}\n"
        else:
            bot_response = "I have shared all available tutorials."
        st.session_state.messages.append(("bot", bot_response))
    
    elif "quiz" in user_input.lower() and st.session_state.preferred_language:
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

        st.session_state.quiz_questions = quiz_data[st.session_state.preferred_language]
        st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}

        bot_response = "Let's start your quiz! Answer the questions below."
        st.session_state.messages.append(("bot", bot_response))

    else:
        bot_response = "I didn't understand that. You can ask for tutorials or a quiz!"
        st.session_state.messages.append(("bot", bot_response))

# Step 4: Display Quiz
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

# Step 5: Display Final Score
if st.session_state.quiz_completed:
    st.write(f"### 🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}")
    if st.button("Retry"):
        st.session_state.quiz_started = False
        st.session_state.quiz_completed = False
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.score = 0
