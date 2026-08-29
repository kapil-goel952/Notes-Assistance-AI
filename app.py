import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai

# =========================
# CONFIGURATION
# =========================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

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
    except:
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

        if not title or not content:
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

    if keyword:

        results = []

        for note in notes:

            if (
                keyword.lower() in note["title"].lower()
                or
                keyword.lower() in note["content"].lower()
            ):
                results.append(note)

        if results:

            for note in results:

                st.subheader(note["title"])
                st.write(note["content"])

        else:

            st.warning("No matching notes found.")
# # =========================
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

        elif not question:

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
                del st.session_state["ai_answer"]
                del st.session_state["ai_question"]

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
                del st.session_state["ai_answer"]
                del st.session_state["ai_question"]

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

        if not question:

            st.warning("Please enter a question.")

        else:

            with st.spinner("🤖 Gemini is thinking..."):

                answer = ask_gemini(question)

            st.subheader("AI Response")
            st.write(answer)
            # asgsd