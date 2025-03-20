import streamlit as st
import google.generativeai as genai
import json

# Set up Google Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Store chat history
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask me something or request a quiz (e.g., 'I want a Python quiz')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Detect quiz request
    if "quiz" in prompt.lower():
        language = "Python"  # Default language (can be extracted from user input)
        st.write(f"🎯 Generating a {language} quiz...")

        quiz_prompt = (
            f"Generate a {language} multiple-choice quiz with 5 questions. "
            "Provide JSON format output with keys: 'question', 'options' (list), and 'answer' (letter)."
        )

        response = model.generate_content(quiz_prompt).text

        # **Fix: Parse JSON correctly**
        try:
            quiz_data = json.loads(response)  # Convert response to Python dictionary
            if isinstance(quiz_data, list):
                st.session_state.quiz_data = quiz_data
                st.session_state.user_answers = {}

        except json.JSONDecodeError:
            st.error("⚠️ Failed to parse quiz questions. Please try again.")

    else:
        # Regular chatbot response
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)

# Display Quiz UI
if st.session_state.quiz_data:
    st.write("### 📌 Quiz Time! Answer the following questions:")

    for i, q in enumerate(st.session_state.quiz_data):
        st.write(f"**{i + 1}. {q['question']}**")
        st.session_state.user_answers[i] = st.radio(
            f"Select your answer for Q{i+1}:",
            q["options"],
            index=None,
            key=f"q{i}"
        )

    # Submit button
    if st.button("Submit Quiz"):
        score = 0
        for i, ans in st.session_state.user_answers.items():
            correct_option = st.session_state.quiz_data[i]["answer"]
            correct_index = ["A", "B", "C", "D"].index(correct_option)
            correct_text = st.session_state.quiz_data[i]["options"][correct_index]

            if ans == correct_text:
                score += 1

        st.success(f"Your Score: {score}/{len(st.session_state.quiz_data)} 🎉")
