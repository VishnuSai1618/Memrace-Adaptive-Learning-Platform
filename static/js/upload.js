// Upload functionality

let currentMode = 'pdf';
let selectedFile = null;

// Toggle between PDF, text, and blank mode
document.getElementById('pdfToggle').addEventListener('click', () => {
    currentMode = 'pdf';
    document.getElementById('pdfToggle').classList.add('active');
    document.getElementById('textToggle').classList.remove('active');
    document.getElementById('blankToggle').classList.remove('active');
    document.getElementById('pdfSection').style.display = 'block';
    document.getElementById('textSection').style.display = 'none';
    document.getElementById('blankSection').style.display = 'none';
});

document.getElementById('textToggle').addEventListener('click', () => {
    currentMode = 'text';
    document.getElementById('textToggle').classList.add('active');
    document.getElementById('pdfToggle').classList.remove('active');
    document.getElementById('blankToggle').classList.remove('active');
    document.getElementById('textSection').style.display = 'block';
    document.getElementById('pdfSection').style.display = 'none';
    document.getElementById('blankSection').style.display = 'none';
});

document.getElementById('blankToggle').addEventListener('click', () => {
    currentMode = 'blank';
    document.getElementById('blankToggle').classList.add('active');
    document.getElementById('pdfToggle').classList.remove('active');
    document.getElementById('textToggle').classList.remove('active');
    document.getElementById('blankSection').style.display = 'block';
    document.getElementById('pdfSection').style.display = 'none';
    document.getElementById('textSection').style.display = 'none';
});

// File upload handling
const fileInput = document.getElementById('pdfFile');
const fileUploadArea = document.getElementById('fileUploadArea');

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        showFileInfo(selectedFile.name);
    }
});

// Drag and drop
fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.style.borderColor = 'var(--primary-purple)';
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.style.borderColor = 'var(--dark-hover)';
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.style.borderColor = 'var(--dark-hover)';

    if (e.dataTransfer.files.length > 0) {
        selectedFile = e.dataTransfer.files[0];
        fileInput.files = e.dataTransfer.files;
        showFileInfo(selectedFile.name);
    }
});

function showFileInfo(filename) {
    document.querySelector('.upload-placeholder').style.display = 'none';
    const fileInfo = document.getElementById('fileInfo');
    fileInfo.style.display = 'block';
    document.getElementById('fileName').textContent = filename;
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    document.querySelector('.upload-placeholder').style.display = 'block';
    document.getElementById('fileInfo').style.display = 'none';
}

// PDF upload form
document.getElementById('pdfUploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!selectedFile) {
        showError('Please select a PDF file');
        return;
    }

    const title = document.getElementById('deckTitle').value;
    const description = document.getElementById('deckDescription').value;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('title', title);
    formData.append('description', description);

    showLoading();

    try {
        // Upload PDF and create deck
        const uploadResponse = await fetch('/api/content/upload', {
            method: 'POST',
            body: formData
        });

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok) {
            throw new Error(uploadData.error || 'Upload failed');
        }

        // Generate flashcards
        const generateResponse = await fetch('/api/content/generate-flashcards', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                deck_id: uploadData.deck.id,
                num_cards: 10
            })
        });

        const generateData = await generateResponse.json();

        if (!generateResponse.ok) {
            throw new Error(generateData.error || 'Flashcard generation failed');
        }

        // Generate quiz questions
        const quizResponse = await fetch('/api/content/generate-quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                deck_id: uploadData.deck.id,
                num_questions: 5
            })
        });

        if (!quizResponse.ok) {
            const quizData = await quizResponse.json();
            throw new Error(quizData.error || 'Quiz generation failed');
        }

        hideLoading();
        showSuccess();

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
});

// Text upload form
document.getElementById('textUploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('textDeckTitle').value;
    const description = document.getElementById('textDeckDescription').value;
    const content = document.getElementById('textContent').value;

    if (!content.trim()) {
        showError('Please enter some content');
        return;
    }

    showLoading();

    try {
        // Create deck with text
        const uploadResponse = await fetch('/api/content/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                description,
                content
            })
        });

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok) {
            throw new Error(uploadData.error || 'Upload failed');
        }

        // Generate flashcards
        const generateResponse = await fetch('/api/content/generate-flashcards', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                deck_id: uploadData.deck.id,
                num_cards: 10
            })
        });

        const generateData = await generateResponse.json();

        if (!generateResponse.ok) {
            throw new Error(generateData.error || 'Flashcard generation failed');
        }

        // Generate quiz questions
        const quizResponse = await fetch('/api/content/generate-quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                deck_id: uploadData.deck.id,
                num_questions: 5
            })
        });

        if (!quizResponse.ok) {
            const quizData = await quizResponse.json();
            throw new Error(quizData.error || 'Quiz generation failed');
        }

        hideLoading();
        showSuccess();

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
});

// Blank deck upload form
document.getElementById('blankDeckForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('blankDeckTitle').value;
    const description = document.getElementById('blankDeckDescription').value;

    showLoading();

    try {
        // Create blank deck
        const createResponse = await fetch('/api/content/create-deck', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                description
            })
        });

        const createData = await createResponse.json();

        if (!createResponse.ok) {
            throw new Error(createData.error || 'Deck creation failed');
        }

        hideLoading();
        // Redirect completely to frontend Deck Edit page
        window.location.href = `/deck/${createData.deck.id}/edit`;

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
});

function showLoading() {
    document.getElementById('pdfSection').style.display = 'none';
    document.getElementById('textSection').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

function showSuccess() {
    document.getElementById('successMessage').style.display = 'block';
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}
