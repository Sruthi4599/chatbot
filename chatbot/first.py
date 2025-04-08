import streamlit as st
import google.generativeai as genai
import re

# Configure Gemini API
API_KEY = "YOUR_API_KEY"  # Replace with your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C"]

# Session State Initialization
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = {}

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "active_quiz_lang" not in st.session_state:
    st.session_state.active_quiz_lang = None

st.title("🤖 CodeGenie - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Intent Detection
def detect_intent(prompt):
    prompt_lower = prompt.lower()
    greetings = ["hi", "hello", "hey"]
    if any(greet in prompt_lower for greet in greetings):
        return "greeting"
    elif "learn" in prompt_lower:
        return "learn"
    elif prompt_lower.startswith("quiz") or "give me a quiz" in prompt_lower:
        return "quiz"
    elif "explain" in prompt_lower or extract_question_number(prompt):
        return "explain"
    return "chat"

def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# Generate Quiz
def generate_quiz(language):
    prompt = (
        f"Create a 10-question multiple-choice quiz on {language}. "
        f"Each question must have 4 options labeled A, B, C, D. "
        f"Indicate the correct answer at the end using 'Correct Answer: <Letter>'. "
        f"Format:\n1. Question?\nA. Option\nB. Option\nC. Option\nD. Option\nCorrect Answer: B\n"
    )
    response = model.generate_content(prompt)
    raw_questions = response.text.strip().split("\n\n")
    structured_questions = {}

    for i, q in enumerate(raw_questions, start=1):
        match = re.search(r'Correct Answer:\s*([A-Da-d])', q)
        correct_answer = match.group(1).upper() if match else "Unknown"
        question_text = re.sub(r'Correct Answer:.*', '', q).strip()
        structured_questions[i] = {"question": question_text, "answer": correct_answer}

    st.session_state.quiz_questions[language] = structured_questions
    st.session_state.active_quiz_lang = language

# Quiz UI with Buttons
def quiz_ui(language):
    questions = st.session_state.quiz_questions.get(language, {})
    if not questions:
        st.warning("Please generate a quiz first.")
        return

    st.subheader(f"{language} Quiz")

    for q_num, q_data in questions.items():
        with st.expander(f"Question {q_num}"):
            st.markdown(q_data["question"])
            options = ['A', 'B', 'C', 'D']
            selected = st.radio(
                f"Your answer for Q{q_num}:", options, key=f"answer_{q_num}"
            )

            if st.button(f"Submit Q{q_num}", key=f"submit_{q_num}"):
                correct = q_data["answer"]
                if selected == correct:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct answer is {correct}")
                st.session_state.user_answers[q_num] = selected

# Recommend Resources
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}. Provide direct links."
    response = model.generate_content(prompt)
    return response.text

# Explain a Quiz Question
def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

def explain_answer(question_text, correct_answer):
    prompt = f"Explain why the correct answer to this quiz question is {correct_answer}: {question_text}"
    response = model.generate_content(prompt)
    return response.text

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Handler
if prompt := st.chat_input("Say something..."):
    intent = detect_intent(prompt)
    language = extract_language(prompt)

    if intent == "greeting":
        response_text = "Hello! How can I assist you today?"

    elif intent == "learn":
        response_text = recommend_resources(language) if language else "Which programming language would you like to learn?"

    elif intent == "quiz":
        if language:
            generate_quiz(language)
            response_text = f"Here is your {language} quiz!"
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
            response_text = "Please specify the question number or paste the full question."

    else:
        response_text = model.generate_content(prompt).text

    # Store user and assistant messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

# Always show quiz interface if active
if st.session_state.active_quiz_lang:
    quiz_ui(st.session_state.active_quiz_lang)
