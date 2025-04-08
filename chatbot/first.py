import streamlit as st
import google.generativeai as genai
import re

# Configure Gemini API
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C"]

# Session Initialization
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
st.write("Learn programming, take quizzes, and get answers explained!")

# --- Utility Functions ---
def detect_intent(prompt):
    prompt = prompt.lower()
    if any(greet in prompt for greet in ["hi", "hello", "hey"]):
        return "greeting"
    elif "learn" in prompt:
        return "learn"
    elif "quiz" in prompt:
        return "quiz"
    elif "explain" in prompt:
        return "explain"
    return "chat"

def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

def generate_quiz(language):
    prompt = (
        f"Create 10 multiple-choice questions on {language}. "
        f"Each should include a question, four options labeled A to D. "
        f"Do NOT include the correct answer. Format like:\n"
        f"1. Question?\nA. ...\nB. ...\nC. ...\nD. ..."
    )
    response = model.generate_content(prompt)
    questions_raw = response.text.strip().split("\n\n")
    structured = {}

    for i, q in enumerate(questions_raw, start=1):
        lines = q.strip().split("\n")
        if len(lines) >= 5:
            question_text = "\n".join(lines[:5])
            structured[i] = {
                "question": question_text,
                "full": q,
                "answer": None
            }

    st.session_state.quiz_questions[language] = structured
    st.session_state.active_quiz_lang = language

def recommend_resources(language):
    prompt = f"Suggest some good YouTube videos, websites, and books to learn {language}. Provide clickable links using markdown format."
    return model.generate_content(prompt).text

def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

def explain_answer(question_text, user_answer):
    prompt = f"Here's a quiz question:\n{question_text}\nI chose: {user_answer}\nExplain whether it's correct and why."
    return model.generate_content(prompt).text

# --- Quiz UI ---
def quiz_ui(language):
    questions = st.session_state.quiz_questions.get(language, {})
    st.subheader(f"{language} Quiz")

    for q_num, q_data in questions.items():
        with st.expander(f"Question {q_num}"):
            st.markdown(q_data["question"])
            selected = st.radio("Choose your answer:", ['A', 'B', 'C', 'D'], key=f"answer_{q_num}")

            if st.button("Submit", key=f"submit_{q_num}"):
                st.session_state.user_answers[q_num] = selected
                explanation = explain_answer(q_data["question"], selected)
                st.info(explanation)

# --- Chat History Display ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input Logic ---
if prompt := st.chat_input("Ask me to learn, quiz, or explain..."):
    intent = detect_intent(prompt)
    language = extract_language(prompt)
    response_text = ""

    if intent == "greeting":
        response_text = "Hey there! Ready to learn or take a quiz?"

    elif intent == "learn":
        response_text = recommend_resources(language) if language else "Which programming language would you like to learn?"

    elif intent == "quiz":
        if language:
            generate_quiz(language)
            response_text = f"Here is your {language} quiz!"
        else:
            response_text = "Please mention which language you want the quiz in."

    elif intent == "explain":
        lang = st.session_state.active_quiz_lang
        question_number = extract_question_number(prompt)
        found = False

        # Try to explain quiz question
        if lang:
            questions = st.session_state.quiz_questions.get(lang, {})
            if question_number:
                q_data = questions.get(question_number)
                user_answer = st.session_state.user_answers.get(question_number)
                if q_data and user_answer:
                    response_text = explain_answer(q_data["question"], user_answer)
                    found = True
            else:
                for q_num, q_data in questions.items():
                    if q_data["question"].strip() in prompt:
                        user_answer = st.session_state.user_answers.get(q_num)
                        if user_answer:
                            response_text = explain_answer(q_data["question"], user_answer)
                        else:
                            response_text = "Please submit your answer first before asking for an explanation."
                        found = True
                        break

        # Not a quiz question — treat it as a general programming/interview question
        if not found:
            explain_prompt = f"Explain this programming interview question clearly:\n{prompt}"
            response_text = model.generate_content(explain_prompt).text

    else:
        response_text = model.generate_content(prompt).text

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        st.markdown(response_text)

# --- Quiz Display at Bottom ---
if st.session_state.active_quiz_lang:
    quiz_ui(st.session_state.active_quiz_lang)
