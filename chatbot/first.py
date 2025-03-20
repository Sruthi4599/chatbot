import streamlit as st
import google.generativeai as genai
import random
import json

# Set Google Gemini API key
GENAI_API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY"
genai.configure(api_key=GENAI_API_KEY)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# Function to generate quiz questions
def generate_quiz(language="Python", num_questions=10):
    prompt = f"Generate {num_questions} multiple-choice quiz questions for {language}. Each question should have 4 options (A, B, C, D) and a correct answer."
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    try:
        questions = json.loads(response.text)
        return questions
    except:
        return None

# Function to calculate score
def calculate_score():
    if "quiz" not in st.session_state or not st.session_state.quiz:
        return 0, len(st.session_state.user_answers)
    
    correct_count = 0
    for i, question in enumerate(st.session_state.quiz):
        if i in st.session_state.user_answers:
            if st.session_state.user_answers[i] == question["answer"]:
                correct_count += 1
    return correct_count, len(st.session_state.quiz)

# UI Layout
st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge.")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask me something or request a quiz (e.g., 'I want a Python quiz')")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if "quiz" in user_input.lower():
        lang = "Python"  # Default language
        for l in ["Python", "Java", "C++", "JavaScript"]:
            if l.lower() in user_input.lower():
                lang = l
                break
        
        st.session_state.quiz = generate_quiz(lang, 10)
        st.session_state.user_answers = {}

        if st.session_state.quiz:
            response = f"🎯 Generating 10 {lang} questions...\n\n"
        else:
            response = "⚠️ Failed to parse questions. Please try again."

    else:
        response = f"🤖 Sorry, I can only provide programming quizzes and tutorials."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Display quiz if available
if st.session_state.quiz:
    st.subheader("📝 Quiz Time! Answer the following questions:")
    
    for i, q in enumerate(st.session_state.quiz):
        st.write(f"**{i+1}. {q['question']}**")
        user_answer = st.radio(
            f"Select your answer for Q{i+1}:",
            options=q["options"],
            index=None,
            key=f"q_{i}",
        )
        if user_answer:
            st.session_state.user_answers[i] = user_answer
    
    if st.button("Submit Quiz"):
        score, total = calculate_score()
        st.success(f"Your Score: {score}/{total} 🎉")
        st.session_state.quiz = None  # Reset after submission
        st.session_state.user_answers = {}

