import streamlit as st
import google.generativeai as genai

# Configure the Gemini API
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Supported programming languages
SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript"]

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Initialize session state for quiz
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = ""
if "quiz_language" not in st.session_state:
    st.session_state.quiz_language = ""
if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""

# Function to detect user intent
def detect_intent(prompt):
    greetings = ["hi", "hello", "hey"]
    if any(greet in prompt.lower() for greet in greetings):
        return "greeting"
    elif "learn" in prompt.lower():
        return "learn"
    elif "quiz" in prompt.lower():
        return "quiz"
    return "chat"

# Function to extract programming language
def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# Function to generate quiz questions
def generate_quiz(language):
    prompt = f"Generate a basic multiple-choice quiz with 5 questions on {language}. Provide 4 answer choices and indicate the correct answer."
    response = model.generate_content(prompt)
    
    questions = []
    lines = response.text.strip().split("\n")
    
    for line in lines:
        if line.strip():
            questions.append(line.strip())
    
    return questions

# Function to explain quiz questions
def explain_answer(question):
    prompt = f"Explain the correct answer to this quiz question: {question}"
    response = model.generate_content(prompt)
    return response.text

# Handle user input
if prompt := st.chat_input("Say something..."):
    intent = detect_intent(prompt)
    language = extract_language(prompt)
    
    if intent == "greeting":
        response_text = "Hello! How can I assist you today?"
    elif intent == "learn":
        if language:
            learn_prompt = f"Recommend YouTube videos, websites, and books for learning {language}."
            response_text = model.generate_content(learn_prompt).text
        else:
            response_text = "Which programming language would you like to learn?"
    elif intent == "quiz":
        if language:
            st.session_state.quiz_active = True
            st.session_state.quiz_language = language
            st.session_state.quiz_questions = generate_quiz(language)
            st.session_state.current_question = 0
        else:
            response_text = "Which programming language quiz would you like to attempt?"
    else:
        response_text = model.generate_content(prompt).text  # General AI response

    # Store chat messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Display ongoing quiz
if st.session_state.quiz_active:
    if st.session_state.current_question < len(st.session_state.quiz_questions):
        question = st.session_state.quiz_questions[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1}")
        st.write(question)
        
        user_input = st.text_input("Your Answer:")
        
        if user_input:
            correct_answer = question.split("Correct Answer: ")[-1].strip()
            st.session_state.correct_answer = correct_answer
            
            if user_input.lower() == correct_answer.lower():
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Wrong! The correct answer is {correct_answer}.")
                explanation = explain_answer(question)
                st.info(f"Explanation: {explanation}")
            
            # Move to the next question
            st.session_state.current_question += 1
            st.session_state.user_answer = ""

    else:
        st.success("🎉 Quiz completed! Want to try another quiz?")
        st.session_state.quiz_active = False
