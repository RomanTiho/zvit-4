// ===== Tournament Detail Page JavaScript =====

let currentTournament = null;

// ===== Check if user is admin =====
function isAdmin() {
    // Check if there's a transfer from admin panel
    const adminTransfer = localStorage.getItem('footballhub_admin_transfer');
    if (adminTransfer === 'true') {
        // Transfer to sessionStorage
        sessionStorage.setItem('footballhub_admin_auth', 'true');
        // Clean up transfer flag
        localStorage.removeItem('footballhub_admin_transfer');
    }

    return sessionStorage.getItem('footballhub_admin_auth') === 'true';
}

// ===== Load Tournament Data =====
function loadTournamentData() {
    // Try to get tournament ID from URL parameter first, then from localStorage
    const urlParams = new URLSearchParams(window.location.search);
    let tournamentId = urlParams.get('id');

    if (tournamentId) {
        // Convert string ID from URL to number
        tournamentId = parseInt(tournamentId);
        // Save to localStorage for future use
        Storage.save('currentTournamentId', tournamentId);
    } else {
        // Fallback to localStorage
        tournamentId = Storage.load('currentTournamentId');
    }

    if (!tournamentId) {
        window.location.href = 'tournaments.html';
        return;
    }

    currentTournament = AppState.tournaments.find(t => t.id === tournamentId);
    if (!currentTournament) {
        window.location.href = 'tournaments.html';
        return;
    }

    renderTournamentHeader();
    renderOverview();
    renderStandings();
    renderMatches();
    renderTeams();
}

// ===== Render Tournament Header =====
function renderTournamentHeader() {
    document.getElementById('tournamentTitle').textContent = currentTournament.name;
    document.getElementById('tournamentDates').textContent =
        `${formatDate(currentTournament.startDate)} - ${formatDate(currentTournament.endDate)}`;
    document.getElementById('tournamentLocation').textContent = currentTournament.location;
    document.getElementById('tournamentFormat').textContent = getFormatName(currentTournament.format);
    document.getElementById('tournamentTeams').textContent =
        `${currentTournament.teams.length} / ${currentTournament.maxTeams} команд`;
}

// ===== Render Overview Tab =====
function renderOverview() {
    const descElement = document.getElementById('tournamentDescription');
    if (descElement) {
        descElement.textContent = currentTournament.description;
    }
}

