// ===== Global State Management =====
const DATA_VERSION = 5; // bump this to force localStorage reset
const AppState = {
    tournaments: [],
    currentTournament: null,
};

// ===== Local Storage Helper (Switched to Session Storage for tab isolation) =====
const Storage = {
    save(key, data) {
        sessionStorage.setItem(key, JSON.stringify(data));
    },
    load(key) {
        const data = sessionStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    },
    clear(key) {
        sessionStorage.removeItem(key);
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

// ===== Hero Carousel =====
function initHeroCarousel() {
    const slides = document.querySelectorAll('.carousel-slide');
    if (!slides.length) return;
    
    let currentSlide = 0;
    setInterval(() => {
        slides[currentSlide].classList.remove('active');
        currentSlide = (currentSlide + 1) % slides.length;
        slides[currentSlide].classList.add('active');
    }, 5000);
}

// ===== Live Hero Stats =====
async function loadHeroStats() {
    const apiBase = (typeof CONFIG !== 'undefined') ? CONFIG.API_BASE_URL : '/api';
    try {
        const [tourRes, teamsRes, playersRes, matchesRes] = await Promise.all([
            fetch(`${apiBase}/tournaments/`),
            fetch(`${apiBase}/teams/`),
            fetch(`${apiBase}/players/`),
            fetch(`${apiBase}/matches/`),
        ]);
        const [tourData, teamsData, playersData, matchesData] = await Promise.all([
            tourRes.json(), teamsRes.json(), playersRes.json(), matchesRes.json()
        ]);

        const counts = {
            statTournaments: tourData.count ?? (Array.isArray(tourData) ? tourData.length : '?'),
            statTeams:       teamsData.count ?? (Array.isArray(teamsData) ? teamsData.length : '?'),
            statPlayers:     playersData.count ?? (Array.isArray(playersData) ? playersData.length : '?'),
            statMatches:     matchesData.count ?? (Array.isArray(matchesData) ? matchesData.length : '?'),
        };

        Object.entries(counts).forEach(([id, val]) => {
            const el = document.getElementById(id);
            if (!el || typeof val !== 'number') { if (el) el.textContent = val; return; }
            // Animate counter
            let start = 0;
            const step = Math.ceil(val / 40);
            const timer = setInterval(() => {
                start += step;
                if (start >= val) { el.textContent = val; clearInterval(timer); }
                else { el.textContent = start; }
            }, 30);
        });
    } catch (e) {
        console.warn('Could not load hero stats', e);
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
    initHeroCarousel();
    loadHeroStats();
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
