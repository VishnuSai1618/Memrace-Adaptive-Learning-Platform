/**
 * theme.js — Dark / Light mode toggle
 * Loads saved preference from localStorage before first paint (no flash).
 */
(function () {
    const STORAGE_KEY = 'memrace-theme';

    // ── Apply saved theme immediately (before render) ──
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'light') {
        document.documentElement.classList.add('light-mode-pending');
    }

    // ── After DOM ready, wire up the button ──
    document.addEventListener('DOMContentLoaded', function () {

        // Move class from <html> to <body> now that <body> exists
        if (document.documentElement.classList.contains('light-mode-pending')) {
            document.documentElement.classList.remove('light-mode-pending');
            document.body.classList.add('light-mode');
        }

        const btn = document.getElementById('theme-toggle-btn');
        if (!btn) return;

        // Set correct icon on load
        _syncIcon(btn);

        // ── Restore saved position ──
        const POS_STORAGE_KEY = 'memrace-theme-pos';
        const savedPos = localStorage.getItem(POS_STORAGE_KEY);
        if (savedPos) {
            try {
                const pos = JSON.parse(savedPos);
                // Fallback sizes if offset bounds aren't fully computed yet
                const btnW = btn.offsetWidth || 50;
                const btnH = btn.offsetHeight || 50;
                const maxX = window.innerWidth - btnW;
                const maxY = window.innerHeight - btnH;
                
                // Only restore if coordinates are completely within visible window
                if (pos.left >= 0 && pos.left <= maxX && pos.top >= 0 && pos.top <= maxY) {
                    btn.style.left = pos.left + 'px';
                    btn.style.top = pos.top + 'px';
                    btn.style.bottom = 'auto'; // Disable CSS bottom
                    btn.style.right = 'auto';  // Disable CSS right
                } else {
                    // Out of bounds: clear corrupted data and rely on CSS default position
                    localStorage.removeItem(POS_STORAGE_KEY);
                }
            } catch (e) {}
        }

        // ── Drag Logic ──
        let isDragging = false;
        let dragHasMoved = false;
        let initialX, initialY, startX, startY;

        btn.addEventListener('pointerdown', function (e) {
            if (e.button !== 0) return; // Only default (left) click
            isDragging = true;
            dragHasMoved = false;
            
            const rect = btn.getBoundingClientRect();
            initialX = rect.left;
            initialY = rect.top;
            startX = e.clientX;
            startY = e.clientY;
            
            btn.classList.add('dragging');
            btn.setPointerCapture(e.pointerId);
        });

        btn.addEventListener('pointermove', function (e) {
            if (!isDragging) return;
            
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            // Allow minor jitter without triggering a drag move
            if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
                dragHasMoved = true;
            }
            
            if (dragHasMoved) {
                let newX = initialX + dx;
                let newY = initialY + dy;
                
                // Keep within viewport bounds
                const maxX = window.innerWidth - btn.offsetWidth;
                const maxY = window.innerHeight - btn.offsetHeight;
                newX = Math.max(0, Math.min(newX, maxX));
                newY = Math.max(0, Math.min(newY, maxY));
                
                btn.style.left = newX + 'px';
                btn.style.top = newY + 'px';
                btn.style.bottom = 'auto';
                btn.style.right = 'auto';
            }
        });

        btn.addEventListener('pointerup', function (e) {
            if (!isDragging) return;
            isDragging = false;
            btn.classList.remove('dragging');
            btn.releasePointerCapture(e.pointerId);
            
            if (dragHasMoved) {
                // Save new position
                localStorage.setItem(POS_STORAGE_KEY, JSON.stringify({
                    left: parseInt(btn.style.left),
                    top: parseInt(btn.style.top)
                }));
            } else {
                // Just a click: toggle theme
                const isLight = document.body.classList.toggle('light-mode');
                localStorage.setItem(STORAGE_KEY, isLight ? 'light' : 'dark');
                _syncIcon(btn);
            }
        });

        // Keep in bounds on resize
        window.addEventListener('resize', function () {
            if (btn.style.left) {
                const rect = btn.getBoundingClientRect();
                const maxX = window.innerWidth - btn.offsetWidth;
                const maxY = window.innerHeight - btn.offsetHeight;
                if (rect.left > maxX || rect.top > maxY) {
                    btn.style.left = Math.min(rect.left, maxX) + 'px';
                    btn.style.top = Math.min(rect.top, maxY) + 'px';
                    localStorage.setItem(POS_STORAGE_KEY, JSON.stringify({
                        left: parseInt(btn.style.left),
                        top: parseInt(btn.style.top)
                    }));
                }
            }
        });
    });

    function _syncIcon(btn) {
        const isLight = document.body.classList.contains('light-mode');
        btn.textContent   = isLight ? '☀️' : '🌙';
        btn.title         = isLight ? 'Switch to Dark Mode' : 'Switch to Light Mode';
        btn.setAttribute('aria-label', btn.title);
    }
})();
