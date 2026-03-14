// Edit Deck Functionality
let currentMode = 'flashcards'; // 'flashcards' or 'quizzes'
let deckData = null;

document.addEventListener('DOMContentLoaded', () => {
    loadDeckData();

    // Toggle logic
    document.getElementById('flashcardBtn').addEventListener('click', () => switchMode('flashcards'));
    document.getElementById('quizBtn').addEventListener('click', () => switchMode('quizzes'));

    // Form logic
    document.getElementById('addFlashcardForm').addEventListener('submit', handleAddFlashcard);
    document.getElementById('addQuizForm').addEventListener('submit', handleAddQuiz);
});

async function loadDeckData() {
    try {
        const response = await fetch(`/api/content/decks/${currentDeckId}`);
        if (!response.ok) throw new Error('Failed to load deck data');

        const data = await response.json();
        deckData = data.deck;

        document.getElementById('deckTitleHeading').textContent = deckData.title;
        document.getElementById('deckDescripText').textContent = deckData.description || "No description provided.";

        renderFlashcards();
        renderQuizzes();

        document.getElementById('loadingIndicator').style.display = 'none';
        switchMode(currentMode);
    } catch (e) {
        console.error(e);
        document.getElementById('deckTitleHeading').textContent = "Error loading deck";
        document.getElementById('loadingIndicator').style.display = 'none';
    }
}

function switchMode(mode) {
    currentMode = mode;
    if (mode === 'flashcards') {
        document.getElementById('flashcardBtn').classList.add('active');
        document.getElementById('quizBtn').classList.remove('active');
        document.getElementById('flashcardsSection').style.display = 'block';
        document.getElementById('quizzesSection').style.display = 'none';
    } else {
        document.getElementById('quizBtn').classList.add('active');
        document.getElementById('flashcardBtn').classList.remove('active');
        document.getElementById('quizzesSection').style.display = 'block';
        document.getElementById('flashcardsSection').style.display = 'none';
    }
}

// ============== FLASHCARDS ==============

function renderFlashcards() {
    const list = document.getElementById('flashcardsList');
    if (!deckData.flashcards || deckData.flashcards.length === 0) {
        list.innerHTML = `<p style="color: var(--text-secondary);">No flashcards yet. Add one below!</p>`;
        return;
    }

    list.innerHTML = deckData.flashcards.map(fc => `
        <div class="deck-card" style="display: flex; justify-content: space-between; align-items: flex-start; background: rgba(255,152,0,0.05); border: 1px solid rgba(255,152,0,0.2);">
            <div style="flex: 1;">
                <h4 style="color: var(--primary-purple); margin-bottom: 0.5rem; white-space: pre-wrap;">Q: ${escapeHtml(fc.question)}</h4>
                <p style="color: var(--text-secondary); white-space: pre-wrap;">A: ${escapeHtml(fc.answer)}</p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-left: 1rem;">
                <button onclick="openEditFlashcardModal(${fc.id})" class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.9rem;">Edit</button>
                <button onclick="deleteFlashcard(${fc.id})" class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.9rem; border-color: var(--accent-red); color: var(--accent-red);">Delete</button>
            </div>
        </div>
    `).join('');
}

async function handleAddFlashcard(e) {
    e.preventDefault();
    const q = document.getElementById('newFcQuestion').value;
    const a = document.getElementById('newFcAnswer').value;

    try {
        const response = await fetch('/api/flashcards/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ deck_id: currentDeckId, question: q, answer: a })
        });
        if (!response.ok) throw new Error('Failed to create flashcard');

        // Reset form and reload data
        document.getElementById('addFlashcardForm').reset();
        await loadDeckData();
    } catch (error) {
        alert(error.message);
    }
}