// ===== Render Standings Table =====
function renderStandings() {
    const tbody = document.getElementById('standingsTableBody');
    if (!tbody) return;

    if (currentTournament.standings.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: var(--spacing-xl); color: var(--dark-500);">
                    Турнірна таблиця ще не сформована
                </td>
            </tr>
        `;
        return;
    }

    // Sort by points, then goal difference
    const sortedStandings = [...currentTournament.standings].sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        const diffA = a.goalsFor - a.goalsAgainst;
        const diffB = b.goalsFor - b.goalsAgainst;
        return diffB - diffA;
    });

    tbody.innerHTML = sortedStandings.map((team, index) => {
        const position = index + 1;
        let positionBadge = `<span class="position-badge">${position}</span>`;

        if (position === 1) {
            positionBadge = `<span class="position-badge gold">${position}</span>`;
        } else if (position === 2) {
            positionBadge = `<span class="position-badge silver">${position}</span>`;
        } else if (position === 3) {
            positionBadge = `<span class="position-badge bronze">${position}</span>`;
        }

        const goalDiff = team.goalsFor - team.goalsAgainst;
        const diffDisplay = goalDiff > 0 ? `+${goalDiff}` : goalDiff;

        return `
            <tr>
                <td>${positionBadge}</td>
                <td style="font-weight: 600;">${team.teamName}</td>
                <td>${team.played}</td>
                <td>${team.won}</td>
                <td>${team.drawn}</td>
                <td>${team.lost}</td>
                <td>${team.goalsFor}</td>
                <td>${team.goalsAgainst}</td>
                <td style="font-weight: 600; color: ${goalDiff >= 0 ? 'var(--success)' : 'var(--error)'};">${diffDisplay}</td>
                <td style="font-weight: 700; font-size: var(--font-size-lg);">${team.points}</td>
            </tr>
        `;
    }).join('');
}

// ===== Render Matches =====
function renderMatches() {
    const matchesList = document.getElementById('matchesList');
    if (!matchesList) return;

    if (currentTournament.matches.length === 0) {
        matchesList.innerHTML = `
            <div style="text-align: center; padding: var(--spacing-xl); color: var(--dark-500);">
                Розклад матчів ще не сформовано
            </div>
        `;
        return;
    }

    matchesList.innerHTML = currentTournament.matches.map(match => {
        const isCompleted = match.status === 'completed';
        const scoreDisplay = isCompleted
            ? `${match.homeScore} : ${match.awayScore}`
            : 'VS';

        return `
            <div class="match-card">
                <div class="match-date">${formatDateTime(match.date)}</div>
                <div class="match-teams">
                    <div class="team home">
                        <span class="team-name">${match.homeTeam}</span>
                    </div>
                    <div class="match-score">${scoreDisplay}</div>
                    <div class="team away">
                        <span class="team-name">${match.awayTeam}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ===== Render Teams =====
function renderTeams() {
    const teamsList = document.getElementById('teamsList');
    if (!teamsList) return;

    if (currentTournament.teams.length === 0) {
        teamsList.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: var(--spacing-xl); color: var(--dark-500);">
                Команди ще не зареєстровані
            </div>
        `;
        return;
    }

    const adminMode = isAdmin();

    teamsList.innerHTML = currentTournament.teams.map(team => `
        <div class="tournament-card">
            <div class="tournament-header" style="background: var(--gradient-primary);">
                <h3>${team.name}</h3>
            </div>
            <div class="tournament-body">
                <div class="tournament-info">
                    <div class="info-row">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <circle cx="9" cy="6" r="3" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M3 15C3 12 6 10 9 10C12 10 15 12 15 15" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span><strong>Капітан:</strong> ${team.captain}</span>
                    </div>
                    <div class="info-row">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <rect x="2" y="4" width="14" height="11" rx="2" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M2 7H16M6 2V6M12 2V6" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span><strong>Гравців:</strong> ${team.players}</span>
                    </div>
                    <div class="info-row">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                            <rect x="2" y="3" width="14" height="12" rx="2" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M2 7H16M6 11H12" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span>${team.email}</span>
                    </div>
                </div>
                ${adminMode ? `
                    <div style="margin-top: var(--spacing-md); padding-top: var(--spacing-md); border-top: 1px solid var(--dark-200);">
                        <button class="btn btn-secondary delete-team-btn" data-team-id="${team.id}" style="width: 100%;">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="flex-shrink: 0;">
                                <path d="M2 4H14M6 4V2H10V4M3 4L4 14H12L13 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            Видалити команду
                        </button>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');

    // Add event listeners to delete buttons
    if (adminMode) {
        const deleteButtons = teamsList.querySelectorAll('.delete-team-btn');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function () {
                const teamId = parseInt(this.getAttribute('data-team-id'));
                deleteTeam(teamId);
            });
        });
    }
}

// ===== Tab Navigation =====
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// ===== Register Team Modal =====
function setupRegisterTeamModal() {
    const registerBtn = document.getElementById('registerTeamBtn');
    const modal = document.getElementById('registerTeamModal');
    const closeBtn = document.getElementById('closeRegisterModalBtn');
    const cancelBtn = document.getElementById('cancelRegisterBtn');
    const overlay = modal?.querySelector('.modal-overlay');
    const form = document.getElementById('registerTeamForm');

    if (registerBtn) {
        registerBtn.addEventListener('click', () => {
            if (currentTournament.teams.length >= currentTournament.maxTeams) {
                showWarning('Вибачте, всі місця в турнірі зайняті');
                return;
            }
            openModal('registerTeamModal');
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => closeModal('registerTeamModal'));
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => closeModal('registerTeamModal'));
    }

    if (overlay) {
        overlay.addEventListener('click', () => closeModal('registerTeamModal'));
    }

    if (form) {
        form.addEventListener('submit', handleRegisterTeam);
    }
}

// ===== Handle Team Registration =====
function handleRegisterTeam(e) {
    e.preventDefault();

    const teamData = {
        id: Date.now(),
        name: document.getElementById('teamName').value,
        captain: document.getElementById('captainName').value,
        email: document.getElementById('captainEmail').value,
        phone: document.getElementById('captainPhone').value,
        players: parseInt(document.getElementById('playersCount').value),
        notes: document.getElementById('teamNotes').value
    };

    // Check if team name already exists
    if (currentTournament.teams.some(t => t.name.toLowerCase() === teamData.name.toLowerCase())) {
        showError('Команда з такою назвою вже зареєстрована');
        return;
    }

    // Add team to tournament
    currentTournament.teams.push(teamData);

    // Update in storage
    const tournamentIndex = AppState.tournaments.findIndex(t => t.id === currentTournament.id);
    AppState.tournaments[tournamentIndex] = currentTournament;
    Storage.save('tournaments', AppState.tournaments);

    // Reset form and close modal
    e.target.reset();
    closeModal('registerTeamModal');

    // Refresh display
    renderTournamentHeader();
    renderTeams();

    // Show success message
    showSuccess('Команду успішно зареєстровано!');
}

// ===== Delete Team (Admin Only) =====
function deleteTeam(teamId) {
    if (!isAdmin()) {
        showError('Тільки адміністратори можуть видаляти команди');
        return;
    }

    const team = currentTournament.teams.find(t => t.id === teamId);
    if (!team) {
        showError('Команду не знайдено!');
        return;
    }

    showConfirm(`Ви впевнені, що хочете видалити команду "${team.name}"?`, () => {
        // Remove team from tournament
        currentTournament.teams = currentTournament.teams.filter(t => t.id !== teamId);

        // Update in storage
        const tournamentIndex = AppState.tournaments.findIndex(t => t.id === currentTournament.id);
        AppState.tournaments[tournamentIndex] = currentTournament;
        Storage.save('tournaments', AppState.tournaments);

        // Refresh display
        renderTournamentHeader();
        renderTeams();

        // Show success message
        showSuccess('Команду успішно видалено!');
    });
}

// ===== Initialize Tournament Detail Page =====
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('tournamentTitle')) {
        loadTournamentData();
        setupTabs();
        setupRegisterTeamModal();
        setupAdminLogout();
    }
});

// ===== Setup Admin Login/Logout =====
function setupAdminLogout() {
    const logoutBtn = document.getElementById('adminLogoutBtn');

    // Only show logout button if admin is logged in
    if (logoutBtn && isAdmin()) {
        logoutBtn.style.display = 'flex';
    }

    // Handle logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            showConfirm('Ви впевнені, що хочете вийти з адмін-режиму?', () => {
                sessionStorage.removeItem('footballhub_admin_auth');
                showInfo('Ви вийшли з адмін-режиму');
                // Reload page to hide admin features
                window.location.reload();
            });
        });
    }
}
