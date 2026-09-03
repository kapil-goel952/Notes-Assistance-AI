import os
import json
import requests
import streamlit as st

from dotenv import load_dotenv
from google import genai

import firebase_admin
from firebase_admin import credentials, firestore, auth


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# Check Gemini API key
if not API_KEY:
    st.error("❌ Gemini API key not found. Check your .env file.")
    st.stop()

# Check Firebase API key
if not FIREBASE_API_KEY:
    st.error("❌ Firebase API key not found. Check your .env file.")
    st.stop()


# =========================================================
# FIREBASE ADMIN SDK
# =========================================================

if not firebase_admin._apps:

    cred = credentials.Certificate(
        "notes-assistant-ai-firebase-adminsdk-fbsvc-fc69cf4ed2.json"
    )

    firebase_admin.initialize_app(cred)


db = firestore.client()


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=API_KEY
)


# =========================================================
# FILE CONFIGURATION
# =========================================================

NOTES_FILE = "notes.json"


# =========================================================
# FIREBASE AUTH FUNCTIONS
# =========================================================

def firebase_login(email, password):

    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    )

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        return response.json()

    except requests.exceptions.RequestException as e:

        return {
            "error": {
                "message": str(e)
            }
        }


def firebase_signup(email, password):

    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signUp?key={FIREBASE_API_KEY}"
    )

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        return response.json()

    except requests.exceptions.RequestException as e:

        return {
            "error": {
                "message": str(e)
            }
        }


def verify_firebase_token(id_token):

    try:

        decoded_token = auth.verify_id_token(
            id_token
        )

        return decoded_token

    except Exception:

        return None


# =========================================================
# FIRESTORE NOTES FUNCTIONS
# =========================================================

def get_user_notes_document():

    user = st.session_state.get("user")

    if not user:
        return None

    uid = user.get("uid")

    if not uid:
        return None

    return (
        db.collection("users")
        .document(uid)
        .collection("data")
        .document("notes")
    )


def load_notes():

    notes_document = get_user_notes_document()

    if notes_document is None:
        return []

    try:

        document = notes_document.get()

        if document.exists:

            data = document.to_dict()

            return data.get("notes", [])

        return []

    except Exception as e:

        st.error(
            f"❌ Could not load notes: {e}"
        )

        return []


def save_notes(notes):

    notes_document = get_user_notes_document()

    if notes_document is None:
        return

    try:

        notes_document.set(
            {
                "notes": notes
            }
        )

    except Exception as e:

        st.error(
            f"❌ Could not save notes: {e}"
        )
# =========================================================
# GEMINI AI FUNCTION
# =========================================================

def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return f"❌ Gemini Error: {e}"


# =========================================================
# STREAMLIT PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Notes Assistant AI",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "user" not in st.session_state:

    st.session_state.user = None


# =========================================================
# LOGIN / SIGNUP PAGE
# =========================================================

if st.session_state.user is None:

    st.title("🤖 Notes Assistant AI")

    st.caption(
        "Your notes + Gemini AI = smarter learning"
    )

    st.divider()

    st.subheader("🔐 Login / Sign Up")

    tab1, tab2 = st.tabs(
        [
            "🔑 Login",
            "📝 Create Account"
        ]
    )


    # =====================================================
    # LOGIN
    # =====================================================

    with tab1:

        st.write("Login to continue.")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )


        if st.button(
            "🔑 Login",
            use_container_width=True
        ):

            if (
                not login_email.strip()
                or
                not login_password
            ):

                st.warning(
                    "⚠️ Please enter email and password."
                )

            else:

                with st.spinner(
                    "🔐 Logging in..."
                ):

                    result = firebase_login(
                        login_email.strip(),
                        login_password
                    )


                if "idToken" in result:

                    decoded_token = verify_firebase_token(
                        result["idToken"]
                    )


                    if decoded_token:

                        st.session_state.user = decoded_token

                        st.success(
                            "✅ Login successful!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Could not verify Firebase token."
                        )

                else:

                    error_message = (
                        result
                        .get("error", {})
                        .get(
                            "message",
                            "Login failed."
                        )
                    )

                    # Make Firebase errors easier to understand
                    if error_message == "INVALID_LOGIN_CREDENTIALS":
                        error_message = (
                            "Invalid email or password."
                        )

                    elif error_message == "EMAIL_NOT_FOUND":
                        error_message = (
                            "No account found with this email."
                        )

                    elif error_message == "INVALID_PASSWORD":
                        error_message = (
                            "Incorrect password."
                        )

                    elif error_message == "USER_DISABLED":
                        error_message = (
                            "This account has been disabled."
                        )

                    st.error(
                        f"❌ {error_message}"
                    )


    # =====================================================
    # SIGN UP
    # =====================================================

    with tab2:

        st.write(
            "Create a new Notes Assistant AI account."
        )

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        signup_confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm_password"
        )


        if st.button(
            "📝 Create Account",
            use_container_width=True
        ):

            if (
                not signup_email.strip()
                or
                not signup_password
                or
                not signup_confirm_password
            ):

                st.warning(
                    "⚠️ Please fill all fields."
                )

            elif signup_password != signup_confirm_password:

                st.error(
                    "❌ Passwords do not match."
                )

            elif len(signup_password) < 6:

                st.error(
                    "❌ Password must be at least 6 characters."
                )

            else:

                with st.spinner(
                    "📝 Creating account..."
                ):

                    result = firebase_signup(
                        signup_email.strip(),
                        signup_password
                    )


                if "idToken" in result:

                    st.success(
                        "✅ Account created successfully!"
                    )

                    st.info(
                        "Now go to the Login tab and login."
                    )

                else:

                    error_message = (
                        result
                        .get("error", {})
                        .get(
                            "message",
                            "Signup failed."
                        )
                    )


                    if error_message == "EMAIL_EXISTS":

                        error_message = (
                            "An account with this email already exists."
                        )

                    elif error_message == "INVALID_EMAIL":

                        error_message = (
                            "Please enter a valid email address."
                        )

                    elif error_message == "WEAK_PASSWORD":

                        error_message = (
                            "Password is too weak."
                        )


                    st.error(
                        f"❌ {error_message}"
                    )


    # IMPORTANT:
    # Stop the rest of the application
    # until the user logs in.

    st.stop()


