import streamlit as st
import google.generativeai as genai
import re  # For extracting question numbers
import speech_recognition as sr  # For voice input
import subprocess  # For code execution

# Configure the Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Supported programming languages
SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C"]

# Initialize session state for chat history, quiz storage, and learning paths
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = {}

if "learning_progress" not in st.session_state:
    st.session_state.learning_progress = {}  # Track user progress per language

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
    elif "run code" in prompt.lower():
        return "code_execution"
    elif "voice" in prompt.lower():
        return "voice_input"
    return "chat"

# Function to extract programming language
def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# Function to track user progress
def track_progress(language, topic):
    if language not in st.session_state.learning_progress:
        st.session_state.learning_progress[language] = []
    if topic not in st.session_state.learning_progress[language]:
        st.session_state.learning_progress[language].append(topic)
    return f"Progress updated: You've covered {topic} in {language}."

# Function to generate quiz questions
def generate_quiz(language):
    prompt = f"Generate a multiple-choice quiz with 10 questions on {language}. Provide options and indicate the correct answer."
    response = model.generate_content(prompt)
    
    questions = response.text.strip().split("\n\n")
    structured_questions = {}
    
    for i, q in enumerate(questions, start=1):
        match = re.search(r'Correct Answer:\s*(.*)', q)
        correct_answer = match.group(1) if match else "Unknown"
        structured_questions[i] = {"question": q, "answer": correct_answer}
    
    st.session_state.quiz_questions[language] = structured_questions
    
    return "\n\n".join(q["question"] for q in structured_questions.values())

# Function to recommend learning resources
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}. Provide direct links to access them."
    response = model.generate_content(prompt)
    return response.text

# Function to extract question number from user input
def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

# Function to explain a quiz question
def explain_answer(question_text, correct_answer):
    prompt = f"Explain why the correct answer to this quiz question is {correct_answer}: {question_text}"
    response = model.generate_content(prompt)
    return response.text

# Function to execute code
def execute_code(code, language):
    if language == "Python":
        try:
            result = subprocess.run(["python3", "-c", code], capture_output=True, text=True)
            return result.stdout or result.stderr
        except Exception as e:
            return str(e)
    return "Code execution is currently supported only for Python."

# Function for voice input
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError:
            return "Error with the speech recognition service."

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
        correct_answer = ""

        if question_number:
            for lang, questions in st.session_state.quiz_questions.items():
                if question_number in questions:
                    matched_question = questions[question_number]["question"]
                    correct_answer = questions[question_number]["answer"]
                    break

        if matched_question:
            response_text = explain_answer(matched_question, correct_answer)
        else:
            response_text = "Please specify the exact quiz question number or copy-paste the question you need an explanation for."
    
    elif intent == "code_execution":
        response_text = execute_code(prompt.replace("run code", ""), language)
    
    elif intent == "voice_input":
        response_text = get_voice_input()
    
    else:
        response_text = model.generate_content(prompt).text

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
