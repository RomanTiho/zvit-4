// ===== Tournaments Page JavaScript =====
let map = null;
let markers = [];

const CITY_COORDS = {
    'київ': [50.4501, 30.5234],
    'львів': [49.8397, 24.0297],
    'харків': [49.9935, 36.2304],
    'одеса': [46.4825, 30.7233],
    'дніпро': [48.4647, 35.0461]
};

function getCoords(locationStr) {
    if (!locationStr) return [48.3794, 31.1656];
    const locLower = locationStr.toLowerCase();
    for (const city in CITY_COORDS) {
        if (locLower.includes(city)) return CITY_COORDS[city];
    }
    // Random jitter around center for unknown locations to prevent overlapping
    return [48.3794 + (Math.random() - 0.5) * 2, 31.1656 + (Math.random() - 0.5) * 2];
}

function updateMap(tournaments) {
    if (!document.getElementById('tournamentsMap')) return;

    if (!map) {
        map = L.map('tournamentsMap').setView([48.3794, 31.1656], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }

    // Clear old markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    tournaments.forEach(t => {
        const coords = getCoords(t.location);
        const marker = L.marker(coords).addTo(map);

        // Popup content
        const popupContent = `
            <div style="text-align: center; min-width: 150px;">
                <strong style="font-size: 14px; color: var(--primary);">${t.name}</strong><br>
                <div style="margin: 5px 0; font-size: 12px;">${t.location}</div>
                <a href="tournament-detail.html?id=${t.id}" style="display: inline-block; margin-top: 5px; padding: 4px 8px; background: var(--primary); color: white; border-radius: 4px; text-decoration: none; font-size: 12px;">Перейти до турніру</a>
            </div>
        `;
        marker.bindPopup(popupContent);
        markers.push(marker);
    });

    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.2));
    }
}

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
                    Спробуйте змінити фільтри або створіть новий турнір
                </p>
                <button class="btn btn-primary" onclick="openModal('createTournamentModal')">
                    Створити турнір
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = tournaments.map(tournament => `
        <div class="tournament-card" onclick="viewTournament(${tournament.id})">
            <div class="tournament-header">
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
    `).join('');

    // Update map with displayed tournaments
    updateMap(tournaments);
}

// ===== Filter Tournaments =====
function filterTournaments() {
    const statusFilter = document.getElementById('statusFilter').value;
    const formatFilter = document.getElementById('formatFilter').value;
    const searchQuery = document.getElementById('searchInput').value.toLowerCase();

    let filtered = AppState.tournaments;

    if (statusFilter !== 'all') {
        filtered = filtered.filter(t => t.status === statusFilter);
    }

    if (formatFilter !== 'all') {
        filtered = filtered.filter(t => t.format === formatFilter);
    }

    if (searchQuery) {
        filtered = filtered.filter(t =>
            t.name.toLowerCase().includes(searchQuery) ||
            t.location.toLowerCase().includes(searchQuery) ||
            t.description.toLowerCase().includes(searchQuery)
        );
    }

    // Sort tournaments: upcoming and ongoing first, completed last
    const statusOrder = { 'upcoming': 1, 'ongoing': 2, 'completed': 3 };
    filtered.sort((a, b) => {
        const orderA = statusOrder[a.status] || 999;
        const orderB = statusOrder[b.status] || 999;
        return orderA - orderB;
    });

    renderTournaments(filtered);
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

    const requestData = {
        id: Date.now(),
        contactName: document.getElementById('contactName').value,
        contactEmail: document.getElementById('contactEmail').value,
        contactPhone: document.getElementById('contactPhone').value,
        tournamentName: document.getElementById('tournamentName').value,
        startDate: document.getElementById('startDate').value,
        endDate: document.getElementById('endDate').value,
        format: document.getElementById('format').value,
        maxTeams: parseInt(document.getElementById('maxTeams').value),
        location: document.getElementById('location').value,
        description: document.getElementById('description').value || 'Немає додаткової інформації',
        submittedAt: new Date().toISOString(),
        status: 'pending'
    };

    // Validate dates
    if (new Date(requestData.start_date) >= new Date(requestData.end_date)) {
        showError('Дата завершення повинна бути пізніше дати початку');
        return;
    }

    // Get existing requests
    const requests = Storage.load('tournamentRequests') || [];

    // Add new request
    requests.push(requestData);
    Storage.save('tournamentRequests', requests);

    // Reset form and close modal
    e.target.reset();
    closeModal('createTournamentModal');

    // Show success message
    showSuccess('Дякуємо! Ваш запит успішно надіслано. Наш менеджер зв\'яжеться з вами найближчим часом.');
}

// ===== Initialize Tournaments Page =====
document.addEventListener('DOMContentLoaded', async () => {
    // Check if we're on tournaments page
    if (document.getElementById('tournamentsGrid')) {
        try {
            const response = await TournamentsAPI.getTournaments();
            AppState.tournaments = response.results || response;
            renderTournaments(AppState.tournaments);
        } catch (error) {
            console.error('Failed to load tournaments:', error);
            renderTournaments([]);
        }
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

        // Check if we should open create modal
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('create') === 'true') {
            setTimeout(() => openModal('createTournamentModal'), 100);
        }
    }
});