# =========================================================
# USER IS LOGGED IN
# =========================================================

user = st.session_state.user

user_email = user.get(
    "email",
    "User"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "📚 Notes Assistant"
)

st.sidebar.success(
    f"👤 {user_email}"
)

st.sidebar.divider()


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


st.sidebar.divider()


# =========================================================
# LOGOUT
# =========================================================

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.user = None

    st.session_state.pop(
        "ai_answer",
        None
    )

    st.session_state.pop(
        "ai_question",
        None
    )

    st.rerun()


# =========================================================
# LOAD NOTES
# =========================================================

notes = load_notes()


# =========================================================
# MAIN PAGE HEADER
# =========================================================

st.title(
    "🤖 Notes Assistant AI"
)

st.caption(
    "Your notes + Gemini AI = smarter learning"
)


# =========================================================
# ADD NOTE
# =========================================================

if option == "📝 Add Note":

    st.header(
        "📝 Add a New Note"
    )

    title = st.text_input(
        "Note Title",
        placeholder="Example: Python Functions"
    )

    content = st.text_area(
        "Note Content",
        height=200,
        placeholder="Write your notes here..."
    )


    if st.button(
        "💾 Save Note",
        use_container_width=True
    ):

        if (
            not title.strip()
            or
            not content.strip()
        ):

            st.warning(
                "⚠️ Please enter both title and content."
            )

        else:

            new_note = {
                "title": title.strip(),
                "content": content.strip()
            }

            notes.append(
                new_note
            )

            save_notes(
                notes
            )

            st.success(
                "✅ Note saved successfully!"
            )


# =========================================================
# VIEW NOTES
# =========================================================

elif option == "📖 View Notes":

    st.header("📖 Your Notes")

    if not notes:

        st.info("📭 No notes found. Add your first note!")

    else:

        st.write(f"Total Notes: **{len(notes)}**")

        for i, note in enumerate(notes):

            title = note.get(
                "title",
                "Untitled Note"
            )

            content = note.get(
                "content",
                ""
            )

            with st.expander(
                f"{i + 1}. {title}"
            ):

                # =========================================
                # EDIT NOTE
                # =========================================

                st.subheader("✏️ Edit Note")

                edited_title = st.text_input(
                    "Note Title",
                    value=title,
                    key=f"edit_title_{i}"
                )

                edited_content = st.text_area(
                    "Note Content",
                    value=content,
                    height=200,
                    key=f"edit_content_{i}"
                )

                col1, col2 = st.columns(2)

                # =========================================
                # UPDATE BUTTON
                # =========================================

                with col1:

                    if st.button(
                        "💾 Update Note",
                        key=f"update_{i}",
                        use_container_width=True
                    ):

                        if (
                            not edited_title.strip()
                            or
                            not edited_content.strip()
                        ):

                            st.warning(
                                "⚠️ Title and content cannot be empty."
                            )

                        else:

                            notes[i]["title"] = (
                                edited_title.strip()
                            )

                            notes[i]["content"] = (
                                edited_content.strip()
                            )

                            save_notes(notes)

                            st.success(
                                "✅ Note updated successfully!"
                            )

                            st.rerun()

                # =========================================
                # DELETE BUTTON
                # =========================================

                with col2:

                    if st.button(
                        "🗑️ Delete Note",
                        key=f"delete_{i}",
                        use_container_width=True
                    ):

                        notes.pop(i)

                        save_notes(notes)

                        st.success(
                            "✅ Note deleted successfully!"
                        )

                        st.rerun()
# =========================================================
# SEARCH NOTES
# =========================================================

