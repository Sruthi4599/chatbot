pip install openai
import openai
import streamlit as st
import random

# Set OpenAI API Key (Replace with your actual key)
openai.api_key = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

# Function to generate quiz questions using OpenAI API
def generate_quiz_questions(language):
    try:
        prompt = f"Generate 5 multiple-choice questions for a {language} programming quiz. Each question should have 4 options (A, B, C, D) and one correct answer in this format:\nQ: <question>\nA) <option1>\nB) <option2>\nC) <option3>\nD) <option4>\nAnswer: <correct option>."
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        
        quiz_text = response["choices"][0]["message"]["content"]
        quiz_lines = quiz_text.split("\n")

        questions = []
        for i in range(0, len(quiz_lines), 6):
            if i + 5 < len(quiz_lines):
                question = quiz_lines[i][3:].strip()  # Extract question
                options = {
                    "A": quiz_lines[i+1][3:].strip(),
                    "B": quiz_lines[i+2][3:].strip(),
                    "C": quiz_lines[i+3][3:].strip(),
                    "D": quiz_lines[i+4][3:].strip()
                }
                answer = quiz_lines[i+5].split(":")[-1].strip()  # Extract correct answer
                questions.append({"question": question, "options": options, "answer": answer})

        return questions if questions else None
    except Exception as e:
        return None

# Function to process user input
def process_input(user_input):
    if "quiz" in user_input.lower():
        detected_language = None
        for lang in ["Python", "Java", "C++", "JavaScript"]:
            if lang.lower() in user_input.lower():
                detected_language = lang
                break
        
        if detected_language:
            quiz_data = generate_quiz_questions(detected_language)
            if not quiz_data:
                return "⚠️ Unable to fetch quiz questions. Please try again."

            st.session_state.quiz_active = True
            st.session_state.quiz_questions = quiz_data
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            return f"📢 Starting the {detected_language} quiz! Here’s your first question:\n\n{quiz_data[0]['question']}\nA) {quiz_data[0]['options']['A']}\nB) {quiz_data[0]['options']['B']}\nC) {quiz_data[0]['options']['C']}\nD) {quiz_data[0]['options']['D']}"

        return "Please specify a programming language for the quiz (Python, Java, C++, JavaScript)."

    if st.session_state.quiz_active:
        if st.session_state.quiz_index < len(st.session_state.quiz_questions):
            correct_answer = st.session_state.quiz_questions[st.session_state.quiz_index]["answer"]

            # Check if user input matches correct answer
            if user_input.strip().upper() == correct_answer:
                st.session_state.quiz_score += 1
                response = "✅ Correct!"
            else:
                response = f"❌ Wrong! The correct answer was {correct_answer}."

            st.session_state.quiz_index += 1
            if st.session_state.quiz_index >= len(st.session_state.quiz_questions):
                final_score = st.session_state.quiz_score
                st.session_state.quiz_active = False
                return f"{response}\n\n🎉 Quiz completed! Your final score: {final_score}/{len(st.session_state.quiz_questions)}"

            next_question = st.session_state.quiz_questions[st.session_state.quiz_index]
            return f"{response}\n\nNext Question:\n\n{next_question['question']}\nA) {next_question['options']['A']}\nB) {next_question['options']['B']}\nC) {next_question['options']['C']}\nD) {next_question['options']['D']}"

    return "I didn't understand that. Please ask about a quiz or programming topic."

# Streamlit UI
st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask me anything about programming or start a quiz (e.g., 'I want to attempt a Python quiz').")

if user_input:
    response = process_input(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
