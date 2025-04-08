import streamlit as st
import google.generativeai as genai
import re

# Configure the Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Supported languages
SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C"]

# Session state init
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = {}

st.title("🤖 CodeGenie - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Detect user intent
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

# Extract language
def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# Generate quiz
def generate_quiz(language):
    prompt = (
        f"Create a 10-question multiple-choice quiz on {language}. "
        f"Each question must have 4 options labeled A, B, C, D. "
        f"Indicate the correct answer at the end using 'Correct Answer: <Letter>'. "
        f"Format: \n1. Question?\nA. Option\nB. Option\nC. Option\nD. Option\nCorrect Answer: B\n"
    )
    response = model.generate_content(prompt)

    raw_questions = response.text.strip().split("\n\n")
    structured_questions = {}
    display_texts = []

    for i, q in enumerate(raw_questions, start=1):
        match = re.search(r'Correct Answer:\s*([A-Da-d])', q)
        correct_answer = match.group(1).upper() if match else "Unknown"
        question_text = re.sub(r'Correct Answer:.*', '', q).strip()
        structured_questions[i] = {"question": question_text, "answer": correct_answer}
        display_texts.append(f"Q{i}. {question_text}")

    st.session_state.quiz_questions[language] = structured_questions
    return "\n\n".join(display_texts)

# Recommend resources
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}. Provide direct links."
    response = model.generate_content(prompt)
    return response.text

# Evaluate answer
def evaluate_answer(language, question_number, user_answer):
    questions = st.session_state.quiz_questions.get(language, {})
    if question_number in questions:
        correct_answer = questions[question_number]["answer"]
        if user_answer.strip().upper() == correct_answer:
            return "✅ Correct!"
        else:
            return f"❌ Incorrect. The correct answer is: {correct_answer}"
    return "Question not found."

# Extract question number for explanations
def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

# Explain answers
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
        response_text = recommend_resources(language) if language else "Which programming language would you like to learn?"

    elif intent == "quiz":
        response_text = generate_quiz(language) if language else "Which programming language quiz would you like to attempt?"

    elif intent == "answer":
        match = re.search(r'question\s*(\d+)\s*answer\s*[:\-]?\s*([a-dA-D])', prompt, re.IGNORECASE)
        if match:
            q_num = int(match.group(1))
            user_ans = match.group(2)
            if st.session_state.quiz_questions:
                last_lang = list(st.session_state.quiz_questions.keys())[-1]
                response_text = evaluate_answer(last_lang, q_num, user_ans)
            else:
                response_text = "Please generate a quiz first."
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

        if matched_question:
            response_text = explain_answer(matched_question, correct_answer)
        else:
            response_text = "Please provide the question number or paste the full question."

    else:
        response_text = model.generate_content(prompt).text

    # Update chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
