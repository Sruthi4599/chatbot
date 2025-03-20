import streamlit as st
import google.generativeai as genai

# Configure Google Gemini API
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Initialize session state
if "quiz" not in st.session_state:
    st.session_state.quiz = None
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.user_answers = []

# Function to generate quiz questions
def generate_quiz(language):
    prompt = f"""
    Generate a 10-question multiple-choice quiz on {language}.
    Each question should have four answer choices (a, b, c, d), a correct answer, and an explanation.
    Format:
    Question: <question text>
    a) <option1>
    b) <option2>
    c) <option3>
    d) <option4>
    Answer: <correct option letter>
    Explanation: <brief explanation>
    """

    response = model.generate_content(prompt)
    quiz_text = response.text.strip()

    # Split quiz text into individual questions
    quiz_data = quiz_text.split("\n\n")

    # Reset session variables
    st.session_state.quiz = []
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.user_answers = []

    for q in quiz_data:
        lines = q.strip().split("\n")
        if len(lines) >= 6:
            question = lines[0].replace("Question: ", "").strip()
            options = {
                "a": lines[1].replace("a) ", "").strip(),
                "b": lines[2].replace("b) ", "").strip(),
                "c": lines[3].replace("c) ", "").strip(),
                "d": lines[4].replace("d) ", "").strip()
            }
            correct = lines[5].replace("Answer: ", "").strip().lower()
            explanation = lines[6].replace("Explanation: ", "").strip()

            st.session_state.quiz.append({
                "question": question,
                "options": options,
                "correct": correct,
                "explanation": explanation
            })

    if not st.session_state.quiz:
        return "⚠️ Failed to generate quiz. Please try again!"
    return "✅ Quiz generated! Answer the questions below."

# Function to display the quiz
def display_quiz():
    if "quiz" in st.session_state and st.session_state.quiz:
        idx = st.session_state.current_index
        total_questions = len(st.session_state.quiz)

        if idx < total_questions:
            q_data = st.session_state.quiz[idx]
            st.write(f"**{idx + 1}. {q_data['question']}**")  

            # Radio button for selecting an answer
            options = list(q_data["options"].items())
            user_choice = st.radio("Select your answer:", options, index=None, key=f"q_{idx}")

            # Check answer
            if user_choice:
                st.session_state.user_answers.append(user_choice[0])  # Store the selected answer
                correct_ans = q_data["correct"]

                if user_choice[0].lower() == correct_ans:
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Wrong! The correct answer is {correct_ans.upper()}")
                    st.info(f"ℹ️ Explanation: {q_data['explanation']}")

                # Move to next question
                st.session_state.current_index += 1
                st.experimental_rerun()

        else:
            st.write(f"🎉 Quiz completed! Your final score: **{st.session_state.score}/{total_questions}**")
            del st.session_state.quiz  # Reset quiz

# Streamlit UI
st.title("🤖 CodeMat - Your AI Learning Assistant")
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

user_input = st.text_input("Ask me something or request a quiz (e.g., 'I want a Python quiz'): ")

if user_input:
    if "quiz" in user_input.lower():
        # Detect language from input
        words = user_input.lower().split()
        language = None
        for lang in ["python", "java", "c++", "javascript"]:
            if lang in words:
                language = lang
                break
        
        if language:
            st.session_state.quiz = None  # Reset previous quiz state
            st.write(f"📚 Generating a **{language}** quiz...")
            quiz_msg = generate_quiz(language)
            st.success(quiz_msg)
            st.experimental_rerun()
        else:
            st.error("⚠️ Please specify a programming language (Python, Java, C++, JavaScript).")
    else:
        st.write("🤖 I'm here to help! Ask me anything or request a quiz.")

# Display the quiz if available
display_quiz()
