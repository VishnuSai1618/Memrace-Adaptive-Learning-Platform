# MEMRACE – AI-Powered Adaptive Learning Platform

MEMRACE is an intelligent web-based learning platform that helps students study more effectively using **AI-generated flashcards, quizzes, and real-time live quiz sessions**.

The system adapts to a student's performance and dynamically adjusts the learning experience to improve knowledge retention.

MEMRACE combines the strengths of:

* Flashcard learning systems like **Anki**
* Interactive quiz platforms like **Kahoot**
* AI-powered content generation

to create a **smart, personalized learning environment**.

---

# Project Overview

MEMRACE allows users to upload study material and automatically generate learning content such as flashcards and quizzes using Artificial Intelligence.

The platform also includes **real-time multiplayer live quizzes** where students can compete with each other similar to Kahoot.

The goal of the project is to **make studying interactive, adaptive, and engaging**.

---

# Key Features

### AI Content Generation

* Automatically generate **flashcards and quiz questions** from uploaded study material
* Supports **text and PDF inputs**
* Uses AI to extract important concepts and key points

### Flashcard Learning System

* Study using flashcards
* Track learning progress
* Uses the **SM-2 spaced repetition algorithm** for better retention

### Quiz System

* Multiple choice quizzes generated from study material
* Tracks accuracy and performance
* Stores quiz attempts and analytics

### Live Quiz (Kahoot-style)

* Host real-time quiz sessions
* Players join using a **PIN**
* Real-time leaderboard and scoring
* Timer-based questions

### Adaptive Learning

* Tracks study sessions
* Adjusts difficulty based on performance
* Provides learning insights

### Gamification

* XP and level system
* Study streak tracking
* Progress monitoring

---

# Tech Stack

### Backend

* Python
* Flask
* Flask-SocketIO
* SQLAlchemy
* SQLite

### Frontend

* HTML
* CSS
* JavaScript

### AI Integration

* AI-based flashcard and quiz generation

### Real-time Communication

* WebSockets using **Flask-SocketIO**

---

# Project Structure

```
Memrace Project/
│
├── models/          # Database models
├── routes/          # API routes
├── services/        # Business logic and AI services
├── templates/       # HTML templates
├── static/          # CSS, JS, assets
├── uploads/         # Uploaded files
│
├── app.py           # Main Flask application
├── config.py        # Configuration settings
└── requirements.txt # Project dependencies
```

---

# How to Run the Project

### 1. Clone the repository

```
git clone https://github.com/MadhuriSinga/CSE_2022-2026_Batch-A01.git
```

### 2. Navigate to the project folder

```
cd CSE_2022-2026_Batch-A01
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Create environment file

Create a `.env` file and add required configuration variables.

### 5. Run the application

```
python app.py
```

The application will start on:

```
http://localhost:5000
```

---

# Future Improvements

* Better UI/UX design
* Mobile responsive interface
* Advanced AI content generation
* Real-time analytics dashboard
* Multiplayer quiz enhancements
* Cloud deployment

---

# Contributors

* Vishnu Sai
* Madhuri Singa
* Chandra Sekhar Reddy

---

# Project Motivation

The idea behind MEMRACE is to build a platform where students can **learn faster and retain knowledge longer** using adaptive learning techniques and AI-generated study materials.

By combining **AI, spaced repetition, and real-time quizzes**, MEMRACE aims to transform traditional studying into an engaging and efficient experience.

---
