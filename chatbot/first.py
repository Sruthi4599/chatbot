import streamlit as st
import google.generativeai as genai

# Configure the Gemini API
API_KEY = "AIzaSyD9ZPsFRIDK5oaXbZriD_Ib1CjGzV0mejk"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Supported programming languages
SUPPORTED_LANGUAGES = ["Python", "Java", "C++", "JavaScript"]

# Initialize chat history
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

# Function to detect user intent
def detect_intent(prompt):
    greetings = ["hi", "hello", "hey"]
    if any(greet in prompt.lower() for greet in greetings):
        return "greeting"
    elif "learn" in prompt.lower():
        return "learn"
    elif "quiz" in prompt.lower():
        return "quiz"
    elif "explain" in prompt.lower():
        return "explain"
    return "chat"

# Function to extract programming language
def extract_language(prompt):
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower() in prompt.lower():
            return lang
    return None

# Function to generate quiz questions with explanations
def generate_quiz(language):
    prompt = f"""
    Generate 10 multiple-choice quiz questions on {language}. 
    Each question should have four options labeled (a), (b), (c), (d), indicate the correct answer, and provide a brief explanation.
    Format:
    Question: <question>
    a) <option1>
    b) <option2>
    c) <option3>
    d) <option4>
    Answer: <correct option>
    Explanation: <explanation>
    """
    response = model.generate_content(prompt)
    quiz_data = response.text.split("\n\n")  # Splitting questions properly
    st.session_state.quiz = {"questions": [], "current_index": 0, "score": 0}  # Reset quiz state
    
    for q in quiz_data:
        lines = q.split("\n")
        if len(lines) >= 7:
            question = lines[0].replace("Question: ", "").strip()
            options = [lines[1], lines[2], lines[3], lines[4]]
            correct = lines[5].replace("Answer: ", "").strip().lower()
            explanation = lines[6].replace("Explanation: ", "").strip()
            st.session_state.quiz["questions"].append({
                "question": question, "options": options, "correct": correct, "explanation": explanation
            })

    return "Quiz generated! Enter your answers (a/b/c/d) below."

# Function to recommend learning resources
def recommend_resources(language):
    prompt = f"Recommend YouTube videos, websites, and books for learning {language}."
    response = model.generate_content(prompt)
    return response.text

# Function to explain quiz questions
def explain_answer(question):
    prompt = f"Explain the correct answer to this quiz question: {question}"
    response = model.generate_content(prompt)
    return response.text

# Function to display and handle quiz interaction
def display_quiz():
    if "quiz" in st.session_state and st.session_state.quiz["questions"]:
        idx = st.session_state.quiz["current_index"]
        if idx < len(st.session_state.quiz["questions"]):
            q_data = st.session_state.quiz["questions"][idx]
            st.write(f"**{q_data['question']}**")
            
            # Display options properly
            for option in q_data["options"]:
                st.write(option)

            # Answer input
            user_answer = st.text_input("Enter your answer (a/b/c/d):", key=f"quiz_{idx}")
            if user_answer:
                correct_ans = q_data["correct"].strip().lower()
                if user_answer.lower() == correct_ans:
                    st.success("✅ Correct!")
                    st.session_state.quiz["score"] += 1
                else:
                    st.error(f"❌ Wrong! The correct answer is {correct_ans.upper()}")
                    st.info(f"ℹ️ Explanation: {q_data['explanation']}")

                # Move to next question
                st.session_state.quiz["current_index"] += 1

        else:
            st.write(f"🎉 Quiz finished! Your final score: {st.session_state.quiz['score']}/{len(st.session_state.quiz['questions'])}")
            del st.session_state.quiz  # Reset quiz

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Say something..."):
    intent = detect_intent(prompt)
    language = extract_language(prompt)
    
    if intent == "greeting":
        response_text = "Hello! How can I assist you today?"
    elif intent == "learn":
        if language:
            response_text = recommend_resources(language)
        else:
            response_text = "Which programming language would you like to learn?"
    elif intent == "quiz":
        if language:
            response_text = generate_quiz(language)
        else:
            response_text = "Which programming language quiz would you like to attempt?"
    elif intent == "explain":
        response_text = explain_answer(prompt)
    else:
        response_text = model.generate_content(prompt).text  # General AI response

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

# Call quiz display function
display_quiz()
