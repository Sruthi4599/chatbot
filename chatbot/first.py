import streamlit as st
import google.generativeai as genai

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
st.write("Welcome! Tell me what programming language you want to learn.")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if user_input := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Detect user intent
    if any(lang in user_input.lower() for lang in ["python", "java", "c++", "javascript"]):
        for lang in ["Python", "Java", "C++", "JavaScript"]:
            if lang.lower() in user_input.lower():
                st.session_state.preferred_language = lang
                break
        
        response_text = f"Great! You want to learn {st.session_state.preferred_language}. Here are some tutorials:\n"
        
        tutorial_data = {
            "Python": ["Python Crash Course", "Automate the Boring Stuff", "LeetCode Python Challenges"],
            "Java": ["Effective Java", "Head First Java", "Java Programming on GeeksforGeeks"],
            "C++": ["The C++ Programming Language", "Accelerated C++", "C++ Primer"],
            "JavaScript": ["Eloquent JavaScript", "JavaScript: The Good Parts", "You Don't Know JS"]
        }
        
        response_text += "\n".join(f"- {t}" for t in tutorial_data[st.session_state.preferred_language])
        response_text += "\n\nType 'more' if you want additional resources or 'quiz' to start the quiz."

    elif user_input.lower() == "more" and st.session_state.preferred_language:
        extra_resources = {
            "Python": ["Python for Data Science", "Fluent Python", "CS50 Python Course"],
            "Java": ["Java Concurrency in Practice", "Spring Boot in Action", "Java Design Patterns"],
            "C++": ["More Effective C++", "Modern C++ Design", "C++ Templates"],
            "JavaScript": ["JavaScript Patterns", "Secrets of the JavaScript Ninja", "Functional JavaScript"]
        }
        
        response_text = "Here are more resources:\n" + "\n".join(f"- {t}" for t in extra_resources[st.session_state.preferred_language])
        response_text += "\n\nType 'quiz' to start the quiz."

    elif user_input.lower() == "quiz" and st.session_state.preferred_language:
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
        response_text = "Quiz started! Choose the correct answers."

    else:
        response_text = "Sorry, I didn't understand that. Tell me what language you want to learn!"

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

# Quiz Display
if st.session_state.quiz_started and not st.session_state.quiz_completed:
    st.write("### Quiz Time! Choose the correct answers:")
    
    for q in st.session_state.quiz_questions:
        selected_answer = st.radio(q["question"], q["options"], key=q["question"])
        st.session_state.quiz_answers[q["question"]] = selected_answer

    if st.button("Submit Quiz"):
        st.session_state.score = sum(
            1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
        )
        st.session_state.quiz_completed = True

# Final Score
if st.session_state.quiz_completed:
    final_score_text = f"🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}"
    st.session_state.messages.append({"role": "assistant", "content": final_score_text})
    with st.chat_message("assistant"):
        st.markdown(final_score_text)

    if st.button("Retry"):
        st.session_state.quiz_started = False
        st.session_state.quiz_completed = False
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.score = 0
