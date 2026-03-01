// Admin Panel JavaScript

// Admin password (in production, this should be handled server-side)
const ADMIN_PASSWORD = 'admin123';
const AUTH_KEY = 'footballhub_admin_auth';

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function () {
    checkAuthentication();
    setupEventListeners();
});

// Check if admin is authenticated
function checkAuthentication() {
    const isAuthenticated = sessionStorage.getItem(AUTH_KEY) === 'true';

    if (isAuthenticated) {
        showAdminPanel();
        loadRequests();
        loadTournaments();
    } else {
        showLoginSection();
    }
}

// Show login section
function showLoginSection() {
    const loginSection = document.getElementById('loginSection');
    loginSection.style.display = 'flex';
    loginSection.style.position = 'fixed';
    loginSection.style.alignItems = 'center';
    loginSection.style.justifyContent = 'center';
    loginSection.style.visibility = 'visible';
    loginSection.style.zIndex = '9999';

    document.getElementById('adminPanel').style.display = 'none';
    const navbar = document.getElementById('adminNavbar');
    if (navbar) navbar.style.display = 'none';
}

// Show admin panel
function showAdminPanel() {
    const loginSection = document.getElementById('loginSection');
    loginSection.style.display = 'none';
    loginSection.style.position = 'static';
    loginSection.style.visibility = 'hidden';
    loginSection.style.zIndex = '-1';

    document.getElementById('adminPanel').style.display = 'block';
    const navbar = document.getElementById('adminNavbar');
    if (navbar) navbar.style.display = 'block';
}

// Setup event listeners
function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    // Clear cache button
    const clearCacheBtn = document.getElementById('clearCacheBtn');
    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', handleClearCache);
    }

    // Admin tabs
    const tabs = document.querySelectorAll('.admin-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Admin create tournament form
    const adminCreateForm = document.getElementById('adminCreateTournamentForm');
    if (adminCreateForm) {
        adminCreateForm.addEventListener('submit', handleAdminCreateTournament);
    }
}

// Handle login
function handleLogin(e) {
    e.preventDefault();

    const password = document.getElementById('adminPassword').value;

    if (password === ADMIN_PASSWORD) {
        sessionStorage.setItem(AUTH_KEY, 'true');
        showAdminPanel();
        loadRequests();
        loadTournaments();

        // Show welcome message
        showWelcomeMessage();
    } else {
        showError('Невірний пароль! Спробуйте ще раз.');
        document.getElementById('adminPassword').value = '';
    }
}

// Show welcome message
function showWelcomeMessage() {
    const welcomeMessage = document.getElementById('welcomeMessage');
    welcomeMessage.style.display = 'flex';

    // Hide after 5 seconds with fade out
    setTimeout(() => {
        welcomeMessage.style.transition = 'opacity 0.5s ease-out';
        welcomeMessage.style.opacity = '0';

        setTimeout(() => {
            welcomeMessage.style.display = 'none';
            welcomeMessage.style.opacity = '1';
        }, 500);
    }, 5000);
}

// Handle logout
function handleLogout() {
    showConfirm('Ви впевнені, що хочете вийти?', () => {
        sessionStorage.removeItem(AUTH_KEY);
        showLoginSection();
        document.getElementById('loginForm').reset();
    });
}

// Handle clear cache
function handleClearCache() {
    showConfirm('Очистити старі дані автентифікації з localStorage?\n\nЦе видалить старі записи, які могли залишитися з попередніх версій системи.', () => {
        // Clear old localStorage auth
        localStorage.removeItem(AUTH_KEY);

        // Also clear from sessionStorage for completeness
        sessionStorage.removeItem(AUTH_KEY);

        showSuccess('Кеш успішно очищено!\n\nСтарі дані автентифікації видалено з localStorage та sessionStorage.');
    });
}

// Switch between tabs
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.admin-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.admin-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');

    // Load data if needed
    if (tabName === 'requests') {
        loadRequests();
    } else if (tabName === 'tournaments') {
        loadTournaments();
    }
}

