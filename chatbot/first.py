import streamlit as st
import google.generativeai as genai
import re  # For extracting question numbers

# Configure the Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Supported programming languages
SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript"]

# Initialize session state for chat history and quiz storage
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = {}  # Stores structured quiz questions per language

st.title("🤖 CodeGenie - Your AI Learning Assistant")
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

    # Split the response into individual questions
    questions = response.text.strip().split("\n\n")  # Assuming questions are separated by double newlines
    structured_questions = {i+1: q for i, q in enumerate(questions)}  # Numbering questions

    # Store structured questions in session state
    st.session_state.quiz_questions[language] = structured_questions

    return "\n\n".join(questions)  # Return formatted quiz text

# Function to recommend learning resources
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}."
    response = model.generate_content(prompt)
    return response.text

# Function to extract question number from user input
def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

# Function to explain a quiz question
def explain_answer(question_text):
    prompt = f"Explain the correct answer to this quiz question: {question_text}"
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
        question_number = extract_question_number(prompt)
        matched_question = None

        # If the user provided a question number, find it
        if question_number:
            for lang, questions in st.session_state.quiz_questions.items():
                if question_number in questions:
                    matched_question = questions[question_number]
                    break

        # If no number was found, check for direct question matches
        if not matched_question:
            for lang, questions in st.session_state.quiz_questions.items():
                for q_text in questions.values():
                    if prompt.lower() in q_text.lower():
                        matched_question = q_text
                        break
                if matched_question:
                    break

        if matched_question:
            response_text = explain_answer(matched_question)
        else:
            response_text = "Please specify the exact quiz question number or copy-paste the question you need an explanation for."

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
