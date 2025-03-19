import streamlit as st
import google.generativeai as genai

# Configure Google API
API_KEY = "YOUR_GOOGLE_API_KEY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferred_language" not in st.session_state:
    st.session_state.preferred_language = None
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_count" not in st.session_state:
    st.session_state.question_count = 10  # Default 10 questions

st.title("🤖 AI Learning Assistant")
st.write("Type your request in the chat below!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_input := st.chat_input("Type here..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Detect learning interest
    if "learn" in user_input.lower():
        for lang in ["Python", "Java", "C++", "JavaScript"]:
            if lang.lower() in user_input.lower():
                st.session_state.preferred_language = lang
                st.session_state.quiz_started = False
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.score = 0
                break
        
        if st.session_state.preferred_language:
            recommendations = {
                "Python": ["Python Crash Course", "Automate the Boring Stuff", "LeetCode Python Challenges", "Python Docs", "Python for Data Science"],
                "Java": ["Effective Java", "Head First Java", "Java Programming on GeeksforGeeks", "Java: The Complete Reference"],
                "C++": ["The C++ Programming Language", "Accelerated C++", "C++ Primer", "C++ STL Documentation"],
                "JavaScript": ["Eloquent JavaScript", "JavaScript: The Good Parts", "You Don't Know JS", "MDN JavaScript Guide"]
            }
            response_text = f"Here are some {st.session_state.preferred_language} learning resources:\n"
            response_text += "\n".join(f"- {rec}" for rec in recommendations[st.session_state.preferred_language])
        else:
            response_text = "I can recommend programming tutorials! Just type 'I want to learn Python' or another language."

    # Detect quiz request
    elif "quiz" in user_input.lower():
        if st.session_state.preferred_language:
            lang = st.session_state.preferred_language
            st.session_state.quiz_started = True
            st.session_state.score = 0

            quiz_data = {
                "Python": [
                    {"question": "What is the output of `print(2 ** 3)`?", "options": ["5", "6", "8", "10"], "answer": "8"},
                    {"question": "Which data type is mutable?", "options": ["Tuple", "String", "List", "Integer"], "answer": "List"},
                    {"question": "What is the default value of a variable in Python?", "options": ["None", "0", "Depends on type", "Not defined"], "answer": "Not defined"},
                    {"question": "Which loop is used to iterate over items in a list?", "options": ["for", "while", "do-while", "foreach"], "answer": "for"},
                    {"question": "What does `len([])` return?", "options": ["None", "0", "1", "Error"], "answer": "0"}
                ],
                "Java": [
                    {"question": "Which keyword is used to inherit a class?", "options": ["implements", "extends", "inherits", "super"], "answer": "extends"},
                    {"question": "What is the default value of an int variable?", "options": ["0", "null", "undefined", "1"], "answer": "0"}
                ],
                "C++": [
                    {"question": "Which operator is used for dynamic memory allocation?", "options": ["malloc", "new", "alloc", "create"], "answer": "new"},
                    {"question": "Which is the correct file extension for C++ programs?", "options": [".c", ".cpp", ".java", ".py"], "answer": ".cpp"}
                ],
                "JavaScript": [
                    {"question": "Which keyword is used to declare a constant?", "options": ["var", "let", "const", "static"], "answer": "const"},
                    {"question": "Which function converts a string to an integer?", "options": ["parseInt()", "toInteger()", "stringToInt()", "int()"], "answer": "parseInt()"}
                ]
            }

            st.session_state.quiz_questions = quiz_data.get(lang, [])[:st.session_state.question_count]
            st.session_state.quiz_answers = {q["question"]: "" for q in st.session_state.quiz_questions}
            response_text = f"Here is your {lang} quiz with {st.session_state.question_count} questions. Answer them below!"

        else:
            response_text = "Please specify a language before attempting a quiz! Example: 'I want to attempt Python quiz'."

    # Detect request for more questions
    elif "more questions" in user_input.lower():
        st.session_state.question_count += 5
        response_text = f"Okay! I'll now provide {st.session_state.question_count} questions in your quiz."

    else:
        response_text = model.generate_content(user_input).text

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Display Quiz
if st.session_state.quiz_started:
    st.write("### Quiz Time! Choose the correct answers:")
    
    for q in st.session_state.quiz_questions:
        selected_answer = st.radio(q["question"], q["options"], key=q["question"])
        st.session_state.quiz_answers[q["question"]] = selected_answer

    if st.button("Submit Quiz"):
        # Calculate score
        st.session_state.score = sum(
            1 for q in st.session_state.quiz_questions if st.session_state.quiz_answers[q["question"]] == q["answer"]
        )
        st.session_state.quiz_started = False
        response_text = f"🎉 Your Final Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}"
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    if st.button("More Questions"):
        st.session_state.question_count += 5
        st.session_state.quiz_started = False
