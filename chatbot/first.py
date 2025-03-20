import streamlit as st
import google.generativeai as genai

API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me something or request a quiz (e.g., 'I want a Python quiz')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "quiz" in prompt.lower():
        language = "Python"
        if "java" in prompt.lower():
            language = "Java"
        elif "c++" in prompt.lower():
            language = "C++"
        elif "javascript" in prompt.lower():
            language = "JavaScript"

        quiz_prompt = f"Generate 5 multiple-choice questions for {language}. Each question should have exactly 4 options (A, B, C, D) and specify the correct answer. Format: \nQ: <question>\nA) <option1>\nB) <option2>\nC) <option3>\nD) <option4>\nCorrect: <correct_option>"
        
        response = model.generate_content(quiz_prompt)
        quiz_text = response.text.strip()

        # Parse questions
        questions = []
        blocks = quiz_text.split("\n\n")
        for block in blocks:
            lines = block.split("\n")
            if len(lines) >= 6:
                q_text = lines[0][3:].strip()
                options = [lines[i][3:].strip() for i in range(1, 5)]
                correct = lines[5].split(":")[-1].strip()
                questions.append({"question": q_text, "options": options, "answer": correct})

        st.session_state.quiz_data = questions
        st.session_state.user_answers = {i: None for i in range(len(questions))}

    else:
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)

if st.session_state.quiz_data:
    st.write("### Your Quiz")
    for idx, q in enumerate(st.session_state.quiz_data):
        st.write(f"**{idx + 1}. {q['question']}**")
        st.session_state.user_answers[idx] = st.radio(
            f"Select your answer for Q{idx + 1}:", 
            q["options"], 
            index=None, 
            key=f"q{idx}"
        )

    if st.button("Submit Quiz"):
        score = sum(
            1 for i, ans in st.session_state.user_answers.items() 
            if ans and ans.startswith(st.session_state.quiz_data[i]["answer"])
        )
        st.success(f"Your Score: {score}/{len(st.session_state.quiz_data)} 🎉")
