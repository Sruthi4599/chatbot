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

# Predefined quiz questions
quiz_data = {
    "Python": [
        {"question": "What is the output of `print(2 ** 3)`?", "options": ["5", "6", "8", "10"], "answer": "8"},
        {"question": "Which data type is mutable?", "options": ["Tuple", "String", "List", "Integer"], "answer": "List"},
    ],
    "Java": [
        {"question": "Which keyword is used to inherit a class?", "options": ["implements", "extends", "inherits", "super"], "answer": "extends"},
        {"question": "What is the default value of an int variable?", "options": ["0", "null", "undefined", "1"], "answer": "0"},
    ]
}

# Learning resources
resources = {
    "Python": {
        "books": ["Python Crash Course", "Automate the Boring Stuff", "Effective Python"],
        "websites": ["https://realpython.com", "https://docs.python.org"],
        "videos": ["https://www.youtube.com/watch?v=_uQrJ0TkZlc"]
    },
    "Java": {
        "books": ["Effective Java", "Head First Java", "Java: The Complete Reference"],
        "websites": ["https://docs.oracle.com/en/java", "https://www.geeksforgeeks.org/java"],
        "videos": ["https://www.youtube.com/watch?v=eIrMbAQSU34"]
    }
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
    elif any(lang.lower() in user_input.lower() for lang in resources.keys()):
        detected_lang = next(lang for lang in resources.keys() if lang.lower() in user_input.lower())
        st.session_state.preferred_language = detected_lang
        response_text = f"Do you want to **learn** about {detected_lang} or attempt a **quiz**?"

    # Provide learning resources
    elif "learn" in user_input.lower() and st.session_state.preferred_language:
        lang = st.session_state.preferred_language
        response_text = f"Here are some **{lang}** learning resources:\n\n"

        response_text += "**📚 Books:**\n" + "\n".join([f"- {book}" for book in resources[lang]["books"]]) + "\n\n"
        response_text += "**🌐 Websites:**\n" + "\n".join([f"- [{site}]({site})" for site in resources[lang]["websites"]]) + "\n\n"
        response_text += "**🎥 YouTube Videos:**\n" + "\n".join([f"- [{vid}]({vid})" for vid in resources[lang]["videos"]])

    # Start quiz
    elif "quiz" in user_input.lower() and st.session_state.preferred_language:
        lang = st.session_state.preferred_language
        st.session_state.quiz_started = True
        st.session_state.quiz_questions = random.sample(quiz_data[lang], min(2, len(quiz_data[lang])))
        st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}
        response_text = f"Starting a **{lang}** quiz! Answer the following questions:"

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
            response_text += "Would you like to try another quiz?"

    # Store and display assistant response
    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
