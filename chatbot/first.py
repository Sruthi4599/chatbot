import streamlit as st
import google.generativeai as genai

# API Configuration
API_KEY = "YOUR_GOOGLE_API_KEY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "score" not in st.session_state:
    st.session_state.score = 0

if "quiz_language" not in st.session_state:
    st.session_state.quiz_language = None

st.title("🤖 BookMate - Your AI Assistant")
st.write("Welcome! Ask me anything about programming or request a quiz.")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Say something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Detect greetings
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    if any(greet in prompt.lower() for greet in greetings):
        response_text = "Hello! How can I assist you today?"
    
    # Detect programming language request
    elif "learn" in prompt.lower():
        languages = ["Python", "Java", "C++", "JavaScript"]
        for lang in languages:
            if lang.lower() in prompt.lower():
                st.session_state.quiz_language = lang
                response_text = f"Great choice! Here are some {lang} resources:\n\n"
                response_text += f"📹 **YouTube Video**: [Learn {lang}](https://www.youtube.com/results?search_query=learn+{lang})\n"
                response_text += f"🌍 **Website**: [GeeksforGeeks {lang}](https://www.geeksforgeeks.org/{lang}/)\n"
                response_text += "📚 **Recommended Books:**\n"

                book_recommendations = {
                    "Python": ["Python Crash Course", "Automate the Boring Stuff", "Python Cookbook"],
                    "Java": ["Effective Java", "Head First Java", "Java: The Complete Reference"],
                    "C++": ["The C++ Programming Language", "Accelerated C++", "C++ Primer"],
                    "JavaScript": ["Eloquent JavaScript", "JavaScript: The Good Parts", "You Don't Know JS"]
                }

                for book in book_recommendations[lang]:
                    response_text += f"- {book}\n"
                break
        else:
            response_text = "I can recommend resources for Python, Java, C++, and JavaScript. Which language are you interested in?"

    # Detect quiz request
    elif "quiz" in prompt.lower():
        if st.session_state.quiz_language is None:
            response_text = "Please specify a programming language for the quiz. Example: 'I want to attempt a Python quiz.'"
        else:
            lang = st.session_state.quiz_language
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.score = 0

            # Sample Quiz Questions
            quiz_data = {
                "Python": [
                    {"question": "What is the output of `print(2 ** 3)`?", "options": ["5", "6", "8", "10"], "answer": "8"},
                    {"question": "Which data type is mutable?", "options": ["Tuple", "String", "List", "Integer"], "answer": "List"},
                    {"question": "What keyword is used to define a function?", "options": ["func", "def", "define", "function"], "answer": "def"},
                    {"question": "Which module is used for regular expressions in Python?", "options": ["regex", "re", "match", "reg"], "answer": "re"},
                    {"question": "What is the index of the first element in a Python list?", "options": ["1", "0", "-1", "None"], "answer": "0"},
                    {"question": "Which loop is used to iterate over a sequence?", "options": ["for", "while", "do-while", "repeat"], "answer": "for"},
                    {"question": "What is the correct file extension for Python files?", "options": [".py", ".python", ".pt", ".p"], "answer": ".py"},
                    {"question": "What is the output of `print(type([]))`?", "options": ["dict", "list", "tuple", "set"], "answer": "list"},
                    {"question": "Which keyword is used to handle exceptions in Python?", "options": ["catch", "handle", "try", "except"], "answer": "try"},
                    {"question": "How do you start a comment in Python?", "options": ["//", "/*", "#", "--"], "answer": "#"}
                ]
            }

            st.session_state.quiz_questions = quiz_data.get(lang, [])[:10]  # Default 10 questions
            st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}
            response_text = f"Starting {lang} quiz! Please answer the following questions."

    # Handle regular conversation with AI
    else:
        response = st.session_state.chat.send_message(prompt)
        response_text = response.text

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

# Display Quiz if started
if st.session_state.quiz_started and not st.session_state.quiz_completed:
    st.write("### Quiz Time! Choose the correct answers:")
    
    for q in st.session_state.quiz_questions:
        selected_answer = st.radio(q["question"], q["options"], key=q["question"])
        st.session_state.quiz_answers[q["question"]] = selected_answer

    if st.button("Submit Quiz"):
        # Calculate Score
        st.session_state.score = sum(
            1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
        )
        st.session_state.quiz_completed = True

# Display Final Score
if st.session_state.quiz_completed:
    st.write(f"### 🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}")
    if st.button("Retry Quiz"):
        st.session_state.quiz_started = False
        st.session_state.quiz_completed = False
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.score = 0
