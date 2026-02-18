// Auth Navigation Helper
// Додає динамічну навігацію для авторизації на всіх сторінках

function initAuthNav() {
    const token = localStorage.getItem('access_token');
    const navContent = document.querySelector('.nav-content');

    if (!navContent) return;

    // Видалити старі auth кнопки якщо є
    const existingAuthBtns = navContent.querySelectorAll('.auth-nav-btn');
    existingAuthBtns.forEach(btn => btn.remove());

    // Видалити старе посилання на рейтинг якщо є
    const existingRatingLink = navContent.querySelector('.rating-nav-link');
    if (existingRatingLink) {
        existingRatingLink.remove();
    }

    if (token) {
        // Додати посилання "Рейтинг" до nav-links для авторизованих користувачів
        const navLinks = navContent.querySelector('.nav-links');
        if (navLinks) {
            const ratingLi = document.createElement('li');
            ratingLi.className = 'rating-nav-link';
            const ratingLink = document.createElement('a');
            ratingLink.href = 'players.html';
            ratingLink.textContent = 'Рейтинг';
            ratingLi.appendChild(ratingLink);
            navLinks.appendChild(ratingLi);
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
        logoutBtn.style.marginRight = '0.5rem';
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await logout();
        });

        // Вставити після nav-links
        if (navLinks) {
            navLinks.insertAdjacentElement('afterend', profileBtn);
            profileBtn.insertAdjacentElement('afterend', logoutBtn);
        }
    } else {
        // Користувач не увійшов - показати кнопку Входу
        const loginBtn = document.createElement('button');
        loginBtn.className = 'btn btn-primary auth-nav-btn';
        loginBtn.innerHTML = 'Вхід';
        loginBtn.style.marginRight = '0.5rem';
        loginBtn.addEventListener('click', () => {
            window.location.href = 'auth.html';
        });

        // Вставити після nav-links
        const navLinks = navContent.querySelector('.nav-links');
        if (navLinks) {
            navLinks.insertAdjacentElement('afterend', loginBtn);
        }
    }
}

async function logout() {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');

    try {
        await fetch('http://localhost:8001/api/auth/logout/', {
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
