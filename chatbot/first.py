import streamlit as st
import google.generativeai as genai
import re

# Configure Gemini API
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
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

# Detect Intent
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
        if question_text:
            structured_questions[i] = {"question": question_text, "answer": correct_answer}

    st.session_state.quiz_questions[language] = structured_questions
    st.session_state.active_quiz_lang = language

# Quiz UI
def quiz_ui(language):
    questions = st.session_state.quiz_questions.get(language, {})
    if not questions:
        st.warning("Please generate a quiz first.")
        return

    st.subheader(f"{language} Quiz")
    for q_num, q_data in questions.items():
        with st.expander(f"Question {q_num}", expanded=False):
            st.markdown(q_data["question"])
            options = ['A', 'B', 'C', 'D']
            selected = st.radio(f"Your answer for Q{q_num}:", options, key=f"answer_{q_num}")
            if st.button(f"Submit Q{q_num}", key=f"submit_{q_num}"):
                correct = q_data["answer"]
                if selected == correct:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct answer is {correct}")
                st.session_state.user_answers[q_num] = selected

# Recommend Learning Resources with Clickable Links
def recommend_resources(language):
    # Predefined resource links for demonstration.
    resources = {
        "Python": (
            "[Python Official Docs](https://docs.python.org/3/)\n"
            "[W3Schools - Python](https://www.w3schools.com/python/)\n"
            "[Corey Schafer YouTube](https://www.youtube.com/user/schafer5)"
        ),
        "Java": (
            "[Java Official Docs](https://docs.oracle.com/javase/8/docs/)\n"
            "[GeeksforGeeks - Java](https://www.geeksforgeeks.org/java/)"
        ),
        "C++": (
            "[cplusplus.com](http://www.cplusplus.com/)\n"
            "[LearnCPP](https://www.learncpp.com/)"
        ),
        "JavaScript": (
            "[MDN JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)\n"
            "[JavaScript Info](https://javascript.info/)"
        ),
        "C": (
            "[Learn-C.org](https://www.learn-c.org/)\n"
            "[TutorialsPoint C](https://www.tutorialspoint.com/cprogramming/index.htm)"
        )
    }
    # Return resources as a markdown-formatted string
    return resources.get(language, "No resources available for this language.")

# Explain a Quiz Question
def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

def explain_answer(question_text, correct_answer):
    prompt = f"Explain why the correct answer to this quiz question is {correct_answer}: {question_text}"
    response = model.generate_content(prompt)
    return response.text

# --- Display Quiz Interface at the Top ---
if st.session_state.active_quiz_lang:
    quiz_ui(st.session_state.active_quiz_lang)

# --- Chat Input ---
if prompt := st.chat_input("Say something..."):
    intent = detect_intent(prompt)
    language = extract_language(prompt)
    response_text = ""

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
            response_text = "Please specify the question number or paste the full question for explanation."
    else:
        response_text = model.generate_content(prompt).text

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        st.markdown(response_text)

# --- Display Chat Messages After the Quiz ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
