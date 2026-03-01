// ===== Tournament Detail Page JavaScript =====

let currentTournament = null;
let playerRoster = [];

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
async function loadTournamentData() {
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

    try {
        currentTournament = await TournamentsAPI.getTournament(tournamentId);
    } catch (error) {
        console.error('Failed to load tournament:', error);
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
        `${formatDate(currentTournament.start_date)} - ${formatDate(currentTournament.end_date)}`;
    document.getElementById('tournamentLocation').textContent = currentTournament.location;
    document.getElementById('tournamentFormat').textContent = getFormatName(currentTournament.format);
    document.getElementById('tournamentTeams').textContent =
        `${currentTournament.teams.length} / ${currentTournament.max_teams} команд`;
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

    teamsList.innerHTML = currentTournament.teams.map(team => {
        const rosterHtml = (team.playerRoster && team.playerRoster.length > 0)
            ? `<div class="team-roster">
                <div class="roster-section-header">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <circle cx="5" cy="4" r="2" stroke="currentColor" stroke-width="1.5"/>
                        <circle cx="11" cy="4" r="2" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M1 14c0-2.2 1.8-4 4-4s4 1.8 4 4" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M12 10.2c2 0.4 3 1.8 3 3.8" stroke="currentColor" stroke-width="1.5"/>
                    </svg>
                    <strong>Склад гравців (${team.playerRoster.length})</strong>
                </div>
                <div class="roster-player-list">
                    ${team.playerRoster.map((name, i) => `
                        <div class="roster-player-item${adminMode ? ' roster-admin' : ''}">
                            <span class="roster-player-num">${i + 1}</span>
                            <span class="roster-player-name">${name}</span>
                            ${adminMode ? `
                            <button class="roster-delete-player-btn" onclick="deletePlayer(${team.id}, ${i})" title="\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u0433\u0440\u0430\u0432\u0446\u044f">
                                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                    <path d="M9 3L3 9M3 3L9 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                                </svg>
                            </button>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>`
            : `<div class="info-row">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <rect x="2" y="4" width="14" height="11" rx="2" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M2 7H16M6 2V6M12 2V6" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                <span><strong>Гравців:</strong> ${team.players}</span>
            </div>`;

        return `<div class="tournament-card" data-live-team="${team.id}">
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
                            <rect x="2" y="3" width="14" height="12" rx="2" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M2 7H16M6 11H12" stroke="currentColor" stroke-width="1.5"/>
                        </svg>
                        <span>${team.email}</span>
                    </div>
                </div>
                ${rosterHtml}
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
        </div>`;
    }).join('');

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
            if (currentTournament.teams.length >= currentTournament.max_teams) {
                showWarning('Вибачте, всі місця в турнірі зайняті');
                return;
            }
            openModal('registerTeamModal');
        });
    }

    const closeAndReset = () => {
        closeModal('registerTeamModal');
        playerRoster = [];
        renderPlayerRoster();
    };

    if (closeBtn) closeBtn.addEventListener('click', closeAndReset);
    if (cancelBtn) cancelBtn.addEventListener('click', closeAndReset);
    if (overlay) overlay.addEventListener('click', closeAndReset);

    if (form) {
        form.addEventListener('submit', handleRegisterTeam);
    }

    setupPlayerRosterInput();
}

// ===== Handle Team Registration =====
function handleRegisterTeam(e) {
    e.preventDefault();

    if (playerRoster.length < 8) {
        showError('Необхідно додати щонайменше 8 гравців до складу команди');
        return;
    }

    const teamData = {
        id: Date.now(),
        name: document.getElementById('teamName').value,
        captain: document.getElementById('captainName').value,
        email: document.getElementById('captainEmail').value,
        phone: document.getElementById('captainPhone').value,
        players: playerRoster.length,
        playerRoster: [...playerRoster],
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

    // Reset form, roster and close modal
    e.target.reset();
    playerRoster = [];
    renderPlayerRoster();
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

// ===== Player Roster Input (Form) =====
function setupPlayerRosterInput() {
    const addBtn = document.getElementById('addPlayerBtn');
    const input = document.getElementById('playerNameInput');
    if (!addBtn || !input) return;

    addBtn.addEventListener('click', addPlayer);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addPlayer();
        }
    });
}

function addPlayer() {
    const input = document.getElementById('playerNameInput');
    const name = input.value.trim();
    if (!name) return;
    if (playerRoster.length >= 25) {
        showWarning('Максимум 25 гравців у складі');
        return;
    }
    if (playerRoster.map(n => n.toLowerCase()).includes(name.toLowerCase())) {
        showWarning('Такий гравець вже доданий до складу');
        return;
    }
    playerRoster.push(name);
    input.value = '';
    input.focus();
    renderPlayerRoster();
}

function removePlayer(index) {
    playerRoster.splice(index, 1);
    renderPlayerRoster();
}

function renderPlayerRoster() {
    const list = document.getElementById('playerRosterList');
    const label = document.getElementById('playerCountLabel');
    if (!list) return;

    const count = playerRoster.length;
    if (label) {
        const enough = count >= 8;
        label.textContent = count === 0 ? '(мінімум 8)' : `(${count} гравців${enough ? ' ✓' : ', потрібно ще ' + (8 - count)})`;
        label.style.color = enough ? 'var(--success)' : 'var(--dark-500)';
    }

    if (count === 0) {
        list.innerHTML = '<div class="roster-empty">Додайте щонайменше 8 гравців</div>';
        return;
    }

    list.innerHTML = playerRoster.map((name, i) => `
        <div class="roster-form-item">
            <span class="roster-num">${i + 1}</span>
            <span class="roster-name">${name}</span>
            <button type="button" class="roster-remove-btn" onclick="removePlayer(${i})" title="Видалити">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M9 3L3 9M3 3L9 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
    `).join('');
}

// ===== Initialize Tournament Detail Page =====
document.addEventListener('DOMContentLoaded', async () => {
    if (document.getElementById('tournamentTitle')) {
        await loadTournamentData();
        setupTabs();
        setupRegisterTeamModal();
        setupAdminLogout();
    }
});

// ===== Delete Player from Roster (Admin Only) =====
function deletePlayer(teamId, playerIndex) {
    if (!isAdmin()) {
        showError('Тільки адміністратори можуть видаляти гравців');
        return;
    }

    const team = currentTournament.teams.find(t => t.id === teamId);
    if (!team || !team.playerRoster) return;

    const playerName = team.playerRoster[playerIndex];

    showConfirm(`Видалити гравця "${playerName}" зі складу?`, () => {
        team.playerRoster.splice(playerIndex, 1);
        team.players = team.playerRoster.length;

        const tournamentIndex = AppState.tournaments.findIndex(t => t.id === currentTournament.id);
        AppState.tournaments[tournamentIndex] = currentTournament;
        Storage.save('tournaments', AppState.tournaments);

        renderTeams();
        showSuccess(`Гравця "​${playerName}" видалено зі складу`);
    });
}

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
