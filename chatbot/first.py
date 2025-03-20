import streamlit as st
import google.generativeai as genai

API_KEY = "YOUR_ACTUAL_API_KEY"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me something or request a quiz (e.g., 'I want a Python quiz')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Detect if user is asking for a quiz
    if "quiz" in prompt.lower():
        language = "Python"  # Default to Python if not specified
        if "java" in prompt.lower():
            language = "Java"
        elif "c++" in prompt.lower():
            language = "C++"
        elif "javascript" in prompt.lower():
            language = "JavaScript"

        quiz_prompt = f"Generate 5 multiple-choice questions for {language}. Each question should have 4 options and indicate the correct answer."
        response = model.generate_content(quiz_prompt)
        quiz_text = response.text

        # Parse the generated quiz text into questions, options, and correct answers
        questions = []
        for q_block in quiz_text.split("\n\n"):
            lines = q_block.split("\n")
            if len(lines) >= 5:
                question = lines[0].strip()
                options = [lines[i].strip() for i in range(1, 5)]
                correct_answer = lines[5].split(":")[-1].strip() if len(lines) > 5 else None
                questions.append((question, options, correct_answer))

        st.session_state.messages.append({"role": "assistant", "content": "Here is your quiz:"})
        with st.chat_message("assistant"):
            st.markdown("Here is your quiz:")

            user_answers = {}
            for idx, (question, options, correct_answer) in enumerate(questions):
                st.write(f"**{idx + 1}. {question}**")
                user_answers[idx] = st.radio(f"Select an answer for question {idx + 1}:", options, key=f"q{idx}")

            if st.button("Submit Quiz"):
                score = sum(1 for i, ans in user_answers.items() if ans == questions[i][2])
                st.success(f"Your Score: {score}/{len(questions)} 🎉")
    else:
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
