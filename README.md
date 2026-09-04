# 🤖 Notes Assistant AI

> An AI-powered note-taking and learning assistant built with **Python, Streamlit, Firebase, Firestore, and Google Gemini API**.

Notes Assistant AI is a web-based AI productivity and learning application that allows users to create, manage, search, edit, and delete their notes while interacting with Google's Gemini AI.

The application combines **secure user authentication, cloud-based note storage, and AI-powered assistance** into a single workflow.

---

## 🚀 Live Demo

🌐 **Live App:**  
https://notes-assistance-ai.streamlit.app/

The application can be opened directly in a browser.

---

## ✨ Features

### 🔐 User Authentication

Users can create an account and securely log in using **Firebase Authentication**.

Each user's notes are associated with their unique Firebase user ID.

---

### 📝 Add Notes

Create and save notes directly from the application.

Each note contains:

- Note title
- Note content

Notes are stored in **Cloud Firestore**.

---

### 📖 View Notes

View all saved notes in an organized interface.

Users can expand notes to read their complete content.

---

### 🔎 Search Notes

Search through saved notes using keywords.

The search checks both:

- Note titles
- Note content

This makes it easier to quickly find specific information.

---

### ✏️ Edit Notes

Existing notes can be edited directly from the application.

Users can update:

- Note title
- Note content

The updated note is then saved back to Firestore.

---

### 🗑️ Delete Notes

Users can delete notes they no longer need.

The selected note is removed from the user's Firestore data.

---

### 🧠 Ask AI About Notes

This is one of the core AI features of the project.

Users can ask Gemini questions based specifically on their saved notes.

For example:

> "Find mistakes in my Linux notes."

The application provides the user's notes as context to Gemini and generates a response based on the available information.

The AI can be used to:

- Explain concepts
- Find mistakes
- Clarify confusing topics
- Revise notes
- Answer questions
- Improve understanding of study material

---

### 💾 Save AI Responses

