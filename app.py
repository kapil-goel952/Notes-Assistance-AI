import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai

import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
# =========================
# CONFIGURATION
# =========================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

if not FIREBASE_API_KEY:
    st.error("❌ Firebase API key not found.")
    st.stop()


# Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "notes-assistant-ai-firebase-adminsdk-fbsvc-fc69cf4ed2.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()
if not API_KEY:
    st.error("❌ Gemini API key not found. Check your .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

NOTES_FILE = "notes.json"


# =========================
# NOTES FUNCTIONS
# =========================

def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4, ensure_ascii=False)


# =========================
# AI FUNCTION
# =========================

def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"❌ Gemini Error: {e}"


# =========================
# PAGE
# =========================

st.set_page_config(
    page_title="Notes Assistant AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Notes Assistant AI")
st.caption("Your notes + Gemini AI = smarter learning")


# =========================
# SIDEBAR
# =========================

st.sidebar.title("📚 Notes Assistant")

option = st.sidebar.radio(
    "Choose an option",
    [
        "📝 Add Note",
        "📖 View Notes",
        "🔎 Search Notes",
        "🧠 Ask AI About Notes",
        "🤖 Chat with AI"
    ]
)


notes = load_notes()


# =========================
# ADD NOTE
# =========================

if option == "📝 Add Note":

    st.header("📝 Add a New Note")

    title = st.text_input("Note Title")

    content = st.text_area(
        "Note Content",
        height=200
    )

    if st.button("💾 Save Note"):

        if not title.strip() or not content.strip():
            st.warning("Please enter both title and content.")

        else:

            new_note = {
                "title": title,
                "content": content
            }

            notes.append(new_note)
            save_notes(notes)

            st.success("✅ Note saved successfully!")


# =========================
# VIEW NOTES
# =========================

elif option == "📖 View Notes":

    st.header("📖 Your Notes")

    if not notes:

        st.info("No notes found.")

    else:

        for i, note in enumerate(notes, start=1):

            with st.expander(
                f"{i}. {note['title']}"
            ):

                st.write(note["content"])


# =========================
# SEARCH NOTES
# =========================

elif option == "🔎 Search Notes":

    st.header("🔎 Search Your Notes")

    keyword = st.text_input(
        "Search keyword"
    )

    if keyword.strip():

        keyword = keyword.lower()

        results = []

        for note in notes:

            if (
                keyword in note["title"].lower()
                or
                keyword in note["content"].lower()
            ):
                results.append(note)

        if results:

            for note in results:

                st.subheader(note["title"])
                st.write(note["content"])

        else:

            st.warning("No matching notes found.")


# =========================
# ASK AI ABOUT NOTES
# =========================

elif option == "🧠 Ask AI About Notes":

    st.header("🧠 Ask Gemini About Your Notes")

    st.write(
        "Ask questions, find mistakes, explain concepts, "
        "or revise your notes using AI."
    )

    question = st.text_area(
        "Your question",
        placeholder="Example: Find mistakes in my Linux notes."
    )

    if st.button("✨ Ask AI"):

        if not notes:

            st.warning("You don't have any notes yet.")

        elif not question.strip():

            st.warning("Please enter a question.")

        else:

            notes_text = "\n\n".join(
                [
                    f"Title: {note['title']}\n"
                    f"Content: {note['content']}"
                    for note in notes
                ]
            )

            prompt = f"""
You are Notes Assistant AI.

Answer the user's question using their saved notes.

USER NOTES:
{notes_text}

USER QUESTION:
{question}

Give a clear and helpful answer.
If the notes contain an error, point it out clearly.
"""

            with st.spinner("🤖 Gemini is thinking..."):

                answer = ask_gemini(prompt)

            # Store AI response temporarily
            st.session_state["ai_answer"] = answer
            st.session_state["ai_question"] = question


    # =========================
    # SHOW AI RESPONSE
    # =========================

    if "ai_answer" in st.session_state:

        st.subheader("💡 AI Response")

        st.write(st.session_state["ai_answer"])


        # =========================
        # SAVE AI RESPONSE
        # =========================

        st.divider()

        st.subheader("💾 Save AI Response")

        save_title = st.text_input(
            "Note Title",
            value=f"AI Answer - {st.session_state['ai_question']}"
        )

        if st.button("💾 Save to Notes"):

            if not save_title.strip():

                st.warning("Please enter a note title.")

            else:

                new_note = {
                    "title": save_title,
                    "content": st.session_state["ai_answer"]
                }

                notes.append(new_note)

                save_notes(notes)

                st.success("✅ AI response saved to your notes!")

                # Remove temporary response after saving
                st.session_state.pop("ai_answer", None)
                st.session_state.pop("ai_question", None)


# =========================
# NORMAL AI CHAT
# =========================

elif option == "🤖 Chat with AI":

    st.header("🤖 Chat with Gemini")

    question = st.text_area(
        "Ask anything",
        placeholder="Ask Gemini something..."
    )

    if st.button("🚀 Send"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("🤖 Gemini is thinking..."):

                answer = ask_gemini(question)

            st.subheader("AI Response")
            st.write(answer)
    # =========================
# LOGIN SYSTEM
# =========================

if "user" not in st.session_state:
    st.session_state.user = None


if st.session_state.user is None:

    st.title("🤖 Notes Assistant AI")

    st.subheader("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(["Login", "Create Account"])

    # LOGIN
    with tab1:

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("🔑 Login"):

            if not login_email or not login_password:

                st.warning("Please enter email and password.")

            else:

                result = firebase_login(
                    login_email,
                    login_password
                )

                if "idToken" in result:

                    decoded_token = verify_firebase_token(
                        result["idToken"]
                    )

                    if decoded_token:

                        st.session_state.user = decoded_token

                        st.success("✅ Login successful!")

                        st.rerun()

                    else:

                        st.error("❌ Could not verify Firebase token.")

                else:

                    st.error(
                        result.get(
                            "error",
                            {}
                        ).get(
                            "message",
                            "Login failed."
                        )
                    )

    # SIGN UP
    with tab2:

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("📝 Create Account"):

            if not signup_email or not signup_password:

                st.warning(
                    "Please enter email and password."
                )

            else:

                result = firebase_signup(
                    signup_email,
                    signup_password
                )

                if "idToken" in result:

                    st.success(
                        "✅ Account created! Please login."
                    )

                else:

                    st.error(
                        result.get(
                            "error",
                            {}
                        ).get(
                            "message",
                            "Signup failed."
                        )
                    )

    st.stop()