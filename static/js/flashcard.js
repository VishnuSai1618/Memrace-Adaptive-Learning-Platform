// Flashcard study functionality

const deckId = parseInt(window.location.pathname.split('/').pop());
let flashcards = [];
let currentIndex = 0;
let isFlipped = false;
let correctCount = 0;
let startTime = null;

// Load flashcards
async function loadFlashcards() {
    try {
        const response = await fetch(`/api/flashcards/due/${deckId}`);
        const data = await response.json();
        flashcards = data.due_flashcards;

        if (flashcards.length === 0) {
            showCompletion();
            return;
        }

        startTime = Date.now();
        showFlashcard();

    } catch (error) {
        console.error('Error loading flashcards:', error);
        alert('Failed to load flashcards');
    }
}

// Show current flashcard
function showFlashcard() {
    if (currentIndex >= flashcards.length) {
        endStudySession();
        return;
    }

    const card = flashcards[currentIndex];

    document.getElementById('questionText').textContent = card.question;
    document.getElementById('answerText').textContent = card.answer;
    document.getElementById('cardProgress').textContent = `${currentIndex + 1} / ${flashcards.length}`;

    isFlipped = false;
    document.getElementById('flashcard').classList.remove('flipped');
}

// Reveal answer
document.getElementById('revealBtn').addEventListener('click', () => {
    isFlipped = true;
    document.getElementById('flashcard').classList.add('flipped');
});

// Handle correct answer
document.getElementById('correctBtn').addEventListener('click', async () => {
    await submitReview(true);
    correctCount++;
    nextCard();
});

// Handle wrong answer
document.getElementById('wrongBtn').addEventListener('click', async () => {
    await submitReview(false);
    nextCard();
});

// Submit review to backend
async function submitReview(correct) {
    const card = flashcards[currentIndex];
    const responseTime = Date.now() - startTime;

    try {
        const response = await fetch('/api/flashcards/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                flashcard_id: card.id,
                correct: correct,
                response_time_ms: responseTime
            })
        });

        const data = await response.json();

        // Immediate SM-2 Feedback using Toast
        if (data.next_review) {
            const nextReview = new Date(data.next_review);
            const dateStr = nextReview.toLocaleDateString();
            const timeStr = nextReview.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            showToast(`Next review: ${dateStr} ${timeStr}`);
        }

    } catch (error) {
        console.error('Error submitting review:', error);
    }
}

// Show toast notification
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = "toast-notification show";

    // Hide after 3 seconds
    setTimeout(() => {
        toast.className = toast.className.replace("show", "");
    }, 3000);
}

// Move to next card
function nextCard() {
    currentIndex++;
    startTime = Date.now();

    const accuracy = ((correctCount / currentIndex) * 100).toFixed(1);
    document.getElementById('accuracy').textContent = `Accuracy: ${accuracy}%`;

    showFlashcard();
}

// End study session
async function endStudySession() {
    try {
        await fetch('/api/flashcards/session/end', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cards_reviewed: flashcards.length,
                correct_count: correctCount,
                total_time_ms: Date.now() - startTime
            })
        });
    } catch (error) {
        console.error('Error ending session:', error);
    }

    showCompletion();
}

// Show completion message with AI Recommendations
async function showCompletion() {
    document.querySelector('.flashcard-wrapper').style.display = 'none';

    const completionMessage = document.getElementById('completionMessage');
    completionMessage.style.display = 'block';

    document.getElementById('totalReviewed').textContent = flashcards.length;
    document.getElementById('totalCorrect').textContent = correctCount;

    const finalAccuracy = flashcards.length > 0
        ? ((correctCount / flashcards.length) * 100).toFixed(1)
        : 0;
    document.getElementById('finalAccuracy').textContent = finalAccuracy + '%';

    // Fetch AI Recommendations
    try {
        const aiText = document.getElementById('aiRecommendationText');

        const response = await fetch('/api/recommendations/');
        const data = await response.json();

        if (data.recommendation) {
            aiText.textContent = `"${data.recommendation}"`;
            aiText.style.fontStyle = 'normal';
        }

        // Show weak areas if any
        if (data.weak_topics && data.weak_topics.length > 0) {
            const list = document.getElementById('weakAreasList');
            const container = document.getElementById('weakAreasContainer');

            list.innerHTML = ''; // Clear previous

            data.weak_topics.forEach(topic => {
                const li = document.createElement('li');
                li.innerHTML = `• <strong>${topic.deck_title}</strong> <span style="opacity: 0.8; font-size: 0.85em;">(Accuracy: ${topic.accuracy}%)</span>`;
                li.style.marginBottom = '4px';
                list.appendChild(li);
            });

            container.style.display = 'block';
        }

    } catch (error) {
        console.error('Error fetching recommendations:', error);
        document.getElementById('aiRecommendationText').textContent = "Great job finishing your session!";
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Start study session
    try {
        await fetch('/api/flashcards/session/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ deck_id: deckId })
        });
    } catch (error) {
        console.error('Error starting session:', error);
    }

    loadFlashcards();
});
