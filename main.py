import json
from google import genai
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY not found!")
    print("Please create a .env file and add your API key.")
    exit()

client = genai.Client(api_key=API_KEY)
# ==========================================
# GEMINI API
# ==========================================

API_KEY = "YOUR_API_KEY_HERE"

client = genai.Client(api_key=API_KEY)

chat = client.chats.create(
    model="gemini-3.6-flash"
)

# ==========================================
# NOTES FILE
# ==========================================

NOTES_FILE = "notes.json"


# ==========================================
# LOAD NOTES
# ==========================================

def load_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ==========================================
# SAVE NOTES
# ==========================================

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(
            notes,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# ADD NOTE
# ==========================================

def add_note():

    print("\n========== ADD NOTE ==========")

    title = input("Title: ").strip()
    content = input("Content: ").strip()

    if not title or not content:
        print("❌ Title and content cannot be empty.")
        return

    notes = load_notes()

    note = {
        "title": title,
        "content": content
    }

    notes.append(note)

    save_notes(notes)

    print("✅ Note saved successfully!")


# ==========================================
# VIEW NOTES
# ==========================================

def view_notes():

    notes = load_notes()

    print("\n========== YOUR NOTES ==========")

    if not notes:
        print("📭 No notes found.")
        return

    for index, note in enumerate(notes, start=1):

        print(f"\n{index}. {note['title']}")
        print(f"   {note['content']}")

    print("\n================================")


# ==========================================
# DELETE NOTE
# ==========================================

def delete_note():

    notes = load_notes()

    if not notes:
        print("\n📭 No notes available.")
        return

    view_notes()

    try:
        number = int(input("\nEnter note number to delete: "))

        if number < 1 or number > len(notes):
            print("❌ Invalid note number.")
            return

        deleted_note = notes.pop(number - 1)

        save_notes(notes)

        print(
            f"🗑️ Deleted: {deleted_note['title']}"
        )

    except ValueError:
        print("❌ Please enter a valid number.")


# ==========================================
# SEARCH NOTES
# ==========================================

def search_notes():

    notes = load_notes()

    if not notes:
        print("\n📭 No notes available.")
        return

    keyword = input(
        "\nSearch keyword: "
    ).strip().lower()

    if not keyword:
        return

    results = []

    for note in notes:

        if (
            keyword in note["title"].lower()
            or keyword in note["content"].lower()
        ):
            results.append(note)

    print("\n========== SEARCH RESULTS ==========")

    if not results:
        print("❌ No matching notes found.")
        return

    for index, note in enumerate(results, start=1):

        print(f"\n{index}. {note['title']}")
        print(f"   {note['content']}")


# ==========================================
# CHAT WITH GEMINI
# ==========================================

def chat_with_ai():

    print("\n========== AI CHAT ==========")
    print("Type 'back' to return to the menu.")

    while True:

        user_input = input("\nYou: ").strip()

        if user_input.lower() == "back":
            break

        if not user_input:
            continue

        try:

            response = chat.send_message(
                message=user_input
            )

            print("\nAI:", response.text)

        except Exception as error:

            print("\n❌ Gemini Error:")
            print(error)

# ==========================================
# ASK AI ABOUT NOTES
# ==========================================

def ask_ai_about_notes():

    notes = load_notes()

    if not notes:
        print("\n📭 You don't have any notes yet.")
        return

    print("\n========== ASK AI ABOUT YOUR NOTES ==========")
    print("Ask anything related to your saved notes.")
    print("Type 'back' to return to the menu.")

    # Prepare notes as context for Gemini
    notes_context = ""

    for index, note in enumerate(notes, start=1):
        notes_context += f"""
            Note {index}:
            Title: {note['title']}
            Content: {note['content']}
            -------------------------
        """

    while True:

        question = input("\nYou: ").strip()

        if question.lower() == "back":
            break

        if not question:
            continue

        prompt = f"""
                You are a helpful Notes Assistant AI.

                Answer the user's question using the notes provided below.

                IMPORTANT:
                - Prefer information from the user's notes.
                - If the answer is not present in the notes, clearly say that
                the information is not available in the saved notes.
                - You can explain the concept in a simple way.
                - Do not pretend that something is in the notes if it isn't.

                USER'S NOTES:
                {notes_context}

                USER'S QUESTION:
                {question}
            """

        try:

            response = chat.send_message(
                message=prompt
            )

            print("\nAI:", response.text)

        except Exception as error:

            print("\n❌ Gemini Error:")
            print(error)
            
            
# ==========================================
# SUMMARIZE A NOTE
# ==========================================

def summarize_note():

    notes = load_notes()

    if not notes:
        print("\n📭 You don't have any notes yet.")
        return

    print("\n========== SUMMARIZE NOTE ==========")

    for index, note in enumerate(notes, start=1):
        print(f"{index}. {note['title']}")

    try:
        number = int(input("\nEnter note number to summarize: "))

        if number < 1 or number > len(notes):
            print("❌ Invalid note number.")
            return

        selected_note = notes[number - 1]

        prompt = f"""
You are a helpful study assistant.

Summarize the following student's note.

Give the response in this format:

SUMMARY:
- Short and clear summary

KEY POINTS:
- Important point 1
- Important point 2
- Important point 3

IMPORTANT TERMS:
- Important term 1
- Important term 2

NOTE TITLE:
{selected_note['title']}

NOTE CONTENT:
{selected_note['content']}
"""

        print("\n⏳ Generating summary...")

        response = chat.send_message(
            message=prompt
        )

        print("\n========== AI SUMMARY ==========")
        print(response.text)
        print("================================")

    except ValueError:
        print("❌ Please enter a valid number.")

    except Exception as error:
        print("\n❌ Gemini Error:")
        print(error)
# ==========================================
# MAIN MENU
# ==========================================

def main():

    print("=" * 50)
    print("        🤖 NOTES ASSISTANT AI")
    print("=" * 50)

    while True:

        print("\nChoose an option:")

        print("1. 📝 Add Note")
        print("2. 📖 View Notes")
        print("3. 🗑️ Delete Note")
        print("4. 🔎 Search Notes")
        print("5. 🤖 Chat with AI")
        print("6. 🧠 Ask AI About Notes")
        print("7. ✨ Summarize a Note")
        print("8. 🚪 Exit")
        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            add_note()

        elif choice == "2":
            view_notes()

        elif choice == "3":
            delete_note()

        elif choice == "4":
            search_notes()

        elif choice == "5":
            chat_with_ai()

        elif choice == "6":
            ask_ai_about_notes()

        elif choice == "7":
            summarize_note()

        elif choice == "8":
            print("\nAI: Goodbye! 👋")
            break

        else:
            print("❌ Invalid choice.")



# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    main()