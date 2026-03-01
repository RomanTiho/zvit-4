// Auth Navigation Helper
// Додає динамічну навігацію для авторизації на всіх сторінках

function initAuthNav() {
    const token = localStorage.getItem('access_token');
    const navContent = document.querySelector('.nav-content');

    if (!navContent) return;

    // Highlight active link
    const path = window.location.pathname;
    const mainLinks = document.querySelectorAll('#mainNavLinks a');
    mainLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === path || (path === '/' && href === '/index.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    const authContainer = document.getElementById('authNavContainer');
    if (!authContainer) return;

    // Clear existing
    authContainer.innerHTML = '';

    if (token) {
        // Показати кнопку Створити турнір на сторінці турнірів
        if (window.location.pathname.includes('tournaments.html') || path === '/') {
            const createBtn = document.getElementById('createTournamentBtn');
            if (createBtn) createBtn.style.display = 'block';
        }

        // Користувач увійшов - показати кнопку Профілю
        const profileBtn = document.createElement('button');
        profileBtn.className = 'btn btn-secondary auth-nav-btn';
        profileBtn.innerHTML = '👤 Мій профіль';
        profileBtn.style.marginRight = '0.5rem';
        profileBtn.addEventListener('click', () => {
            window.location.href = 'profile.html';
        });

        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'btn btn-outline auth-nav-btn';
        logoutBtn.innerHTML = 'Вийти';
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await logout();
        });

        authContainer.appendChild(profileBtn);
        authContainer.appendChild(logoutBtn);
    } else {
        // Користувач не увійшов - показати кнопку Входу
        const loginBtn = document.createElement('button');
        loginBtn.className = 'btn btn-primary auth-nav-btn';
        loginBtn.innerHTML = 'Вхід';
        loginBtn.addEventListener('click', () => {
            window.location.href = 'auth.html';
        });

        authContainer.appendChild(loginBtn);
    }
}

async function logout() {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');

    try {
        await fetch(`${CONFIG.API_BASE_URL}/auth/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    if (typeof showToast === 'function') {
        showToast('Ви вийшли з системи', 'success');
    }

    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

// Ініціалізувати при завантаженні сторінки
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuthNav);
} else {
    initAuthNav();
}
