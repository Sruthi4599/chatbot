import streamlit as st
import json
import re
import google.generativeai as genai
from utils import init_db, register_user, authenticate_user, save_score, get_scores
import pandas as pd
from datetime import datetime

# -----------------------------
# Configure Gemini Model
# -----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


model = genai.GenerativeModel(model_name="gemini-flash-latest")

# Extract text safely
def extract_text(resp):
    try:
        return resp.text
    except:
        try:
            return resp.candidates[0].content.parts[0].text
        except:
            return ""

# -----------------------------
# Initialize DB
# -----------------------------
init_db()

# -----------------------------
# Streamlit Layout
# -----------------------------
st.set_page_config(layout="wide")
st.title("🤖 CodeGenie – Learning Assistant")

# -----------------------------
# Sidebar → Login / Register
# -----------------------------
with st.sidebar:

    if "user_id" not in st.session_state:
        st.header("🔐 Login / Register")

        action = st.selectbox("Action", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button(action):
            if action == "Register":
                if register_user(username, password):
                    st.success("User Registered! Please login.")
                else:
                    st.error("Username already exists.")

            else:  # Login
                user_id = authenticate_user(username, password)
                if user_id:
                    st.session_state["user_id"] = user_id
                    st.session_state["username"] = username
                    st.success(f"Logged in as {username}")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    else:
        st.header(f"👋 Welcome, {st.session_state['username']}")
        st.header("📌 Navigation")
        page = st.radio("Go to", ["Home", "Progress", "Logout"])

        if page == "Logout":
            st.session_state.clear()
            st.success("Logged out successfully!")
            st.rerun()

# -----------------------------
# BODY (only if logged in)
# -----------------------------
if "user_id" in st.session_state:

    # -----------------------------
    # HOME PAGE → CHATBOT + QUIZ
    # -----------------------------
    if page == "Home":

        # Quiz Generator Panel
        with st.sidebar:
            st.header("📝 Generate Quiz")
            topic = st.text_input("Topic (Python, DBMS, OOPS, etc.)")
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            num_q = st.slider("Number of Questions", 3, 10, 5)

            if st.button("Generate Quiz"):
                if not topic.strip():
                    st.error("Please enter a quiz topic.")
                else:
                    prompt = f"""
                    Create a quiz with {num_q} MCQs on "{topic}" difficulty "{difficulty}".

                    STRICT RULES:
                    - Respond ONLY with a JSON array.
                    - NO markdown.
                    - Format:
                    [
                        {{
                            "question": "",
                            "options": ["", "", "", ""],
                            "answer": "",
                            "explanation": ""
                        }}
                    ]
                    """

                    try:
                        response = model.generate_content([prompt])
                        raw = extract_text(response)
                        raw = re.sub(r"```json|```", "", raw).strip()

                        st.session_state.quiz = json.loads(raw)
                        st.session_state.answers = {}
                        st.session_state.quiz_topic = topic  # SAVE SUBJECT/TOPIC
                        st.success("Quiz generated!")
                    except Exception as e:
                        st.error("JSON Parse Error")
                        st.write(str(e))

        # Chat + Quiz columns
        col1, col2 = st.columns([2, 1])

        # -------------------
        # Chatbot UI
        # -------------------
        with col1:
            st.subheader("💬 Chatbot")

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            user_msg = st.chat_input("Ask something...")

            if user_msg:
                st.session_state.chat_history.append(("user", user_msg))
                try:
                    response = model.generate_content(user_msg)
                    bot_reply = extract_text(response)
                except:
                    bot_reply = "⚠ Error generating reply."

                st.session_state.chat_history.append(("bot", bot_reply))

            # Display history
            for role, msg in st.session_state.chat_history:
                if role == "user":
                    st.chat_message("user").write(msg)
                else:
                    st.chat_message("assistant").write(msg)

        # -------------------
        # Quiz UI
        # -------------------
        with col2:
            st.subheader("📝 Quiz")

            if "quiz" in st.session_state:

                for idx, q in enumerate(st.session_state.quiz):
                    st.markdown(f"### Q{idx+1}. {q['question']}")
                    st.session_state.answers[idx] = st.radio(
                        "Choose:", q["options"], key=f"q{idx}"
                    )

                if st.button("Submit Answers"):
                    score = 0

                    for i, q in enumerate(st.session_state.quiz):
                        if st.session_state.answers.get(i) == q["answer"]:
                            score += 1
                            st.success(f"Q{i+1}: ✔ Correct")
                        else:
                            st.error(f"Q{i+1}: ❌ Wrong")

                        st.info("Explanation: " + q["explanation"])

                    st.write(f"## 🎯 Score: {score}/{len(st.session_state.quiz)}")

                    # Save score INCLUDING topic
                    save_score(
                        st.session_state["user_id"],
                        st.session_state["quiz_topic"],   # SUBJECT
                        score,
                        len(st.session_state.quiz),
                        str(datetime.now().date())
                    )

    # -----------------------------
    # PROGRESS PAGE
    # -----------------------------
    elif page == "Progress":
        st.header("📊 Your Progress")

        scores = get_scores(st.session_state["user_id"])

        if scores:

            df = pd.DataFrame(scores, columns=["Topic", "Score", "Total", "Date"])

            # ---------------- FILTER BY SUBJECT ----------------
            all_topics = df["Topic"].unique()
            selected_topic = st.selectbox("Select Topic:", all_topics)

            df_topic = df[df["Topic"] == selected_topic]

            st.subheader("📑 Scoreboard")
            st.dataframe(df_topic)

            # Plot graph
            st.subheader(f"📈 Performance Graph – {selected_topic}")
            df_topic["Percentage"] = df_topic["Score"] / df_topic["Total"] * 100
            df_topic["Date"] = pd.to_datetime(df_topic["Date"])

            st.line_chart(df_topic.set_index("Date")["Percentage"])
        else:
            st.info("No quiz scores yet.")

else:
    st.info("Please login to access the app.")
