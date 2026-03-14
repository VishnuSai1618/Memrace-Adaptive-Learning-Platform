# Tech Stack Documentation

## Project Name

AI-Powered Adaptive Flashcard Learning System with Spaced Repetition

---

## 1. Overview

This document describes the complete technical stack used to build the AI-Powered Adaptive Flashcard Learning System. The chosen technologies ensure simplicity, scalability, and alignment with the defined project workflow and algorithms.

The system follows a modular client–server architecture where the frontend handles user interaction, the backend manages business logic and algorithms, and external AI services handle content generation.

---

## 2. Architecture Overview

* **Architecture Type:** Web-based Client–Server Architecture
* **Frontend:** Browser-based UI
* **Backend:** RESTful Flask application
* **Database:** Lightweight relational database
* **AI Integration:** External AI API (Google Gemini)

---

## 3. Frontend Tech Stack

### Technologies Used

* **HTML5** – Structure of the web application
* **CSS3** – Styling and layout
* **JavaScript (ES6)** – Client-side interactivity

### Responsibilities

* File upload interface (Text / PDF)
* Flashcard display (Question–Answer)
* User interactions (Correct / Wrong buttons)
* Quiz interface (MCQ)
* Analytics visualization

### Reason for Selection

* Lightweight and easy to deploy
* No additional frameworks required
* Suitable for academic and prototype-level projects

---

## 4. Backend Tech Stack

### Technologies Used

* **Python 3.x** – Core backend language
* **Flask** – Web framework

### Responsibilities

* Handling file uploads
* Text extraction from PDFs
* Communication with AI API
* Flashcard and quiz generation logic
* Implementation of SM-2 algorithm
* Managing study sessions and review schedules
* Exposing REST APIs to frontend

### Reason for Selection

* Simple and flexible framework
* Strong ecosystem for AI and ML integration
* Easy to maintain and extend

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

* Lightweight and file-based
* No separate server required
* Ideal for academic projects

---

## 6. AI & NLP Layer

### Technologies Used

* **Google Gemini API**

### Responsibilities

* Understanding uploaded study content
* Generating flashcards (Q&A format)
* Generating quiz questions (MCQs)
* Assisting in content summarization

### Reason for Selection

* High-quality natural language understanding
* Easy API-based integration
* Suitable for dynamic content generation

---

## 7. Algorithms Used

### SM-2 Algorithm (SuperMemo 2)

**Purpose:**

* Schedule flashcard reviews using spaced repetition

**Inputs:**

* User response (Correct / Incorrect)
* Response time
* Previous review history

**Outputs:**

* Next review date
* Updated ease factor

### Rule-Based Recommendation Engine

**Purpose:**

* Provide personalized study recommendations

**Logic Includes:**

* Accuracy trends
* Frequency of incorrect answers
* Time taken per flashcard

---

## 8. File Processing Libraries

### Libraries Used

* **PyPDF2** – Extract text from PDF files

### Responsibilities

* Read uploaded PDFs
* Convert PDF content into raw text for AI processing

---

## 9. API Communication

### Type

* RESTful APIs

### Communication Flow

* Frontend sends requests to Flask backend
* Backend processes data and calls Gemini API
* Processed results returned to frontend

---

## 10. Security Considerations

* Input validation for file uploads
* Restricted file size and format
* Secure handling of API keys
* No direct database access from frontend

---

## 11. Deployment Strategy

* **Deployment Type:** Local / Institutional Server
* **Environment:** Python virtual environment
* **Web Server:** Flask built-in server (development)

> Note: Cloud deployment is out of scope as per requirements.

---

## 12. Scalability & Maintainability

* Modular backend structure
* Clear separation of concerns
* Easy migration to:

  * PostgreSQL / MySQL
  * React frontend
  * Cloud deployment

---

## 13. Development Tools

* Visual Studio Code
* Git & GitHub
* Postman (API testing)

---

## 14. Summary

The selected tech stack ensures a balanced combination of simplicity, efficiency, and AI capability. It aligns strictly with the project requirements, avoids unnecessary complexity, and supports future enhancements without major architectural changes.