async function deleteFlashcard(fcId) {
    if (!confirm("Are you sure you want to delete this flashcard?")) return;
    try {
        const response = await fetch(`/api/flashcards/${fcId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete flashcard');
        await loadDeckData();
    } catch (err) {
        alert(err.message);
    }
}

function openEditFlashcardModal(fcId) {
    const fc = deckData.flashcards.find(c => c.id === fcId);
    if (!fc) return;

    document.getElementById('modalTitle').textContent = "Edit Flashcard";
    const content = document.getElementById('modalContent');
    content.innerHTML = `
        <form id="editFcForm">
            <div class="form-group">
                <label>Front (Question)</label>
                <textarea id="editFcQ" rows="2" required>${escapeHtml(fc.question)}</textarea>
            </div>
            <div class="form-group">
                <label>Back (Answer)</label>
                <textarea id="editFcA" rows="2" required>${escapeHtml(fc.answer)}</textarea>
            </div>
            <button type="submit" class="btn-primary" style="width: 100%;">Save Changes</button>
        </form>
    `;

    document.getElementById('editModal').style.display = 'flex';
    document.getElementById('editFcForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const q = document.getElementById('editFcQ').value;
            const a = document.getElementById('editFcA').value;
            const res = await fetch(`/api/flashcards/${fcId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: q, answer: a })
            });
            if (!res.ok) throw new Error('Failed to update flashcard');
            closeEditModal();
            await loadDeckData();
        } catch (err) {
            alert(err.message);
        }
    });
}

// ============== QUIZZES ==============

function renderQuizzes() {
    const list = document.getElementById('quizzesList');
    if (!deckData.quizzes || deckData.quizzes.length === 0) {
        list.innerHTML = `<p style="color: var(--text-secondary);">No quizzes yet. Add one below!</p>`;
        return;
    }

    list.innerHTML = deckData.quizzes.map(q => {
        // Find which option matches the correct_answer
        let correctLetter = 'A';
        if (q.options) {
            if (q.options.B === q.correct_answer) correctLetter = 'B';
            if (q.options.C === q.correct_answer) correctLetter = 'C';
            if (q.options.D === q.correct_answer) correctLetter = 'D';
        }

        return `
        <div class="deck-card" style="display: flex; justify-content: space-between; align-items: flex-start; background: rgba(59,130,246,0.05); border: 1px solid rgba(59,130,246,0.2);">
            <div style="flex: 1;">
                <h4 style="color: var(--accent-blue); margin-bottom: 0.5rem; white-space: pre-wrap;">${escapeHtml(q.question)}</h4>
                <ul style="list-style: none; padding-left: 0; color: var(--text-secondary); font-size: 0.95rem;">
                    <li><strong>A:</strong> ${escapeHtml(q.options ? q.options.A : '')}</li>
                    <li><strong>B:</strong> ${escapeHtml(q.options ? q.options.B : '')}</li>
                    <li><strong>C:</strong> ${escapeHtml(q.options ? q.options.C : '')}</li>
                    <li><strong>D:</strong> ${escapeHtml(q.options ? q.options.D : '')}</li>
                </ul>
                <p style="margin-top: 0.5rem; color: var(--accent-green);"><strong>Correct:</strong> Option ${correctLetter}</p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-left: 1rem;">
                <button onclick="openEditQuizModal(${q.id})" class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.9rem;">Edit</button>
                <button onclick="deleteQuiz(${q.id})" class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.9rem; border-color: var(--accent-red); color: var(--accent-red);">Delete</button>
            </div>
        </div>
        `;
    }).join('');
}

async function handleAddQuiz(e) {
    e.preventDefault();
    const q = document.getElementById('newQuizQues').value;
    const optA = document.getElementById('optA').value;
    const optB = document.getElementById('optB').value;
    const optC = document.getElementById('optC').value;
    const optD = document.getElementById('optD').value;
    const correctLetter = document.getElementById('correctAns').value;

    // Resolve the literal text of the correct answer
    let correctStr = optA;
    if (correctLetter === 'B') correctStr = optB;
    if (correctLetter === 'C') correctStr = optC;
    if (correctLetter === 'D') correctStr = optD;

    try {
        const response = await fetch('/api/quizzes/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deck_id: currentDeckId,
                question: q,
                option_a: optA,
                option_b: optB,
                option_c: optC,
                option_d: optD,
                correct_answer: correctStr
            })
        });
        if (!response.ok) throw new Error('Failed to create quiz');

        document.getElementById('addQuizForm').reset();
        await loadDeckData();
    } catch (error) {
        alert(error.message);
    }
}

