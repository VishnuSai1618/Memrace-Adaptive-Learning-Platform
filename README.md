# MEMRACE – AI-Powered Adaptive Learning Platform

<p align="center">
  <a href="https://memrace-adaptive-learning-platform.onrender.com/" target="_blank">
    <img src="https://img.shields.io/badge/🚀%20Live%20Demo-View%20Project-blue?style=for-the-badge&logo=google-chrome&logoColor=white" />
  </a>
</p>

> 🚀 Try the live application instantly without setup


MEMRACE is an intelligent web-based learning platform that helps students study more effectively using **AI-generated flashcards, quizzes, and real-time live quiz sessions**.

The system adapts to a student's performance and dynamically adjusts the learning experience to improve knowledge retention.

MEMRACE combines the strengths of:

* Flashcard learning systems like **Anki**
* Interactive quiz platforms like **Kahoot**
* AI-powered content generation using **Gemini**

to create a **smart, personalized learning environment**.

---

# Project Overview

MEMRACE allows users to upload study material and automatically generate learning content such as flashcards and quizzes using Artificial Intelligence.

The platform also includes **real-time multiplayer live quizzes** where students can compete with each other across interactive websockets.

The goal of the project is to **make studying interactive, adaptive, and engaging**.

---

# Key Features

### AI Content Generation
* Automatically generate **flashcards and quiz questions** from uploaded study material
* Supports **text and PDF inputs**
* Uses Google Gemini AI to extract important concepts and key points

### Flashcard Learning System
* Study using flashcards
* Track learning progress
* Uses the **SM-2 spaced repetition algorithm** for better retention

### Quiz System
* Multiple choice quizzes generated from study material
* Tracks accuracy and performance
* Stores quiz attempts and analytics

### Live Quiz (Multiplayer)
* Host real-time quiz sessions natively inside the browser via WebSockets
* Players join using a **PIN**
* Real-time leaderboard and scoring

### Adaptive Learning & Coaching
* Tracks study sessions
* Adjusts difficulty based on performance
* **AI Coach** available to contextually help students understand skipped concepts

---

# Tech Stack

### Backend
* **Python / Flask** - Core routing and logic
* **Flask-SocketIO** - Real-time websocket event handling for Live Events
* **Flask-SQLAlchemy (SQLite default)** - Database ORM

### Frontend
* **HTML5 + Jinja2 Templates**
* **Vanilla JavaScript (ES6)** (Stored natively in `/static/js`)
* **Custom CSS3** (Stored natively in `/static/css` – No bloated frameworks)

### AI Integration
* **Google Gemini API** (`google-generativeai`)

---

# Project Structure

```
Memrace Project/
│
├── models/          # Database ORM models
├── routes/          # API routes and Flask Blueprints
├── services/        # Business logic and Gemini AI services
├── templates/       # HTML Jinja2 templates
├── static/          # CSS stylesheets, Vanilla JS files, images
├── uploads/         # Storage for user-uploaded PDFs/Text
│
├── app.py           # Main Flask application entrypoint
├── config.py        # Configuration variables
└── requirements.txt # Python dependencies
```

---

# How to Run the Project

### 1. Prerequisites
* Python 3.8+

### 2. General Setup
From the root directory:
```bash
# Optional: Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install Python dependencies
pip install -r requirements.txt

# Create .env and add your variables (see config.py)
#   e.g. FLASK_SECRET_KEY=supersecret
#   e.g. GEMINI_API_KEY=your_gemini_key

# Run the server
python app.py
```
**Access the app:** Open your browser and navigate to `http://localhost:5000`.

*Note: Since Memrace uses standard Flask templates, there is no NodeJS/npm build step required! Everything works instantly out of the box.*

---

# Contributors

* Vishnu Sai
* Madhuri Singa
* Chandra Sekhar Reddy

---

# Project Motivation

The idea behind MEMRACE is to build a platform where students can **learn faster and retain knowledge longer** using adaptive learning techniques and AI-generated study materials.

By combining **AI, spaced repetition, and real-time quizzes**, MEMRACE aims to transform traditional studying into an engaging and efficient experience.
