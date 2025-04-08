import streamlit as st
import google.generativeai as genai
import re

# --- CONFIGURATION ---
API_KEY = "YOUR_API_KEY"  # Replace with your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C"]

# --- SESSION STATE ---
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
if "mode" not in st.session_state:
    st.session_state.mode = "idle"

st.title("🤖 CodeGenie - Your AI Learning Assistant")
st.write("Learn programming or test your knowledge with a quiz!")

# --- INTENT DETECTION ---
def detect_intent(prompt):
    if "explain" in prompt.lower() or extract_question_number(prompt):
        return "explain"
    elif "quiz" in prompt.lower():
        return "quiz"
    elif "learn" in prompt.lower():
        return "learn"
    elif any(greet in prompt.lower() for greet in ["hi", "hello", "hey"]):
        return "greeting"
    return "chat"

def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# --- GENERATE QUIZ ---
def generate_quiz(language):
    prompt = (
        f"Create a 10-question multiple-choice quiz on {language}.\n"
        f"Each question should follow this format:\n\n"
        f"Q: <question text>\nA. <option1>\nB. <option2>\nC. <option3>\nD. <option4>\nCorrect Answer: <A/B/C/D>"
    )
    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Use regex to parse properly formatted questions
    question_blocks = re.findall(
        r"Q:\s*(.?)\nA\.\s(.?)\nB\.\s(.?)\nC\.\s(.?)\nD\.\s(.?)\nCorrect Answer:\s([A-D])",
        raw, re.DOTALL
    )

    structured = {}
    for i, block in enumerate(question_blocks, 1):
        q, a, b, c, d, correct = block
        question_text = f"{q.strip()}\n\nA. {a.strip()}\nB. {b.strip()}\nC. {c.strip()}\nD. {d.strip()}"
        structured[i] = {"question": question_text, "answer": correct.strip().upper()}

    if not structured:
        st.error("❌ Failed to generate valid questions. Please try again.")
        return

    st.session_state.quiz_questions[language] = structured
    st.session_state.active_quiz_lang = language
    st.session_state.mode = "quiz"

# --- DISPLAY QUIZ UI ---
def quiz_ui(language):
    questions = st.session_state.quiz_questions.get(language, {})
    if not questions:
        st.warning("No quiz found. Generate one first.")
        return

    st.subheader(f"{language} Quiz")

    for q_num, q_data in questions.items():
        if not q_data.get("question") or not q_data.get("answer"):
            continue

        with st.expander(f"Question {q_num}"):
            st.markdown(q_data["question"])
            selected = st.radio(
                f"Choose your answer for Q{q_num}:", ["A", "B", "C", "D"],
                key=f"answer_{q_num}"
            )
            if st.button(f"Submit Q{q_num}", key=f"submit_{q_num}"):
                correct = q_data["answer"]
                if selected == correct:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct answer is {correct}")
                st.session_state.user_answers[q_num] = selected

# --- RECOMMEND LEARNING RESOURCES ---
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}. Include direct links."
    response = model.generate_content(prompt)
    return response.text

# --- EXPLANATION HANDLING ---
def extract_question_number(prompt):
    match = re.search(r'\bquestion (\d+)\b', prompt, re.IGNORECASE)
    return int(match.group(1)) if match else None

def explain_answer(question_text, correct_answer):
    prompt = f"Explain why the correct answer to this question is {correct_answer}: {question_text}"
    response = model.generate_content(prompt)
    return response.text

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT HANDLER ---
if prompt := st.chat_input("Say something..."):
    intent = detect_intent(prompt)
    language = extract_language(prompt)
    response_text = ""

    if intent == "greeting":
        response_text = "Hey there! How can I help you today?"

    elif intent == "learn":
        if language:
            response_text = recommend_resources(language)
        else:
            response_text = "Which language would you like to learn?"

    elif intent == "quiz":
        if language:
            generate_quiz(language)
            response_text = f"✅ Generated a quiz on {language}! Scroll down to take it."
        else:
            response_text = "Which programming language quiz do you want?"

    elif intent == "explain":
        question_number = extract_question_number(prompt)
        matched_q = None
        correct = ""

        for lang, questions in st.session_state.quiz_questions.items():
            for q_num, q_data in questions.items():
                if question_number and q_num == question_number:
                    matched_q = q_data["question"]
                    correct = q_data["answer"]
                    break
                elif prompt.strip().lower()[:20] in q_data["question"].lower():
                    matched_q = q_data["question"]
                    correct = q_data["answer"]
                    break
            if matched_q:
                break

        if matched_q:
            response_text = explain_answer(matched_q, correct)
        else:
            response_text = "Please specify the question number or paste the question for explanation."

    else:
        response_text = model.generate_content(prompt).text

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

# --- KEEP QUIZ UI VISIBLE ---
if st.session_state.active_quiz_lang:
    quiz_ui(st.session_state.active_quiz_lang)
