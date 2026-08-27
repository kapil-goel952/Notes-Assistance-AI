import json
from google import genai

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
        print("6. 🚪 Exit")

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
            print("\nAI: Goodbye! 👋")
            break

        else:
            print("❌ Invalid choice.")


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":
    main()