// ===== Global State Management =====
const DATA_VERSION = 5; // bump this to force localStorage reset
const AppState = {
    tournaments: [],
    currentTournament: null,
};

// ===== Local Storage Helper =====
const Storage = {
    save(key, data) {
        localStorage.setItem(key, JSON.stringify(data));
    },
    load(key) {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    },
    clear(key) {
        localStorage.removeItem(key);
    }
};

// Data is now loaded dynamically from the backend

// ===== Modal Management =====
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// ===== Navigation Handlers =====
function setupNavigation() {
    // Create tournament buttons
    const createBtns = document.querySelectorAll('#createTournamentBtn, #heroCreateBtn, #ctaCreateBtn');
    createBtns.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                // Check if we're already on tournaments page
                if (window.location.pathname.includes('tournaments.html')) {
                    openModal('createTournamentModal');
                } else {
                    window.location.href = 'tournaments.html?create=true';
                }
            });
        }
    });

    // Explore tournaments button
    const exploreBtn = document.getElementById('heroExploreBtn');
    if (exploreBtn) {
        exploreBtn.addEventListener('click', () => {
            window.location.href = 'tournaments.html';
        });
    }
}

// ===== Format Date Helper =====
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('uk-UA', options);
}

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    const dateOptions = { day: 'numeric', month: 'long', year: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('uk-UA', dateOptions) + ' о ' + date.toLocaleTimeString('uk-UA', timeOptions);
}

// ===== Get Status Badge =====
function getStatusBadge(status) {
    const statusMap = {
        'upcoming': 'Майбутній',
        'ongoing': 'Поточний',
        'completed': 'Завершений'
    };
    return statusMap[status] || status;
}

function getFormatName(format) {
    const formatMap = {
        'league': 'Ліга',
        'knockout': 'Плей-офф',
        'mixed': 'Змішаний'
    };
    return formatMap[format] || format;
}

// ===== Initialize App =====
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();

    // Add smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Navbar scroll effect
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            navbar.style.boxShadow = 'var(--shadow-md)';
        } else {
            navbar.style.boxShadow = 'none';
        }

        lastScroll = currentScroll;
    });
});
