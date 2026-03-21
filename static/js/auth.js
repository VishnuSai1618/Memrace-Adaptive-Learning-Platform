// Authentication helper functions

// Check if user is authenticated
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check');
        const data = await response.json();
        return data.authenticated;
    } catch (error) {
        console.error('Auth check failed:', error);
        return false;
    }
}

// Logout function
async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// Attach logout to button if it exists
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});

// Protect pages that require authentication
async function protectPage() {
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) {
        window.location.href = '/login';
    }
}

// Auto-protect dashboard pages — public pages are explicitly whitelisted
const PUBLIC_PATHS = ['/', '/login', '/signup', '/forgot-password'];
const isPublicPage = PUBLIC_PATHS.includes(window.location.pathname) ||
                     window.location.pathname.startsWith('/reset-password/');

if (!isPublicPage) {
    protectPage();
}
