// ===== Tournaments Page JavaScript =====
// Map removed

// ===== Render Tournaments Grid =====
function renderTournaments(tournaments) {
    const grid = document.getElementById('tournamentsGrid');
    if (!grid) return;

    if (tournaments.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: var(--spacing-3xl);">
                <h3 style="font-size: var(--font-size-2xl); color: var(--dark-600); margin-bottom: var(--spacing-md);">
                    Турнірів не знайдено
                </h3>
                <p style="color: var(--dark-500); margin-bottom: var(--spacing-lg);">
                    Спробуйте змінити фільтри або зверніться до тренера для створення турніру
                </p>
            </div>
        `;
        return;
    }

    grid.innerHTML = tournaments.map(tournament => {
        const bgStyle = tournament.image || tournament.image_base64 ? 
            `style="background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url('${tournament.image || tournament.image_base64}'); background-size: cover; background-position: center;"` : 
            '';
        
        return `
        <div class="tournament-card" onclick="viewTournament(${tournament.id})">
            <div class="tournament-header" ${bgStyle}>
                <div class="tournament-status">${getStatusBadge(tournament.status)}</div>
                <h3>${tournament.name}</h3>
                <div class="tournament-dates">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <rect x="2" y="3" width="12" height="11" rx="2" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M2 6H14M5 1V5M11 1V5" stroke="currentColor" stroke-width="1.5"/>
                    </svg>
                    ${formatDate(tournament.start_date)} - ${formatDate(tournament.end_date)}
                </div>
            </div>
            <div class="tournament-body">
                <div class="tournament-info">
                    <div class="info-row">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <path d="M9 2C9 2 5 5 5 9C5 13 9 16 9 16C9 16 13 13 13 9C13 5 9 2 9 2Z" stroke="currentColor" stroke-width="1.5"/>
                            <circle cx="9" cy="9" r="2" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span>${tournament.location}</span>
                    </div>
                    <div class="info-row">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <rect x="2" y="4" width="14" height="11" rx="2" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M2 7H16" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span>${getFormatName(tournament.format)}</span>
                    </div>
                </div>
                <p class="tournament-description">${tournament.description}</p>
                <div class="tournament-footer">
                    <span class="teams-count">
                        ${tournament.teams.length} / ${tournament.max_teams} команд
                    </span>
                    <button class="btn btn-primary btn-small" onclick="event.stopPropagation(); viewTournament(${tournament.id})">
                        Детальніше
                    </button>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

// ===== Filter Tournaments =====
function filterTournaments() {
    // Reset to page 1 and fetch from backend with filters
    loadTournamentsPage(1);
}

// ===== View Tournament Details =====
function viewTournament(tournamentId) {
    Storage.save('currentTournamentId', tournamentId);
    window.location.href = 'tournament-detail.html';
}

// ===== Modal Handlers =====
function setupModalHandlers() {
    const modal = document.getElementById('createTournamentModal');
    const closeBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelFormBtn');
    const overlay = modal?.querySelector('.modal-overlay');

    if (closeBtn) {
        closeBtn.addEventListener('click', () => closeModal('createTournamentModal'));
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => closeModal('createTournamentModal'));
    }

    if (overlay) {
        overlay.addEventListener('click', () => closeModal('createTournamentModal'));
    }

    // Form submission
    const form = document.getElementById('createTournamentForm');
    if (form) {
        form.addEventListener('submit', handleCreateTournament);
    }
}

// ===== Create Tournament Handler (Now saves as request) =====
function handleCreateTournament(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('tournamentImage');
    const file = fileInput ? fileInput.files[0] : null;

    if (file) {
        const reader = new FileReader();
        reader.onloadend = () => {
            saveTournamentRequest(reader.result);
        };
        reader.readAsDataURL(file);
    } else {
        saveTournamentRequest(null);
    }
}

function saveTournamentRequest(imageBase64) {
    const requestData = {
        id: Date.now(),
        contactName: document.getElementById('contactName').value,
        contactEmail: document.getElementById('contactEmail').value,
        contactPhone: document.getElementById('contactPhone').value,
        tournamentName: document.getElementById('tournamentName').value,
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        format: document.getElementById('format').value,
        max_teams: parseInt(document.getElementById('maxTeams').value),
        location: document.getElementById('location').value,
        description: document.getElementById('description').value || 'Немає додаткової інформації',
        image_base64: imageBase64,
        submittedAt: new Date().toISOString(),
        status: 'pending'
    };

    // Validate dates
    const today = new Date();
    today.setHours(0,0,0,0);
    const startDateObj = new Date(requestData.start_date);
    
    if (startDateObj < today) {
        showError('Дата початку турніру не може бути в минулому');
        return;
    }

    if (startDateObj >= new Date(requestData.end_date)) {
        showError('Дата завершення повинна бути пізніше дати початку');
        return;
    }

    // Get existing requests
    const requests = Storage.load('tournamentRequests') || [];

    // Add new request
    requests.push(requestData);
    Storage.save('tournamentRequests', requests);

    // Reset form and close modal
    document.getElementById('createTournamentForm').reset();
    closeModal('createTournamentModal');

    // Show success message
    showSuccess('Дякуємо! Ваш запит успішно надіслано. Наш менеджер зв\'яжеться з вами найближчим часом.');
}

// ===== Pagination Data =====
let currentPage = 1;
let totalPages = 1;

// ===== Load Tournaments =====
async function loadTournamentsPage(page = 1) {
    currentPage = page;
    
    // Get filter values
    const statusFilter = document.getElementById('statusFilter')?.value || 'all';
    const formatFilter = document.getElementById('formatFilter')?.value || 'all';
    const searchQuery = document.getElementById('searchInput')?.value || '';

    const params = { page: currentPage };
    if (statusFilter !== 'all') params.status = statusFilter;
    if (formatFilter !== 'all') params.format = formatFilter;
    if (searchQuery) params.search = searchQuery;

    try {
        const response = await TournamentsAPI.getTournaments(params);
        if (response.results) {
            AppState.tournaments = response.results;
            const pageSize = 3; // Matching DRF page size
            totalPages = Math.ceil(response.count / pageSize);
        } else {
            AppState.tournaments = response;
            totalPages = 1;
        }
        
        renderTournaments(AppState.tournaments);
        renderPaginationControl();
    } catch (error) {
        console.error('Failed to load tournaments:', error);
        renderTournaments([]);
    }
}

function renderPaginationControl() {
    let btnContainer = document.getElementById('paginationControls');
    if (!btnContainer) {
        btnContainer = document.createElement('div');
        btnContainer.id = 'paginationControls';
        btnContainer.style.marginTop = 'var(--spacing-xl)';
        document.querySelector('.tournaments-section .container').appendChild(btnContainer);
    }
    
    if (totalPages > 1) {
        let html = '';
        html += `<button class="btn btn-outline" style="padding: 0.5rem 1rem; ${currentPage === 1 ? 'opacity:0.5; cursor:not-allowed;' : ''}" ${currentPage === 1 ? 'disabled' : ''} onclick="loadTournamentsPage(${currentPage - 1})">← Назад</button>`;
        
        for (let i = 1; i <= totalPages; i++) {
            const activeClass = i === currentPage ? 'btn-primary' : 'btn-outline';
            html += `<button class="btn ${activeClass}" style="padding: 0.5rem 1rem;" onclick="loadTournamentsPage(${i})">${i}</button>`;
        }
        
        html += `<button class="btn btn-outline" style="padding: 0.5rem 1rem; ${currentPage === totalPages ? 'opacity:0.5; cursor:not-allowed;' : ''}" ${currentPage === totalPages ? 'disabled' : ''} onclick="loadTournamentsPage(${currentPage + 1})">Далі →</button>`;
        
        btnContainer.innerHTML = `<div style="display:flex; justify-content:center; gap:0.5rem; flex-wrap:wrap;">${html}</div>`;
    } else {
        btnContainer.innerHTML = '';
    }
}

window.loadTournamentsPage = loadTournamentsPage;

// ===== Initialize Tournaments Page =====
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on tournaments page
    if (document.getElementById('tournamentsGrid')) {
        loadTournamentsPage(1);
        setupModalHandlers();

        // Setup filters
        const statusFilter = document.getElementById('statusFilter');
        const formatFilter = document.getElementById('formatFilter');
        const searchInput = document.getElementById('searchInput');

        if (statusFilter) statusFilter.addEventListener('change', filterTournaments);
        if (formatFilter) formatFilter.addEventListener('change', filterTournaments);
        if (searchInput) {
            searchInput.addEventListener('input', filterTournaments);
        }

        // Set min date for tournament creation to today
        const todayStr = new Date().toISOString().split('T')[0];
        const startDateInput = document.getElementById('startDate');
        const endDateInput = document.getElementById('endDate');
        if (startDateInput) startDateInput.min = todayStr;
        if (endDateInput) endDateInput.min = todayStr;

        // Check if we should open create modal
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('create') === 'true') {
            setTimeout(() => openModal('createTournamentModal'), 100);
        }
    }
});
