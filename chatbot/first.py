import streamlit as st
import google.generativeai as genai
import random

# API Configuration
API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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

# Learning Resources
resources = {
    "Python": {
        "Books": ["Python Crash Course", "Automate the Boring Stuff", "Fluent Python"],
        "Websites": ["https://docs.python.org", "https://realpython.com"],
        "Videos": ["https://www.youtube.com/watch?v=_uQrJ0TkZlc"]
    },
    "Java": {
        "Books": ["Effective Java", "Head First Java", "Java: The Complete Reference"],
        "Websites": ["https://docs.oracle.com/en/java/", "https://www.geeksforgeeks.org/java"],
        "Videos": ["https://www.youtube.com/watch?v=grEKMHGYyns"]
    },
    "C++": {
        "Books": ["The C++ Programming Language", "Accelerated C++", "C++ Primer"],
        "Websites": ["https://cplusplus.com", "https://www.geeksforgeeks.org/c-plus-plus/"],
        "Videos": ["https://www.youtube.com/watch?v=vLnPwxZdW4Y"]
    },
    "JavaScript": {
        "Books": ["Eloquent JavaScript", "JavaScript: The Good Parts", "You Don't Know JS"],
        "Websites": ["https://developer.mozilla.org/en-US/docs/Web/JavaScript"],
        "Videos": ["https://www.youtube.com/watch?v=W6NZfCO5SIk"]
    }
}

# Chatbot Title
st.title("🤖 CodeMate - Your AI Chatbot")

# Display chat history
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# User Input
user_input = st.chat_input("Type a message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Greetings
    if user_input.lower() in ["hi", "hello", "hey"]:
        response = "Hello! How can I assist you today?"

    # Detect Language & Ask for Intent
    elif any(lang.lower() in user_input.lower() for lang in resources.keys()):
        for lang in resources.keys():
            if lang.lower() in user_input.lower():
                st.session_state.selected_language = lang
                break
        response = f"Do you want to *learn* {st.session_state.selected_language} or *attempt a quiz*?"

    # Provide Learning Resources
    elif "learn" in user_input.lower() and st.session_state.selected_language:
        lang = st.session_state.selected_language
        response = f"Here are some learning resources for {lang}:\n\n"
        response += "**📚 Books:**\n" + "\n".join(f"- {book}" for book in resources[lang]["Books"]) + "\n\n"
        response += "**🌐 Websites:**\n" + "\n".join(f"- {site}" for site in resources[lang]["Websites"]) + "\n\n"
        response += "**📺 Videos:**\n" + "\n".join(f"- {video}" for video in resources[lang]["Videos"])

    # Start a Quiz
    elif "quiz" in user_input.lower() and st.session_state.selected_language:
        lang = st.session_state.selected_language

        # Generate Quiz Questions using Gemini API
        prompt = f"Generate 10 multiple-choice quiz questions with answers and explanations for {lang}."
        try:
            quiz_response = model.generate_content(prompt)
            quiz_data = eval(quiz_response.text)  # Convert API response to Python list

            st.session_state.quiz_questions = quiz_data
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.score = 0
            st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}

            response = f"Starting {lang} quiz. Answer the following questions:"
        except Exception as e:
            response = f"Error fetching quiz questions: {str(e)}"

    # Display Quiz Questions
    elif st.session_state.quiz_started and not st.session_state.quiz_completed:
        response = "### Quiz Time! Choose the correct answers:"
        for q in st.session_state.quiz_questions:
            selected_answer = st.radio(q["question"], q["options"], key=q["question"])
            st.session_state.quiz_answers[q["question"]] = selected_answer

        if st.button("Submit Quiz"):
            st.session_state.score = sum(
                1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
            )
            st.session_state.quiz_completed = True
            response = f"🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}"

    # Provide Explanation for Quiz
    elif "explain" in user_input.lower():
        for q in st.session_state.quiz_questions:
            if q["question"] in user_input:
                response = f"**Explanation:** {q['explanation']}"
                break

    # Default Response
    else:
        response = "I'm not sure how to respond. Try asking about programming languages, learning, or quizzes."

    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
