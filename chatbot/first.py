import streamlit as st
import google.generativeai as genai
import re  # For extracting question numbers and answers

# Configure the Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Supported programming languages
SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C"]

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
    elif re.search(r'question\s*\d+\s*answer\s*[:\-]?\s*[a-dA-D]', prompt.lower()):
        return "answer"
    return "chat"

# Function to extract programming language
def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# Function to generate quiz questions without showing the correct answer
def generate_quiz(language):
    prompt = f"Generate a multiple-choice quiz with 10 questions on {language}. Provide options and indicate the correct answer."
    response = model.generate_content(prompt)

    questions = response.text.strip().split("\n\n")  # Assuming questions are separated by double newlines
    structured_questions = {}
    display_texts = []

    for i, q in enumerate(questions, start=1):
        match = re.search(r'Correct Answer:\s*(.*)', q)
        correct_answer = match.group(1) if match else "Unknown"
        question_text = re.sub(r'Correct Answer:.*', '', q).strip()
        structured_questions[i] = {"question": question_text, "answer": correct_answer}
        display_texts.append(f"Q{i}. {question_text}")

    st.session_state.quiz_questions[language] = structured_questions
    return "\n\n".join(display_texts)

# Function to recommend learning resources
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}. Provide direct links to access them."
    response = model.generate_content(prompt)
    return response.text

# Function to evaluate user's quiz answer
def evaluate_answer(language, question_number, user_answer):
    questions = st.session_state.quiz_questions.get(language, {})
    if question_number in questions:
        correct_answer = questions[question_number]["answer"].strip().lower()
        if user_answer.strip().lower() == correct_answer:
            return "✅ Correct!"
        else:
            return f"❌ Incorrect. The correct answer is: {questions[question_number]['answer']}"
    return "Question not found."

# Function to extract question number from user input (used for explanation intent)
def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

# Function to explain a quiz question
def explain_answer(question_text, correct_answer):
    prompt = f"Explain why the correct answer to this quiz question is {correct_answer}: {question_text}"
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

    elif intent == "answer":
        match = re.search(r'question\s*(\d+)\s*answer\s*[:\-]?\s*([a-dA-D])', prompt, re.IGNORECASE)
        if match:
            question_number = int(match.group(1))
            user_answer = match.group(2)
            if st.session_state.quiz_questions:
                last_lang = list(st.session_state.quiz_questions.keys())[-1]
                response_text = evaluate_answer(last_lang, question_number, user_answer)
            else:
                response_text = "No quiz found to evaluate. Please start a quiz first."
        else:
            response_text = "Please use the format like: 'Question 3 Answer: A'"

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

        if not matched_question:
            for lang, questions in st.session_state.quiz_questions.items():
                for q_num, q_data in questions.items():
                    if prompt.lower() in q_data["question"].lower():
                        matched_question = q_data["question"]
                        correct_answer = q_data["answer"]
                        break
                if matched_question:
                    break

        if matched_question:
            response_text = explain_answer(matched_question, correct_answer)
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
