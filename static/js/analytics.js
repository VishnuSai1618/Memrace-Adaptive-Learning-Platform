// Analytics functionality

// Load analytics data
async function loadAnalytics() {
    try {
        // Load performance data
        const perfResponse = await fetch('/api/analytics/performance?days=30');
        const perfData = await perfResponse.json();
        const analytics = perfData.analytics;

        // Update stats with animations
        animateNumber('totalReviews', analytics.total_reviews);
        animateNumber('correctReviews', analytics.correct_reviews);
        animateNumber('overallAccuracy', analytics.accuracy, '%');

        const avgTime = analytics.average_response_time
            ? (analytics.average_response_time / 1000).toFixed(1)
            : 0;
        document.getElementById('avgResponseTime').textContent = avgTime + 's';

        // Load weak topics
        await loadWeakTopics();

        // Load deck performance
        renderDeckPerformance(analytics.deck_performance);

        // Render daily activity
        renderDailyActivity(analytics.daily_activity);

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Animate number counting
function animateNumber(elementId, targetValue, suffix = '') {
    const element = document.getElementById(elementId);
    const duration = 1000;
    const steps = 30;
    const increment = targetValue / steps;
    let current = 0;

    const timer = setInterval(() => {
        current += increment;
        if (current >= targetValue) {
            current = targetValue;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + suffix;
    }, duration / steps);
}

// Load weak topics
async function loadWeakTopics() {
    try {
        const response = await fetch('/api/analytics/weak-topics?threshold=0.6');
        const data = await response.json();
        const weakTopics = data.weak_topics;

        const weakTopicsList = document.getElementById('weakTopicsList');

        if (weakTopics.length === 0) {
            weakTopicsList.innerHTML = `
                <div style="text-align: center; padding: 3rem; background: var(--dark-card); border-radius: var(--radius-md);">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
                    <h3 style="color: var(--accent-green); margin-bottom: 0.5rem;">Excellent Work!</h3>
                    <p style="color: var(--text-secondary);">No weak topics found. You're performing great across all decks!</p>
                </div>
            `;
            return;
        }

        weakTopicsList.innerHTML = weakTopics.map(topic => {
            const progressPercent = topic.accuracy;
            const progressColor = progressPercent < 40 ? 'var(--accent-red)' :
                progressPercent < 60 ? 'var(--accent-yellow)' :
                    'var(--accent-green)';

            return `
                <div class="weak-topic-card" style="
                    background: var(--dark-card);
                    padding: 1.5rem;
                    border-radius: var(--radius-md);
                    border-left: 4px solid ${progressColor};
                    transition: all 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='translateX(5px)'" onmouseout="this.style.transform='translateX(0)'">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <h3 style="margin-bottom: 0.5rem;">${topic.deck_title}</h3>
                            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                                ${topic.correct_reviews} / ${topic.total_reviews} correct attempts
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <h2 style="color: ${progressColor}; margin-bottom: 0.5rem;">${topic.accuracy}%</h2>
                            <a href="/study/${topic.deck_id}" class="btn-primary" style="font-size: 0.9rem; padding: 0.5rem 1rem;">
                                📚 Practice Now
                            </a>
                        </div>
                    </div>
                    
                    <!-- Progress Bar -->
                    <div style="background: var(--dark-bg); height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="
                            width: ${progressPercent}%;
                            height: 100%;
                            background: ${progressColor};
                            transition: width 1s ease;
                        "></div>
                    </div>
                    
                    <!-- Recommendation -->
                    <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(99, 102, 241, 0.1); border-radius: var(--radius-sm);">
                        <p style="font-size: 0.85rem; color: var(--primary-purple);">
                            💡 <strong>Tip:</strong> ${getRecommendation(topic.accuracy)}
                        </p>
                    </div>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading weak topics:', error);
    }
}

// Get personalized recommendation based on accuracy
function getRecommendation(accuracy) {
    if (accuracy < 30) {
        return "Review the basics and study the flashcards multiple times before taking quizzes.";
    } else if (accuracy < 50) {
        return "Focus on understanding key concepts. Try studying in shorter, more frequent sessions.";
    } else if (accuracy < 70) {
        return "You're making progress! Review incorrect answers and practice regularly.";
    } else {
        return "Almost there! A few more practice sessions will help you master this topic.";
    }
}

// Render deck performance
function renderDeckPerformance(deckPerformance) {
    const deckPerformanceList = document.getElementById('deckPerformanceList');

    if (!deckPerformance || deckPerformance.length === 0) {
        deckPerformanceList.innerHTML = `
            <div style="text-align: center; padding: 3rem; background: var(--dark-card); border-radius: var(--radius-md);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                <p style="color: var(--text-secondary);">No performance data yet. Start studying to see your progress!</p>
            </div>
        `;
        return;
    }

    deckPerformanceList.innerHTML = deckPerformance.map(deck => {
        const accuracyColor = deck.accuracy >= 80
            ? 'var(--accent-green)'
            : deck.accuracy >= 60
                ? 'var(--accent-yellow)'
                : 'var(--accent-red)';

        const grade = deck.accuracy >= 90 ? 'A+' :
            deck.accuracy >= 80 ? 'A' :
                deck.accuracy >= 70 ? 'B' :
                    deck.accuracy >= 60 ? 'C' :
                        deck.accuracy >= 50 ? 'D' : 'F';

        return `
            <div class="performance-card" style="
                background: var(--dark-card);
                padding: 1.5rem;
                border-radius: var(--radius-md);
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.3s ease;
            " onmouseover="this.style.boxShadow='0 8px 20px rgba(99, 102, 241, 0.2)'" onmouseout="this.style.boxShadow='none'">
                <div style="flex: 1;">
                    <h3 style="margin-bottom: 0.5rem;">${deck.deck_title}</h3>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">
                        ${deck.correct_reviews} / ${deck.total_reviews} correct
                    </p>
                    
                    <!-- Mini Progress Bar -->
                    <div style="margin-top: 0.75rem; background: var(--dark-bg); height: 6px; border-radius: 3px; overflow: hidden; max-width: 200px;">
                        <div style="width: ${deck.accuracy}%; height: 100%; background: ${accuracyColor}; transition: width 1s ease;"></div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="
                        width: 60px;
                        height: 60px;
                        border-radius: 50%;
                        background: ${accuracyColor}20;
                        border: 3px solid ${accuracyColor};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 0.5rem;
                    ">
                        <span style="font-size: 1.5rem; font-weight: bold; color: ${accuracyColor};">${grade}</span>
                    </div>
                    <p style="color: ${accuracyColor}; font-weight: bold;">${deck.accuracy}%</p>
                </div>
            </div>
        `;
    }).join('');
}

// Render daily activity
function renderDailyActivity(dailyActivity) {
    const activityChart = document.getElementById('dailyActivityChart');

    if (!dailyActivity || Object.keys(dailyActivity).length === 0) {
        activityChart.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📅</div>
                <p style="color: var(--text-secondary);">No activity data yet. Start studying to track your progress!</p>
            </div>
        `;
        return;
    }

    // Simple bar chart visualization
    const dates = Object.keys(dailyActivity).sort();
    const maxTotal = Math.max(...dates.map(date => dailyActivity[date].total));

    activityChart.innerHTML = `
        <div style="display: flex; align-items: flex-end; gap: 0.5rem; height: 250px; padding: 1rem;">
            ${dates.slice(-14).map(date => {
        const data = dailyActivity[date];
        const height = (data.total / maxTotal) * 100;
        const accuracy = (data.correct / data.total) * 100;
        const color = accuracy >= 70 ? 'var(--accent-green)' :
            accuracy >= 50 ? 'var(--accent-yellow)' :
                'var(--accent-red)';

        return `
                    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; position: relative; group;">
                        <div style="
                            width: 100%; 
                            height: ${height}%; 
                            background: linear-gradient(to top, ${color}, ${color}80); 
                            border-radius: 4px 4px 0 0;
                            min-height: 10px;
                            transition: all 0.3s ease;
                            cursor: pointer;
                        " 
                        onmouseover="this.style.opacity='0.8'; this.nextElementSibling.style.display='block';" 
                        onmouseout="this.style.opacity='1'; this.nextElementSibling.style.display='none';"
                        ></div>
                        
                        <!-- Tooltip -->
                        <div style="
                            display: none;
                            position: absolute;
                            bottom: ${height + 10}%;
                            background: var(--dark-card);
                            padding: 0.5rem;
                            border-radius: var(--radius-sm);
                            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                            white-space: nowrap;
                            z-index: 10;
                        ">
                            <p style="font-size: 0.8rem; margin-bottom: 0.25rem;">${date}</p>
                            <p style="font-size: 0.75rem; color: var(--text-secondary);">${data.total} reviews</p>
                            <p style="font-size: 0.75rem; color: ${color};">${accuracy.toFixed(1)}% accuracy</p>
                        </div>
                        
                        <span style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.5rem;">
                            ${new Date(date).getDate()}
                        </span>
                    </div>
                `;
    }).join('')}
        </div>
        <p style="text-align: center; color: var(--text-secondary); margin-top: 1rem; font-size: 0.9rem;">
            📊 Last 14 days activity • Hover over bars for details
        </p>
    `;
}

// Initialize
document.addEventListener('DOMContentLoaded', loadAnalytics);
