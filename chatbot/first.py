import streamlit as st
import google.generativeai as genai

# Configure the Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Supported programming languages
SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript"]

# Initialize chat history and quiz storage
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = {}  # Store questions per language

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Function to detect user intent
def detect_intent(prompt):
    greetings = ["hi", "hello", "hey"]
    if any(greet in prompt.lower() for greet in greetings):
        return "greeting"
    elif "learn" in prompt.lower():
        return "learn"
    elif "quiz" in prompt.lower():
        return "quiz"
    elif "explain" in prompt.lower():
        return "explain"
    return "chat"

# Function to extract programming language
def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# Function to generate quiz questions
def generate_quiz(language):
    prompt = f"Generate a multiple-choice quiz with 10 questions on {language}. Provide options and indicate the correct answer."
    response = model.generate_content(prompt)
    
    # Store questions in session state
    st.session_state.quiz_questions[language] = response.text
    return response.text

# Function to recommend learning resources
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}."
    response = model.generate_content(prompt)
    return response.text

# Function to explain a quiz question
def explain_answer(question):
    prompt = f"Explain the correct answer to this quiz question: {question}"
    response = model.generate_content(prompt)
    return response.text

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Say something..."):
    intent = detect_intent(prompt)
    language = extract_language(prompt)
    
    if intent == "greeting":
        response_text = "Hello! How can I assist you today?"
    
    elif intent == "learn":
        if language:
            response_text = recommend_resources(language)
        else:
            response_text = "Which programming language would you like to learn?"
    
    elif intent == "quiz":
        if language:
            response_text = generate_quiz(language)
        else:
            response_text = "Which programming language quiz would you like to attempt?"
    
    elif intent == "explain":
        # Check if a question from the quiz is mentioned
        matched_question = None
        for lang, questions in st.session_state.quiz_questions.items():
            if prompt in questions:  # Checking if the user request matches any question
                matched_question = prompt
                break

        if matched_question:
            response_text = explain_answer(matched_question)
        else:
            response_text = "Please specify the exact quiz question you need an explanation for."
    
    else:
        response_text = model.generate_content(prompt).text  # General AI response

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
