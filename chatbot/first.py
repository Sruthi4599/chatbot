import streamlit as st
import google.generativeai as genai

# Configure the Google Gemini API
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Initialize session state
if "quiz" not in st.session_state:
    st.session_state.quiz = None

# Function to generate a quiz
def generate_quiz(language):
    prompt = f"""
    Generate a 10-question multiple-choice quiz on {language}.
    Each question should have four options (a, b, c, d), the correct answer, and an explanation.
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

    # Debugging: Print the response to check format
    print("Quiz Response:", quiz_text)

    # Ensure response is split correctly into questions
    quiz_data = quiz_text.split("\n\n")

    # Reset quiz state
    st.session_state.quiz = {"questions": [], "current_index": 0, "score": 0}

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
            st.session_state.quiz["questions"].append({
                "question": question, "options": options, "correct": correct, "explanation": explanation
            })

    if not st.session_state.quiz["questions"]:
        return "⚠️ Failed to generate quiz. Please try again!"

    return "✅ Quiz generated! Enter your answers (a/b/c/d) below."

# Function to display the quiz
def display_quiz():
    if "quiz" in st.session_state and st.session_state.quiz:
        if not st.session_state.quiz["questions"]:
            st.error("⚠️ No questions generated! Try requesting the quiz again.")
            return

        idx = st.session_state.quiz["current_index"]
        total_questions = len(st.session_state.quiz["questions"])

        if idx < total_questions:
            q_data = st.session_state.quiz["questions"][idx]
            st.write(f"**{idx + 1}. {q_data['question']}**")  

            # Display options
            for key, value in q_data["options"].items():
                st.write(f"**{key})** {value}")

            # Answer input
            user_answer = st.text_input("Enter your answer (a/b/c/d):", key=f"quiz_{idx}")
            if user_answer:
                correct_ans = q_data["correct"]
                if user_answer.lower() == correct_ans:
                    st.success("✅ Correct!")
                    st.session_state.quiz["score"] += 1
                else:
                    st.error(f"❌ Wrong! The correct answer is {correct_ans.upper()}")
                    st.info(f"ℹ️ Explanation: {q_data['explanation']}")

                # Move to next question
                st.session_state.quiz["current_index"] += 1
                st.experimental_rerun()

        else:
            st.write(f"🎉 Quiz completed! Your final score: **{st.session_state.quiz['score']}/{total_questions}**")
            del st.session_state.quiz

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>🤖 CodeMat - Your AI Learning Assistant</h1>", unsafe_allow_html=True)
st.write("Welcome! Learn programming or test your knowledge with quizzes.")

user_input = st.text_input("Ask me something or request a quiz (e.g., 'I want a Python quiz'): ")

if user_input:
    if "quiz" in user_input.lower():
        # Extract language from input
        words = user_input.lower().split()
        language = None
        for lang in ["python", "java", "c++", "javascript"]:
            if lang in words:
                language = lang
                break
        
        if language:
            st.session_state.quiz = None  # Reset quiz state
            st.write(f"📚 Generating a **{language}** quiz...")
            quiz_msg = generate_quiz(language)
            st.success(quiz_msg)
            st.experimental_rerun()
        else:
            st.error("⚠️ Please specify a programming language (Python, Java, C++, JavaScript).")
    else:
        st.write("🤖 I'm here to help! Ask me anything or request a quiz.")

# Display quiz if available
display_quiz()