// Load user requests
function loadRequests() {
    const requests = Storage.load('tournamentRequests') || [];
    const requestsList = document.getElementById('requestsList');
    const requestsCount = document.getElementById('requestsCount');

    requestsCount.textContent = requests.length;

    if (requests.length === 0) {
        requestsList.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                    <rect x="12" y="16" width="40" height="36" rx="4" stroke="currentColor" stroke-width="3"/>
                    <path d="M20 28H44M20 36H36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                </svg>
                <h3>Немає запитів</h3>
                <p>Поки що користувачі не надсилали запитів на створення турнірів</p>
            </div>
        `;
        return;
    }

    requestsList.innerHTML = requests.map(request => `
        <div class="request-card" data-request-id="${request.id}">
            <div class="request-header">
                <div class="request-info">
                    <h3>${request.tournamentName}</h3>
                    <div class="request-date">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M8 4V8L10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        ${formatDate(request.submittedAt)}
                    </div>
                </div>
                <div class="request-actions">
                    <button class="btn btn-primary btn-small" onclick="createFromRequest(${request.id})">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M8 5V11M5 8H11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        Створити
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="deleteRequest(${request.id})">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        Видалити
                    </button>
                </div>
            </div>
            <div class="request-body">
                <div class="request-field">
                    <strong>Контакт:</strong> <span>${request.contactName} (${request.contactEmail}, ${request.contactPhone})</span>
                </div>
                <div class="request-field">
                    <strong>Локація:</strong> <span>${request.location}</span>
                </div>
                <div class="request-field">
                    <strong>Дати:</strong> <span>${formatDate(request.start_date)} - ${formatDate(request.end_date)}</span>
                </div>
                <div class="request-field">
                    <strong>Формат:</strong> <span>${getFormatName(request.format)}</span>
                </div>
                <div class="request-field">
                    <strong>Максимум команд:</strong> <span>${request.max_teams}</span>
                </div>
                <div class="request-description">
                    <strong>Опис:</strong><br>
                    ${request.description}
                </div>
            </div>
        </div>
    `).join('');
}

// Create tournament from request
window.createFromRequest = function (requestId) {
    const requests = Storage.load('tournamentRequests') || [];
    const request = requests.find(r => r.id === requestId);

    if (!request) {
        showError('Запит не знайдено!');
        return;
    }

    showConfirm(`Створити турнір "${request.tournamentName}"?`, () => {
        const newTournament = {
            id: Date.now(),
            name: request.tournamentName,
            startDate: request.start_date,
            endDate: request.end_date,
            format: request.format,
            maxTeams: parseInt(request.max_teams),
            location: request.location,
            description: request.description,
            status: 'upcoming',
            teams: [],
            standings: [],
            matches: []
        };

        // Add tournament
        AppState.tournaments.push(newTournament);
        Storage.save('tournaments', AppState.tournaments);

        // Remove request
        const updatedRequests = requests.filter(r => r.id !== requestId);
        Storage.save('tournamentRequests', updatedRequests);

        // Reload
        loadRequests();
        loadTournaments();

        showSuccess('Турнір успішно створено!');
    });
};

// Delete request
window.deleteRequest = function (requestId) {
    showConfirm('Ви впевнені, що хочете видалити цей запит?', () => {
        const requests = Storage.load('tournamentRequests') || [];
        const updatedRequests = requests.filter(r => r.id !== requestId);
        Storage.save('tournamentRequests', updatedRequests);
        loadRequests();
        showSuccess('Запит видалено!');
    });
};

// Handle admin create tournament
function handleAdminCreateTournament(e) {
    e.preventDefault();

    const formData = {
        id: Date.now(),
        name: document.getElementById('adminTournamentName').value,
        startDate: document.getElementById('adminStartDate').value,
        endDate: document.getElementById('adminEndDate').value,
        format: document.getElementById('adminFormat').value,
        maxTeams: parseInt(document.getElementById('adminMaxTeams').value),
        location: document.getElementById('adminLocation').value,
        description: document.getElementById('adminDescription').value,
        status: 'upcoming',
        teams: [],
        standings: [],
        matches: []
    };

    // Validate dates
    if (new Date(formData.start_date) >= new Date(formData.end_date)) {
        showError('Дата завершення повинна бути пізніше дати початку');
        return;
    }

    // Add to tournaments
    AppState.tournaments.push(formData);
    Storage.save('tournaments', AppState.tournaments);

    // Reset form
    e.target.reset();

    // Show success message
    showSuccess('Турнір успішно створено!');

    // Switch to tournaments tab
    switchTab('tournaments');
}

// Load all tournaments
async function loadTournaments() {
    try {
        const response = await TournamentsAPI.getTournaments();
        AppState.tournaments = response.results || response;
    } catch (error) {
        console.error('Failed to load tournaments:', error);
        AppState.tournaments = [];
    }
    const tournaments = AppState.tournaments || [];
    const tournamentsList = document.getElementById('adminTournamentsList');

    if (tournaments.length === 0) {
        tournamentsList.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                    <path d="M32 8L36 24H52L39 34L43 50L32 42L21 50L25 34L12 24H28L32 8Z" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/>
                </svg>
                <h3>Немає турнірів</h3>
                <p>Створіть перший турнір або обробіть запити користувачів</p>
            </div>
        `;
        return;
    }

    tournamentsList.innerHTML = tournaments.map(tournament => `
        <div class="admin-tournament-card">
            <div class="admin-tournament-header">
                <span class="tournament-status">${getStatusBadge(tournament.status)}</span>
                <h3>${tournament.name}</h3>
                <div class="admin-tournament-dates">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <rect x="2" y="3" width="12" height="11" rx="2" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M2 6H14M5 1V5M11 1V5" stroke="currentColor" stroke-width="1.5"/>
                    </svg>
                    ${formatDate(tournament.start_date)} - ${formatDate(tournament.end_date)}
                </div>
            </div>
            <div class="admin-tournament-body">
                <div class="admin-tournament-info">
                    <div class="info-row">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M8 2C8 2 4 4 4 8C4 12 8 14 8 14C8 14 12 12 12 8C12 4 8 2 8 2Z" stroke="currentColor" stroke-width="1.5"/>
                            <circle cx="8" cy="8" r="1.5" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span>${tournament.location}</span>
                    </div>
                    <div class="info-row">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <rect x="2" y="3" width="12" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M2 6H14" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span>${getFormatName(tournament.format)}</span>
                    </div>
                    <div class="info-row">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <circle cx="6" cy="6" r="2" stroke="currentColor" stroke-width="1.5"/>
                            <circle cx="10" cy="6" r="2" stroke="currentColor" stroke-width="1.5"/>
                            <circle cx="8" cy="11" r="2" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span>${tournament.teams.length} / ${tournament.max_teams} команд</span>
                    </div>
                </div>
                <div class="admin-tournament-actions">
                    <button class="btn btn-primary btn-small" onclick="viewTournamentAsAdmin(${tournament.id})" style="flex: 1;">
                        Переглянути
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="deleteTournament(${tournament.id})" style="flex: 1;">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M2 4H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            <path d="M5.5 4V3C5.5 2.5 6 2 6.5 2H9.5C10 2 10.5 2.5 10.5 3V4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            <path d="M3 4L4 13C4 13.5 4.5 14 5 14H11C11.5 14 12 13.5 12 13L13 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M6.5 7V11M9.5 7V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        Видалити
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// View tournament as admin (preserves admin auth)
window.viewTournamentAsAdmin = function (tournamentId) {
    // Temporarily store admin auth in localStorage for transfer
    localStorage.setItem('footballhub_admin_transfer', 'true');
    // Navigate to tournament
    window.location.href = `tournament-detail.html?id=${tournamentId}`;
};

// Delete tournament
window.deleteTournament = async function (tournamentId) {
    const tournament = AppState.tournaments.find(t => t.id === tournamentId);

    if (!tournament) {
        showError('Турнір не знайдено!');
        return;
    }

    showConfirm(`Ви впевнені, що хочете видалити турнір "${tournament.name}"?`, async () => {
        try {
            await APIClient._fetch(`${CONFIG.API_BASE_URL}/tournaments/${tournamentId}/`, { method: 'DELETE' });
            await loadTournaments();
            showSuccess('Турнір видалено!');
        } catch (error) {
            showError('Помилка видалення: ' + error.message);
        }
    });
};

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const months = ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня',
        'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня'];
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
}

// Helper function to get format name
function getFormatName(format) {
    const formats = {
        'league': 'Лігова система',
        'knockout': 'Плей-офф',
        'mixed': 'Змішаний формат'
    };
    return formats[format] || format;
}

// Helper function to get status badge
function getStatusBadge(status) {
    const statusMap = {
        'upcoming': 'Майбутній',
        'ongoing': 'Поточний',
        'completed': 'Завершений'
    };
    return statusMap[status] || status;
}
