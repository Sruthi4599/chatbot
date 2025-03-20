import openai
import streamlit as st
import random

# Set OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

# Function to generate quiz questions using OpenAI API
def generate_quiz_questions(language):
    prompt = f"Generate a multiple-choice quiz with 10 questions on {language}. Each question should have 4 options and one correct answer."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    
    questions = []
    if response and "choices" in response:
        quiz_text = response["choices"][0]["message"]["content"]
        quiz_lines = quiz_text.split("\n")
        
        for i in range(0, len(quiz_lines), 6):
            if i + 5 < len(quiz_lines):
                question = quiz_lines[i].strip()
                options = [quiz_lines[i + j].strip() for j in range(1, 5)]
                answer = quiz_lines[i + 5].strip().split(":")[-1].strip()
                questions.append({"question": question, "options": options, "answer": answer})

    return questions[:10]  # Return only 10 questions

# Function to process user input
def process_input(user_input):
    if "quiz" in user_input.lower():
        detected_language = None
        for lang in ["Python", "Java", "C++", "JavaScript"]:
            if lang.lower() in user_input.lower():
                detected_language = lang
                break
        
        if detected_language:
            st.session_state.quiz_active = True
            st.session_state.quiz_questions = generate_quiz_questions(detected_language)
            st.session_state.quiz_answers = [q["answer"] for q in st.session_state.quiz_questions]
            st.session_state.current_question_index = 0
            st.session_state.quiz_score = 0
            return f"Starting the {detected_language} quiz! Here’s your first question:"
        else:
            return "Please specify which programming language quiz you want to attempt (Python, Java, C++, JavaScript)."
    
    if st.session_state.quiz_active:
        current_index = st.session_state.current_question_index
        if current_index < len(st.session_state.quiz_questions):
            correct_answer = st.session_state.quiz_answers[current_index]
            if user_input.strip().lower() == correct_answer.lower():
                st.session_state.quiz_score += 1
                response = "✅ Correct!"
            else:
                response = f"❌ Wrong answer! The correct answer was {correct_answer}."
            
            st.session_state.current_question_index += 1
            if st.session_state.current_question_index >= len(st.session_state.quiz_questions):
                final_score = st.session_state.quiz_score
                st.session_state.quiz_active = False
                return f"🎉 Quiz completed! Your final score: {final_score}/{len(st.session_state.quiz_questions)}"
            else:
                next_question = st.session_state.quiz_questions[st.session_state.current_question_index]["question"]
                return f"{response}\n\nNext Question: {next_question}"
    
    return "I didn't understand that. Please ask about a quiz or programming topic."

# Streamlit UI
st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Chat history display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Ask me anything about programming or say 'I want to attempt a Python quiz'!")

if prompt:
    response = process_input(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
