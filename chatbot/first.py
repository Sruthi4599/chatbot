import streamlit as st
import google.generativeai as genai
import json
import re  # Added to clean JSON responses

# Set up Google Gemini API
API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge.")

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

# User input
if prompt := st.chat_input("Ask me something or request a quiz (e.g., 'I want a Python quiz')"):
    st.write(f"📝 {prompt}")

    # Detect quiz request
    if "quiz" in prompt.lower():
        language = "Python"  # Default language
        st.write(f"🎯 Generating 10 {language} questions...")

        quiz_prompt = (
            f"Generate a {language} multiple-choice quiz with 10 questions. "
            "Provide JSON format output with keys: 'question', 'options'. Do NOT include answers."
        )

        response = model.generate_content(quiz_prompt).text

        # **Fix: Extract valid JSON using regex**
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            json_text = match.group(0)  # Extract JSON part

            try:
                quiz_data = json.loads(json_text)  # Convert response to Python dictionary
                if isinstance(quiz_data, list):
                    st.session_state.quiz_data = quiz_data
                else:
                    st.error("⚠️ Unexpected response format. Try again.")
            except json.JSONDecodeError:
                st.error("⚠️ JSON parsing failed. Try again.")

        else:
            st.error("⚠️ No JSON found in response. Try again.")

# Display Questions
if st.session_state.quiz_data:
    st.write("### 📌 Here are your 10 questions:")
    for i, q in enumerate(st.session_state.quiz_data):
        st.write(f"**{i + 1}. {q['question']}**")
        for option in q["options"]:
            st.write(f"- {option}")
