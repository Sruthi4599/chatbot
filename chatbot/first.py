import streamlit as st
import google.generativeai as genai

# Configure API Key
API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "score" not in st.session_state:
    st.session_state.score = 0
if "language_selected" not in st.session_state:
    st.session_state.language_selected = None

st.title("🤖 CodeMate - Your AI Assistant")
st.write("Welcome! Ask me about programming languages, tutorials, or quizzes.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User Input
user_input = st.chat_input("Type a message...")

# Handle user input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    response = ""
    
    # Greeting Handling
    greetings = ["hi", "hello", "hey"]
    if any(greet in user_input.lower() for greet in greetings):
        response = "Hello! How can I assist you today?"

    # Detect Programming Language
    elif any(lang in user_input.lower() for lang in ["python", "java", "c++", "javascript"]):
        st.session_state.language_selected = next(
            lang for lang in ["Python", "Java", "C++", "JavaScript"] if lang.lower() in user_input.lower()
        )
        response = f"Do you want to learn {st.session_state.language_selected} or attempt a quiz?"

    # Learning Recommendations
    elif "learn" in user_input.lower() and st.session_state.language_selected:
        lang = st.session_state.language_selected
        response = f"Here are some resources for learning {lang}:"

        # YouTube Video Links
        youtube_links = {
            "Python": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "Java": "https://www.youtube.com/watch?v=eIrMbAQSU34",
            "C++": "https://www.youtube.com/watch?v=vLnPwxZdW4Y",
            "JavaScript": "https://www.youtube.com/watch?v=W6NZfCO5SIk"
        }
        response += f"\n📺 YouTube Video: [{lang} Tutorial]({youtube_links.get(lang, '#')})"

        # Website Links
        website_links = {
            "Python": "https://realpython.com/",
            "Java": "https://www.javatpoint.com/java-tutorial",
            "C++": "https://www.learncpp.com/",
            "JavaScript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"
        }
        response += f"\n🌐 Website: [{lang} Guide]({website_links.get(lang, '#')})"

        # Recommended Books
        books = {
            "Python": ["Python Crash Course", "Automate the Boring Stuff"],
            "Java": ["Effective Java", "Head First Java"],
            "C++": ["The C++ Programming Language", "Accelerated C++"],
            "JavaScript": ["Eloquent JavaScript", "You Don't Know JS"]
        }
        response += "\n📚 Books:\n- " + "\n- ".join(books.get(lang, []))

    # Quiz Handling
    elif "quiz" in user_input.lower() and st.session_state.language_selected:
        st.session_state.quiz_started = True
        st.session_state.quiz_answers = {}
        response = f"Starting {st.session_state.language_selected} quiz... Fetching questions!"

        # Generate quiz questions using Google Gemini API
        prompt = f"Generate 10 multiple-choice quiz questions for {st.session_state.language_selected} with 4 options and correct answers."
        result = model.generate_content(prompt)
        
        # Parse and store quiz questions
        questions = result.text.strip().split("\n\n")
        st.session_state.quiz_questions = []
        for q in questions:
            lines = q.split("\n")
            if len(lines) >= 6:
                question_text = lines[0]
                options = [lines[i][3:].strip() for i in range(1, 5)]
                answer = lines[5].split(":")[-1].strip()
                st.session_state.quiz_questions.append({
                    "question": question_text,
                    "options": options,
                    "answer": answer
                })
        
        if len(st.session_state.quiz_questions) < 10:
            response = "Sorry, couldn't fetch enough questions. Try again."

    # Display Quiz Questions
    elif st.session_state.quiz_started and not st.session_state.quiz_questions:
        response = "Quiz has started! Answer the following questions:"

    # Display Quiz in UI
    elif st.session_state.quiz_started:
        st.write("### Quiz Time! Choose the correct answers:")
        for i, q in enumerate(st.session_state.quiz_questions):
            st.session_state.quiz_answers[q["question"]] = st.radio(q["question"], q["options"], key=f"q{i}")

        if st.button("Submit Quiz"):
            st.session_state.score = sum(
                1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
            )
            st.session_state.quiz_started = False
            response = f"🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}"

    # Explanation Request
    elif "explain" in user_input.lower() and any(q["question"] in user_input for q in st.session_state.quiz_questions):
        for q in st.session_state.quiz_questions:
            if q["question"] in user_input:
                explanation_prompt = f"Explain the answer for: {q['question']}"
                explanation = model.generate_content(explanation_prompt).text.strip()
                response = f"🧐 Explanation: {explanation}"
                break

    # Store assistant response
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
