from google import genai

# ==============================
# YOUR GEMINI API KEY
# ==============================
API_KEY = "YOUR_API_KEY_HERE"
# Connect to Gemini
client = genai.Client(api_key=API_KEY)

# Create a conversation
chat = client.chats.create(
    model="gemini-3.6-flash"
)

print("=" * 50)
print("       🤖 NOTES ASSISTANT AI")
print("=" * 50)
print("Gemini is ready!")
print("Type 'exit' to close the program.")
print()

while True:
    try:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("AI: Goodbye! 👋")
            break

        response = chat.send_message(
            message=user_input
        )

        print("AI:", response.text)
        print()

    except Exception as e:
        print("❌ Error:", e)
        print()