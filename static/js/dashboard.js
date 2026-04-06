// Dashboard functionality

let currentUser = null;
let userDecks = [];
let recommendations = null;

// Load dashboard data
async function loadDashboard() {
    try {
        // Get current user
        const userResponse = await fetch('/api/auth/user');
        const userData = await userResponse.json();
        currentUser = userData.user;

        document.getElementById('welcomeMessage').textContent = `Welcome back, ${currentUser.username}! 🏆`;

        // Update Gamification UI
        const level = currentUser.level || 1;
        const xp = currentUser.xp || 0;
        const streak = currentUser.streak || 0;
        const xpThreshold = level * 1000;
        const xpPercentage = Math.min((xp / xpThreshold) * 100, 100).toFixed(1);

        document.getElementById('userLevel').textContent = `LEVEL ${level}`;
        document.getElementById('userXp').textContent = `${xp.toLocaleString()} / ${xpThreshold.toLocaleString()} XP`;
        document.getElementById('xpProgressBar').style.width = `${xpPercentage}%`;

        // The daily streak stat is loaded later, but we can set it via JS directly now
        const streakEl = document.getElementById('dailyStreak');
        if (streakEl) streakEl.textContent = streak;

        // Load decks
        await loadDecks();

        // Load recommendations
        await loadRecommendations();

        // Load stats
        await loadStats();

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load user's decks
async function loadDecks() {
    try {
        const response = await fetch('/api/content/decks');
        const data = await response.json();
        userDecks = data.decks;

        document.getElementById('totalDecks').textContent = userDecks.length;

        // Get due reviews for each deck
        await renderDecksWithReviews();
    } catch (error) {
        console.error('Error loading decks:', error);
    }
}

// Render decks with due review information
async function renderDecksWithReviews() {
    const decksList = document.getElementById('decksList');

    if (userDecks.length === 0) {
        decksList.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem;">
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">No decks yet. Create your first deck!</p>
                <a href="/upload" class="btn-primary">Create Deck</a>
            </div>
        `;
        return;
    }

    // Get due reviews for all decks
    const decksWithReviews = await Promise.all(userDecks.map(async (deck) => {
        try {
            const response = await fetch(`/api/flashcards/due/${deck.id}`);
            const data = await response.json();
            return { ...deck, due_count: data.count };
        } catch (error) {
            return { ...deck, due_count: 0 };
        }
    }));

    decksList.innerHTML = decksWithReviews.map(deck => {
        const hasDueReviews = deck.due_count > 0;
        const borderColor = hasDueReviews ? 'var(--accent-yellow)' : 'transparent';
        const dueBadge = hasDueReviews ? `
            <div style="
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: var(--accent-yellow);
                color: var(--dark-bg);
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: bold;
            ">
                ${deck.due_count} Due
            </div>
        ` : '';

        return `
            <div class="deck-card" style="position: relative; border: 2px solid ${borderColor};" onclick="viewDeck(${deck.id})">
                ${dueBadge}
                <h3>${deck.title}</h3>
                <p>${deck.description || 'No description'}</p>
                <div class="deck-meta">
                    <span>📚 ${deck.flashcard_count} cards</span>
                    <span>❓ ${deck.quiz_count} quizzes</span>
                </div>
                ${hasDueReviews ? `
                    <div style="margin-top: 0.75rem; padding: 0.5rem; background: rgba(251, 191, 36, 0.1); border-radius: var(--radius-sm);">
                        <p style="font-size: 0.85rem; color: var(--accent-yellow);">
                            ⏰ ${deck.due_count} card${deck.due_count > 1 ? 's' : ''} ready for review!
                        </p>
                    </div>
                ` : ''}
                <div class="deck-actions" onclick="event.stopPropagation()">
                    <button class="btn-gradient" onclick="studyDeck(${deck.id})">Study</button>
                    <button class="btn-secondary" onclick="takequiz(${deck.id})">Quiz</button>
                    <button class="btn-gradient-outline" onclick="window.location.href='/live/host/${deck.id}'">Host Live</button>
                    ${deck.is_public 
                        ? `<button class="btn-secondary" style="border-color: var(--accent-red); color: var(--accent-red);" onclick="unpublishDeck(${deck.id})">Unshare</button>`
                        : `<button class="btn-secondary" style="border-color: var(--accent-orange); color: var(--accent-orange);" onclick="publishDeck(${deck.id})">Share</button>`
                    }
                    <button class="btn-secondary" style="border-color: var(--accent-blue); color: var(--accent-blue);" onclick="editDeck(${deck.id})">Edit</button>
                    <button class="btn-secondary" onclick="deleteDeck(${deck.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

// Load recommendations
async function loadRecommendations() {
    try {
        // 1. Get standard stats-based recommendations
        const response = await fetch('/api/analytics/recommendations');
        const data = await response.json();
        recommendations = data.recommendations;

        const dueReviewsEl = document.getElementById('dueReviews');
        if (dueReviewsEl) dueReviewsEl.textContent = recommendations.due_reviews;
        const masteredCardsEl = document.getElementById('masteredCards');
        if (masteredCardsEl) masteredCardsEl.textContent = recommendations.total_cards_mastered;
        const masteryRankEl = document.getElementById('masteryRank');
        if (masteryRankEl) masteryRankEl.textContent = recommendations.mastery_rank || 'Beginner';

        const recommendationsContent = document.getElementById('recommendationsContent');
        if (!recommendationsContent) return;

        // 2. Load cached AI insight (no API call — user must click to generate)
        let aiMessageHTML = '';
        try {
            const aiResponse = await fetch('/api/recommendations/');
            const aiData = await aiResponse.json();
            if (aiData.recommendation) {
                const generatedAt = aiData.generated_at ? new Date(aiData.generated_at).toLocaleString() : '';
                aiMessageHTML = `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(30,58,138,0.2) 100%); border-radius: var(--radius-md); border: 1px solid rgba(59,130,246,0.2);">
                        <h4 style="color: #60a5fa; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                            <span>🤖</span> AI Coach Says:
                        </h4>
                        <p style="color: #e2e8f0; line-height: 1.5; font-style: italic;">"${aiData.recommendation}"</p>
                        <p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem;">Generated: ${generatedAt}</p>
                    </div>
                `;
            } else {
                aiMessageHTML = `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: var(--radius-md); text-align: center;">
                        <p style="color: var(--text-muted);">No AI insights yet. Click the button below to generate your first coaching!</p>
                    </div>
                `;
            }
        } catch (e) {
            console.error('Failed to load AI insight', e);
        }

        // 3. Get upcoming review schedule
        const upcomingResponse = await fetch('/api/flashcards/upcoming-reviews?days=7');
        const upcomingData = await upcomingResponse.json();
        const reviewSchedule = upcomingData.review_schedule;

        let scheduleHTML = '';
        if (Object.keys(reviewSchedule).length > 0) {
            const today = new Date().toISOString().split('T')[0];
            const sortedDates = Object.keys(reviewSchedule).sort();

            scheduleHTML = `
                <div style="margin-top: 1.5rem; padding: 1rem; background: var(--dark-card); border-radius: var(--radius-md);">
                    <h4 style="margin-bottom: 1rem; color: var(--text-secondary);">📅 Upcoming Reviews (Next 7 Days)</h4>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        ${sortedDates.slice(0, 7).map(date => {
                const count = reviewSchedule[date];
                const isToday = date === today;
                const dateObj = new Date(date);
                const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

                return `
                                <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    padding: 0.5rem;
                                    background: ${isToday ? 'rgba(251, 191, 36, 0.1)' : 'var(--dark-bg)'};
                                    border-radius: var(--radius-sm);
                                    border-left: 3px solid ${isToday ? 'var(--accent-yellow)' : 'var(--primary-purple)'};
                                ">
                                    <span style="color: ${isToday ? 'var(--accent-yellow)' : 'var(--text-primary)'}; font-weight: ${isToday ? 'bold' : 'normal'};">
                                        ${isToday ? '🔔 Today' : dayName}
                                    </span>
                                    <span style="color: var(--text-secondary);">${count} card${count > 1 ? 's' : ''}</span>
                                </div>
                            `;
            }).join('')}
                    </div>
                </div>
            `;
        }

        // Render everything
        recommendationsContent.innerHTML = `
            ${aiMessageHTML}
            <div style="margin-bottom: 1rem;">
                <button id="btnGenerateInsights" class="btn-gradient" onclick="generateAIInsights()" 
                    style="width: 100%; padding: 0.75rem; font-size: 1rem;">
                    🔄 Generate New Insights
                </button>
            </div>
            <h3>📌 Focus: ${recommendations.suggested_focus}</h3>
            ${recommendations.weak_topics.length > 0 ? `
                <p style="margin-top: 1rem; color: var(--text-secondary);">
                    Focus on improving: ${recommendations.weak_topics.slice(0, 3).map(t => t.deck_title).join(', ')}
                </p>
            ` : `
                <p style="margin-top: 1rem; color: var(--text-secondary);">
                    You have no weak topics currently! Great job maintaining your mastery.
                </p>
            `}
            ${scheduleHTML}
        `;
    } catch (error) {
        console.error('Error loading recommendations:', error);
        document.getElementById('recommendationsContent').innerHTML = '<p class="error-text">Failed to load recommendations.</p>';
    }
}

// Generate AI Insights on demand
async function generateAIInsights() {
    const btn = document.getElementById('btnGenerateInsights');
    if (!btn) return;
    
    const originalText = btn.innerHTML;
    btn.innerHTML = '<div class="loader" style="width: 20px; height: 20px; margin: 0;"></div> Generating...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/recommendations/generate', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Reload the recommendations panel to show the new insight
            await loadRecommendations();
        } else if (response.status === 429) {
            // Cooldown active
            alert(data.error || 'Please wait before generating new insights.');
            btn.innerHTML = originalText;
            btn.disabled = false;
        } else {
            alert(data.error || 'Failed to generate insights.');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Error generating AI insights:', error);
        alert('Error connecting to AI service.');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Load stats
async function loadStats() {
    try {
        const response = await fetch('/api/analytics/performance?days=30');
        const data = await response.json();
        const analytics = data.analytics;

        document.getElementById('accuracy').textContent = analytics.accuracy + '%';
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Deck actions
function viewDeck(deckId) {
    window.location.href = `/study/${deckId}`;
}

function studyDeck(deckId) {
    window.location.href = `/study/${deckId}`;
}

function takequiz(deckId) {
    window.location.href = `/quiz/${deckId}`;
}

function editDeck(deckId) {
    window.location.href = `/deck/${deckId}/edit`;
}

async function deleteDeck(deckId) {
    if (!confirm('Are you sure you want to delete this deck?')) {
        return;
    }

    try {
        const response = await fetch(`/api/content/decks/${deckId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadDecks();
        } else {
            alert('Failed to delete deck');
        }
    } catch (error) {
        console.error('Error deleting deck:', error);
        alert('Error deleting deck');
    }
}

async function publishDeck(deckId) {
    if (!confirm('Want to share this deck with the public? 🌐')) {
        return;
    }

    try {
        const response = await fetch('/api/repository/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ deck_id: deckId })
        });

        const data = await response.json();

        if (response.ok) {
            alert('🚀 Success! Your deck is now in the Public Repository.');
            window.location.href = '/repository';
        } else {
            alert(data.error || 'Failed to publish deck');
        }
    } catch (error) {
        console.error('Error publishing deck:', error);
        alert('Error publishing deck');
    }
}

async function unpublishDeck(deckId) {
    if (!confirm('Remove this deck from the Public Repository? Your private copy will be kept.')) {
        return;
    }

    try {
        const response = await fetch(`/api/repository/unpublish/${deckId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            alert('Deck removed from Public Repository.');
            loadDashboard();
        } else {
            alert(data.error || 'Failed to unpublish deck');
        }
    } catch (error) {
        console.error('Error unpublishing deck:', error);
        alert('Error unpublishing deck');
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', loadDashboard);
