import streamlit as st
import google.generativeai as genai
import json
import re  # Import regex for cleaning JSON responses

# Set up Google Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"  # Replace with your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Streamlit UI setup
st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge.")

# Initialize session state for quiz data
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

# User input
user_input = st.chat_input("Ask me something or request a quiz (e.g., 'I want a Python quiz')")

if user_input:
    st.write(f"📝 {user_input}")

    # Check if user requested a quiz
    if "quiz" in user_input.lower():
        language = "Python"  # Default to Python quiz
        st.write(f"🎯 Generating 10 {language} quiz questions...")

        # Prompt for generating quiz
        quiz_prompt = (
            f"Generate a {language} multiple-choice quiz with 10 questions. "
            "Provide JSON format output with keys: 'question' and 'options' (list of 4 choices). "
            "DO NOT include answers."
        )

        # Get response from Google Gemini
        response = model.generate_content(quiz_prompt).text

        # Extract JSON using regex
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            json_text = match.group(0)  # Extract JSON part

            try:
                quiz_data = json.loads(json_text)  # Convert to Python list
                if isinstance(quiz_data, list):
                    st.session_state.quiz_data = quiz_data
                else:
                    st.error("⚠️ Unexpected response format. Try again.")
            except json.JSONDecodeError:
                st.error("⚠️ JSON parsing failed. Try again.")

        else:
            st.error("⚠️ No JSON found in response. Try again.")

# Display the quiz questions
if st.session_state.quiz_data:
    st.write("### 📌 Here are your 10 questions:")
    for i, q in enumerate(st.session_state.quiz_data):
        st.write(f"**{i + 1}. {q['question']}**")
        for option in q["options"]:
            st.write(f"- {option}")