elif option == "🔎 Search Notes":

    st.header(
        "🔎 Search Your Notes"
    )

    keyword = st.text_input(
        "Search keyword",
        placeholder="Example: Python"
    )


    if keyword.strip():

        search_keyword = keyword.lower()

        results = []


        for note in notes:

            title = note.get(
                "title",
                ""
            )

            content = note.get(
                "content",
                ""
            )


            if (
                search_keyword in title.lower()
                or
                search_keyword in content.lower()
            ):

                results.append(
                    note
                )


        if results:

            st.success(
                f"✅ Found {len(results)} matching note(s)."
            )


            for note in results:

                st.subheader(
                    note.get(
                        "title",
                        "Untitled Note"
                    )
                )

                st.write(
                    note.get(
                        "content",
                        ""
                    )
                )

                st.divider()


        else:

            st.warning(
                "❌ No matching notes found."
            )


# =========================================================
# ASK AI ABOUT NOTES
# =========================================================

elif option == "🧠 Ask AI About Notes":

    st.header(
        "🧠 Ask Gemini About Your Notes"
    )

    st.write(
        "Ask questions, find mistakes, explain concepts, "
        "or revise your notes using AI."
    )


    if not notes:

        st.info(
            "📭 You don't have any notes yet. "
            "Add some notes first."
        )

    else:

        question = st.text_area(
            "Your question",
            placeholder=(
                "Example: Find mistakes in my Linux notes."
            ),
            height=120
        )


        if st.button(
            "✨ Ask AI",
            use_container_width=True
        ):

            if not question.strip():

                st.warning(
                    "⚠️ Please enter a question."
                )

            else:

                notes_text = "\n\n".join(
                    [
                        f"Title: {note.get('title', '')}\n"
                        f"Content: {note.get('content', '')}"
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

Instructions:

1. Use the user's notes as the main source.
2. Give a clear and helpful answer.
3. If the notes contain an error, point it out clearly.
4. Explain difficult concepts in simple language.
5. If the answer cannot be found in the notes, clearly say that.
6. Do not invent information that is not supported by the notes.
"""


                with st.spinner(
                    "🤖 Gemini is thinking..."
                ):

                    answer = ask_gemini(
                        prompt
                    )


                st.session_state[
                    "ai_answer"
                ] = answer

                st.session_state[
                    "ai_question"
                ] = question


        # =================================================
        # SHOW AI RESPONSE
        # =================================================

        if "ai_answer" in st.session_state:

            st.divider()

            st.subheader(
                "💡 AI Response"
            )

            st.write(
                st.session_state[
                    "ai_answer"
                ]
            )


            # =============================================
            # SAVE AI RESPONSE
            # =============================================

            st.divider()

            st.subheader(
                "💾 Save AI Response"
            )


            default_title = (
                "AI Answer - "
                +
                st.session_state.get(
                    "ai_question",
                    "AI Response"
                )
            )


            save_title = st.text_input(
                "Note Title",
                value=default_title,
                key="save_ai_title"
            )


            if st.button(
                "💾 Save to Notes",
                use_container_width=True
            ):

                if not save_title.strip():

                    st.warning(
                        "⚠️ Please enter a note title."
                    )

                else:

                    new_note = {
                        "title": save_title.strip(),
                        "content": st.session_state[
                            "ai_answer"
                        ]
                    }


                    notes.append(
                        new_note
                    )

                    save_notes(
                        notes
                    )


                    st.success(
                        "✅ AI response saved to your notes!"
                    )


                    # Remove temporary AI response
                    st.session_state.pop(
                        "ai_answer",
                        None
                    )

                    st.session_state.pop(
                        "ai_question",
                        None
                    )

# =========================================================
# MULTI-TURN AI CHAT
# =========================================================

elif option == "🤖 Chat with AI":

    st.header("🤖 Chat with Gemini")

    st.write(
        "Have a conversation with Gemini. "
        "The AI remembers the current chat."
    )

    # Create chat history
    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []


    # =========================================
    # DISPLAY CHAT HISTORY
    # =========================================

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # =========================================
    # USER INPUT
    # =========================================

    user_message = st.chat_input(
        "Ask Gemini something..."
    )


    if user_message:

        # Add user message
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_message
            }
        )


        # Show user message
        with st.chat_message("user"):

            st.write(user_message)


        # Build conversation for Gemini
        conversation = ""

        for message in st.session_state.chat_history:

            if message["role"] == "user":

                conversation += (
                    f"User: {message['content']}\n"
                )

            else:

                conversation += (
                    f"Assistant: {message['content']}\n"
                )


        prompt = f"""
You are Notes Assistant AI.

Have a helpful, natural conversation with the user.

Remember the previous conversation and use it
to understand follow-up questions.

CONVERSATION:
{conversation}

Respond to the user's latest message clearly
and helpfully.
"""
        # =========================================
        # GET GEMINI RESPONSE
        # =========================================
        with st.chat_message("assistant"):
            with st.spinner(
                "🤖 Gemini is thinking..."
            ):
                answer = ask_gemini(prompt)
            st.write(answer)
        # Save AI response
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
    # =========================================
    # CLEAR CHAT
    # =========================================
    if st.session_state.chat_history:
        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True
        ):
            st.session_state.chat_history = []
            st.rerun()