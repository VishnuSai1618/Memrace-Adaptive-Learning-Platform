// Quiz functionality

const deckId = parseInt(window.location.pathname.split('/').pop());
let quizQuestions = [];
let currentQuestionIndex = 0;
let correctAnswers = 0;
let timer = null;
let timeLeft = 30;
let questionStartTime = null;

// Load quiz questions
async function loadQuiz() {
    try {
        const response = await fetch(`/api/quizzes/deck/${deckId}`);
        const data = await response.json();
        quizQuestions = data.quizzes;

        if (quizQuestions.length === 0) {
            alert('No quiz questions available for this deck');
            window.location.href = '/dashboard';
            return;
        }

        showQuestion();

    } catch (error) {
        console.error('Error loading quiz:', error);
        alert('Failed to load quiz');
    }
}

// Show current question
function showQuestion() {
    if (currentQuestionIndex >= quizQuestions.length) {
        showResults();
        return;
    }

    const question = quizQuestions[currentQuestionIndex];

    document.getElementById('questionProgress').textContent =
        `Question ${currentQuestionIndex + 1} / ${quizQuestions.length}`;
    document.getElementById('questionText').textContent = question.question;

    // Render options
    const optionsContainer = document.getElementById('optionsContainer');
    let optionsHtml = '';
    const optionLabels = ['A', 'B', 'C', 'D'];

    optionLabels.forEach(label => {
        if (question.options[label]) {
            optionsHtml += `
                <button class="quiz-option" onclick="selectOption('${label}')">
                    <span class="option-label">${label}</span>
                    <span class="option-text">${escapeHtml(question.options[label])}</span>
                </button>
            `;
        }
    });

    optionsContainer.innerHTML = optionsHtml;

    // Start timer
    startTimer();
    questionStartTime = Date.now();
}

// Start countdown timer
function startTimer() {
    timeLeft = 30;
    updateTimerDisplay();

    timer = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();

        if (timeLeft <= 0) {
            clearInterval(timer);
            selectOption(null, null); // Auto-submit as wrong
        }
    }, 1000);
}

// Update timer display
function updateTimerDisplay() {
    document.getElementById('timerText').textContent = timeLeft;

    const circle = document.getElementById('timerCircle');
    const circumference = 2 * Math.PI * 22;
    const offset = circumference - (timeLeft / 30) * circumference;

    circle.style.strokeDasharray = `${circumference} ${circumference}`;
    circle.style.strokeDashoffset = offset;

    // Change color when time is running out
    if (timeLeft <= 10) {
        circle.style.stroke = 'var(--accent-red)';
    } else {
        circle.style.stroke = 'var(--accent-yellow)';
    }
}

// Select an option
async function selectOption(selectedLetter) {
    if (document.getElementById('submitAnswerBtn') && document.getElementById('submitAnswerBtn').style.display === 'none') {
        return; // Prevent double submission
    }
    clearInterval(timer);

    const question = quizQuestions[currentQuestionIndex];
    const timeTaken = Date.now() - questionStartTime;
    const selectedAnswerText = selectedLetter ? question.options[selectedLetter] : null;

    const correct = selectedAnswerText === question.correct_answer;

    if (correct) {
        correctAnswers++;
    }

    // Submit answer to backend
    try {
        await fetch('/api/quizzes/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quiz_id: question.id,
                selected_answer: selectedAnswerText || '',
                time_taken_ms: timeTaken
            })
        });
    } catch (error) {
        console.error('Error submitting answer:', error);
    }

    // Visual feedback
    const options = document.querySelectorAll('.quiz-option');
    options.forEach(opt => {
        const optionLabel = opt.querySelector('.option-label').textContent;
        const optionText = opt.querySelector('.option-text').textContent;

        if (optionText === question.correct_answer) {
            opt.classList.add('correct');
        } else if (optionLabel === selectedLetter && !correct) { // Mark selected incorrect option
            opt.classList.add('incorrect');
        }
        opt.style.pointerEvents = 'none'; // Disable further clicks
    });

    if (document.getElementById('submitAnswerBtn')) {
        document.getElementById('submitAnswerBtn').style.display = 'none'; // Hide submit button after submission
    }

    // Move to next question after delay
    setTimeout(() => {
        currentQuestionIndex++;
        showQuestion();
    }, 2000);
}

// Show results
function showResults() {
    document.getElementById('quizContent').style.display = 'none';
    document.getElementById('resultsScreen').style.display = 'block';

    document.getElementById('totalQuestions').textContent = quizQuestions.length;
    document.getElementById('correctAnswers').textContent = correctAnswers;

    const accuracy = ((correctAnswers / quizQuestions.length) * 100).toFixed(1);
    document.getElementById('quizAccuracy').textContent = accuracy + '%';
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize
document.addEventListener('DOMContentLoaded', loadQuiz);
