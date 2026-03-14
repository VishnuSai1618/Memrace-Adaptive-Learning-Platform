// Public repository functionality

let publicDecks = [];

// Load public decks
async function loadPublicDecks() {
    try {
        const response = await fetch('/api/repository/');
        const data = await response.json();
        publicDecks = data.public_decks;

        renderPublicDecks();

    } catch (error) {
        console.error('Error loading public decks:', error);
    }
}

// Render public decks
function renderPublicDecks() {
    const publicDecksList = document.getElementById('publicDecksList');
    const emptyState = document.getElementById('emptyState');

    if (publicDecks.length === 0) {
        publicDecksList.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';

    publicDecksList.innerHTML = publicDecks.map(publicDeck => `
        <div class="deck-card glass" style="border-left: 4px solid var(--accent-orange); padding: 2rem;">
            <h3 style="color: var(--primary-purple); font-size: 1.5rem; margin-bottom: 0.5rem;">${publicDeck.deck_title}</h3>
            <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${publicDeck.deck_description || 'No description provided.'}</p>
            <div class="deck-meta" style="display: flex; gap: 1rem; margin-bottom: 1.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                <span>👤 ${publicDeck.author_username}</span>
                <span>📚 ${publicDeck.flashcard_count} pieces of knowledge</span>
                <span style="color: var(--accent-orange);">📥 ${publicDeck.clone_count} clones</span>
            </div>
            <div class="deck-actions">
                <button class="btn-gamified" onclick="cloneDeck(${publicDeck.deck_id})" style="width: 100%;">Clone Knowledge</button>
            </div>
        </div>
    `).join('');
}

// Clone deck
async function cloneDeck(deckId) {
    try {
        const response = await fetch(`/api/repository/clone/${deckId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            alert('Deck cloned successfully!');
            window.location.href = '/dashboard';
        } else {
            alert(data.error || 'Failed to clone deck');
        }
    } catch (error) {
        console.error('Error cloning deck:', error);
        alert('Error cloning deck');
    }
}

// Search functionality
document.getElementById('searchInput').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();

    const filteredDecks = publicDecks.filter(deck =>
        deck.deck_title.toLowerCase().includes(searchTerm) ||
        (deck.deck_description && deck.deck_description.toLowerCase().includes(searchTerm)) ||
        deck.author_username.toLowerCase().includes(searchTerm)
    );

    const publicDecksList = document.getElementById('publicDecksList');

    if (filteredDecks.length === 0) {
        publicDecksList.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No decks found</p>';
        return;
    }

    publicDecksList.innerHTML = filteredDecks.map(publicDeck => `
        <div class="deck-card glass" style="border-left: 4px solid var(--accent-orange); padding: 2rem;">
            <h3 style="color: var(--primary-purple); font-size: 1.5rem; margin-bottom: 0.5rem;">${publicDeck.deck_title}</h3>
            <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${publicDeck.deck_description || 'No description provided.'}</p>
            <div class="deck-meta" style="display: flex; gap: 1rem; margin-bottom: 1.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                <span>👤 ${publicDeck.author_username}</span>
                <span>📚 ${publicDeck.flashcard_count} pieces of knowledge</span>
                <span style="color: var(--accent-orange);">📥 ${publicDeck.clone_count} clones</span>
            </div>
            <div class="deck-actions">
                <button class="btn-gamified" onclick="cloneDeck(${publicDeck.deck_id})" style="width: 100%;">Clone Knowledge</button>
            </div>
        </div>
    `).join('');
});

// Initialize
document.addEventListener('DOMContentLoaded', loadPublicDecks);
