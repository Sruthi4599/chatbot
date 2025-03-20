import streamlit as st
import google.generativeai as genai
import json

# Set up Google Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge.")

# Store chat history
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

# User input
if prompt := st.chat_input("Ask me something or request a quiz (e.g., 'I want a Python quiz')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Detect quiz request
    if "quiz" in prompt.lower():
        language = "Python"  # Default language (can be extracted from user input)
        st.write(f"🎯 Generating 10 {language} questions...")

        quiz_prompt = (
            f"Generate a {language} multiple-choice quiz with 10 questions. "
            "Provide JSON format output with keys: 'question', 'options' (list). Do not include answers."
        )

        response = model.generate_content(quiz_prompt).text

        # **Fix: Parse JSON correctly**
        try:
            quiz_data = json.loads(response)  # Convert response to Python dictionary
            if isinstance(quiz_data, list):
                st.session_state.quiz_data = quiz_data

        except json.JSONDecodeError:
            st.error("⚠️ Failed to parse questions. Please try again.")

    else:
        # Regular chatbot response
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)

# Display Questions (No Multiple-Choice Inputs)
if st.session_state.quiz_data:
    st.write("### 📌 Here are your 10 questions:")

    for i, q in enumerate(st.session_state.quiz_data):
        st.write(f"**{i + 1}. {q['question']}**")
        for option in q["options"]:
            st.write(f"- {option}")