async function deleteQuiz(qId) {
    if (!confirm("Are you sure you want to delete this quiz question?")) return;
    try {
        const response = await fetch(`/api/quizzes/${qId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete quiz');
        await loadDeckData();
    } catch (err) {
        alert(err.message);
    }
}

function openEditQuizModal(qId) {
    const q = deckData.quizzes.find(x => x.id === qId);
    if (!q) return;

    let correctLetter = 'A';
    if (q.options) {
        if (q.options.B === q.correct_answer) correctLetter = 'B';
        if (q.options.C === q.correct_answer) correctLetter = 'C';
        if (q.options.D === q.correct_answer) correctLetter = 'D';
    }

    document.getElementById('modalTitle').textContent = "Edit Quiz Question";
    const content = document.getElementById('modalContent');
    content.innerHTML = `
        <form id="editQuizForm">
            <div class="form-group">
                <label>Question</label>
                <textarea id="editQuizQ" rows="2" required>${escapeHtml(q.question)}</textarea>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                    <label>Option A</label>
                    <input type="text" id="editOptA" required value="${escapeHtml(q.options.A)}">
                </div>
                <div class="form-group">
                    <label>Option B</label>
                    <input type="text" id="editOptB" required value="${escapeHtml(q.options.B)}">
                </div>
                <div class="form-group">
                    <label>Option C</label>
                    <input type="text" id="editOptC" required value="${escapeHtml(q.options.C)}">
                </div>
                <div class="form-group">
                    <label>Option D</label>
                    <input type="text" id="editOptD" required value="${escapeHtml(q.options.D)}">
                </div>
            </div>
            <div class="form-group" style="margin-top: 1rem;">
                <label>Correct Answer</label>
                <select id="editCorrectAns" required style="width: 100%; padding: 0.75rem; background: var(--dark-bg); border: 1px solid var(--dark-border); border-radius: var(--radius-sm); color: var(--text-primary);">
                    <option value="A" ${correctLetter === 'A' ? 'selected' : ''}>Option A</option>
                    <option value="B" ${correctLetter === 'B' ? 'selected' : ''}>Option B</option>
                    <option value="C" ${correctLetter === 'C' ? 'selected' : ''}>Option C</option>
                    <option value="D" ${correctLetter === 'D' ? 'selected' : ''}>Option D</option>
                </select>
            </div>
            <button type="submit" class="btn-primary" style="width: 100%;">Save Changes</button>
        </form>
    `;

    document.getElementById('editModal').style.display = 'flex';
    document.getElementById('editQuizForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const question = document.getElementById('editQuizQ').value;
            const optA = document.getElementById('editOptA').value;
            const optB = document.getElementById('editOptB').value;
            const optC = document.getElementById('editOptC').value;
            const optD = document.getElementById('editOptD').value;
            const correctLet = document.getElementById('editCorrectAns').value;

            let correctStr = optA;
            if (correctLet === 'B') correctStr = optB;
            if (correctLet === 'C') correctStr = optC;
            if (correctLet === 'D') correctStr = optD;

            const res = await fetch(`/api/quizzes/${qId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    option_a: optA,
                    option_b: optB,
                    option_c: optC,
                    option_d: optD,
                    correct_answer: correctStr
                })
            });
            if (!res.ok) throw new Error('Failed to update quiz question');
            closeEditModal();
            await loadDeckData();
        } catch (err) {
            alert(err.message);
        }
    });
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
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
