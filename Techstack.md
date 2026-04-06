# Tech Stack Documentation

## Project Name

AI-Powered Adaptive Flashcard Learning System with Spaced Repetition (Memrace)

---

## 1. Overview

This document describes the complete, *actual* technical stack used to build the AI-Powered Adaptive Flashcard Learning System. The chosen technologies ensure simplicity, scalability, and alignment with the defined project workflow and algorithms.

The system follows a modular client–server architecture where the frontend handles user interaction using modern Vanilla JS, the backend manages business logic and AI processing, and external AI services handle content generation.

**🚫 Anti-Assumptions (What is NOT used):**
- **No React / Next.js / SPAs:** The frontend is purely server-rendered Jinja2 templates augmented with Vanilla JS (ES6).
- **No Tailwind CSS:** Styling is completely custom using standard CSS3 built natively.
- **No PostgreSQL / Cloud SQL:** The application purely uses file-based SQLite via SQLAlchemy.

---

## 2. Architecture Overview

* **Architecture Type:** Web-based Client–Server Architecture
* **Frontend:** Browser-based UI (Jinja2 Templates + Custom CSS/JS)
* **Backend:** RESTful Flask application + WebSocket support
* **Database:** Lightweight relational database (SQLite)
* **AI Integration:** External AI API (Google Gemini)

---

## 3. Frontend Tech Stack

### Technologies Used

* **HTML5 + Jinja2** – Structure of the web application and server-side rendering
* **CSS3** – Custom styling, layout, animations, and Glassmorphism (no CSS frameworks)
* **JavaScript (ES6)** – Client-side interactivity, DOM manipulation, Socket.io clients

### Responsibilities

* File upload interface (Text / PDF)
* Flashcard display (Question–Answer)
* User interactions (Correct / Wrong buttons)
* Quiz interface (MCQ) & Real-time Live Multiplayer Quizzes
* Analytics visualization

### Reason for Selection

* Lightweight and easy to deploy
* Zero bundle overhead natively optimizing speeds
* Highly cohesive with Flask Jinja templates

---

## 4. Backend Tech Stack

### Technologies Used

* **Python 3.x** – Core backend language
* **Flask** – Web framework
* **Flask-SocketIO / Eventlet** – Real-time event broadcasting for multiplayer Live Quizzes
* **Flask-Login** – Session management

### Responsibilities

* Handling file uploads and Text extraction from PDFs
* Managing REST APIs and WebSocket connections
* Flashcard and quiz generation logic
* Implementation of SM-2 spaced repetition algorithm
* Session management and user state validation

### Reason for Selection

* Simple, non-opinionated API endpoints
* Strong ecosystem for AI integration
* SocketIO bridges the gap between typical request-response cycles and live events

---

## 5. Database Layer

### Technologies Used

* **SQLite** – Relational database
* **Flask-SQLAlchemy** – ORM layer

### Data Stored

* User information
* Flashcard data
* Quiz data
* Performance metrics
* Review schedules
* Public deck metadata

### Reason for Selection

* Lightweight and file-based (no separate server dependencies)
* Zero-configuration ideal for rapid iteration

---

## 6. AI & NLP Layer

### Technologies Used

* **Google Gemini API** (via `google-generativeai`)

### Responsibilities

* Understanding uploaded study content
* Generating flashcards (Q&A format)
* Generating quiz questions (MCQs)
* Powering the "AI Coach" for personalized learning context

### Reason for Selection

* High-quality natural language understanding
* Easy API-based integration

---

## 7. Algorithms Used

### SM-2 Algorithm (SuperMemo 2)
**Purpose:** Schedule flashcard reviews using spaced repetition
**Inputs:** User response (Correct / Incorrect), Response time
**Outputs:** Next review date, Updated ease factor

### Rule-Based Recommendation Engine
**Purpose:** Provide personalized study recommendations based on accuracy trends and response times.

---

## 8. File Processing Libraries

### Libraries Used
* **PyPDF2** – Extract text from PDF files

---

## 9. API Communication

### Type
* HTTP RESTful APIs
* WebSockets (for Live Multiplayer mode)

---

## 10. Security Considerations

* Input validation for file uploads (restricted formats)
* Environment variable injection via `.env`
* Jinja API auto-escaping natively preventing XSS

---

## 11. Deployment Strategy

* **Web Server:** Standard Python environments using eventlet WSGI

---

## 12. Scalability & Maintainability

* Modular backend structure (Blueprints)
* Database agnostic relying abstractly on ORM
