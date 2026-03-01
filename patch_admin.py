import re

with open(r'd:\zvit4\diplom\frontend\js\admin.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update loadTournaments
old_load = """// Load all tournaments
function loadTournaments() {
    const tournaments = AppState.tournaments || [];
    const tournamentsList = document.getElementById('adminTournamentsList');"""

new_load = """// Load all tournaments
async function loadTournaments() {
    try {
        const response = await TournamentsAPI.getTournaments();
        AppState.tournaments = response.results || response;
    } catch (error) {
        console.error('Failed to load tournaments:', error);
        AppState.tournaments = [];
    }
    const tournaments = AppState.tournaments || [];
    const tournamentsList = document.getElementById('adminTournamentsList');"""
content = content.replace(old_load, new_load)

# 2. Update handleAdminCreateTournament
old_create = """// Handle admin create tournament
function handleAdminCreateTournament(e) {
    e.preventDefault();

    const formData = {
        id: Date.now(),
        name: document.getElementById('adminTournamentName').value,
        start_date: document.getElementById('adminStartDate').value,
        end_date: document.getElementById('adminEndDate').value,
        format: document.getElementById('adminFormat').value,
        max_teams: parseInt(document.getElementById('adminMaxTeams').value),
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
}"""

new_create = """// Handle admin create tournament
async function handleAdminCreateTournament(e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('adminTournamentName').value,
        start_date: document.getElementById('adminStartDate').value,
        end_date: document.getElementById('adminEndDate').value,
        format: document.getElementById('adminFormat').value,
        max_teams: parseInt(document.getElementById('adminMaxTeams').value),
        location: document.getElementById('adminLocation').value,
        description: document.getElementById('adminDescription').value,
        status: 'upcoming'
    };

    if (new Date(formData.start_date) >= new Date(formData.end_date)) {
        showError('Дата завершення повинна бути пізніше дати початку');
        return;
    }

    try {
        await TournamentsAPI.createTournament(formData);
        showSuccess('Турнір успішно створено!');
        e.target.reset();
        await loadTournaments();
        switchTab('tournaments');
    } catch (error) {
        showError('Помилка при створенні турніру: ' + error.message);
    }
}"""
content = content.replace(old_create, new_create)

# 3. Update createFromRequest
old_request_create = """window.createFromRequest = function (requestId) {
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
            start_date: request.start_date,
            end_date: request.end_date,
            format: request.format,
            max_teams: parseInt(request.max_teams),
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
};"""

new_request_create = """window.createFromRequest = async function (requestId) {
    const requests = Storage.load('tournamentRequests') || [];
    const request = requests.find(r => r.id === requestId);

    if (!request) {
        showError('Запит не знайдено!');
        return;
    }

    showConfirm(`Створити турнір "${request.tournamentName}"?`, async () => {
        const newTournament = {
            name: request.tournamentName,
            start_date: request.start_date,
            end_date: request.end_date,
            format: request.format,
            max_teams: parseInt(request.max_teams),
            location: request.location,
            description: request.description,
            status: 'upcoming'
        };

        try {
            await TournamentsAPI.createTournament(newTournament);
            const updatedRequests = requests.filter(r => r.id !== requestId);
            Storage.save('tournamentRequests', updatedRequests);
            loadRequests();
            await loadTournaments();
            showSuccess('Турнір успішно створено!');
        } catch (error) {
            showError('Помилка створення: ' + error.message);
        }
    });
};"""
content = content.replace(old_request_create, new_request_create)

# 4. deleteTournament
old_delete = """// Delete tournament
window.deleteTournament = function (tournamentId) {
    const tournament = AppState.tournaments.find(t => t.id === tournamentId);

    if (!tournament) {
        showError('Турнір не знайдено!');
        return;
    }

    showConfirm(`Ви впевнені, що хочете видалити турнір "${tournament.name}"?`, () => {
        AppState.tournaments = AppState.tournaments.filter(t => t.id !== tournamentId);
        Storage.save('tournaments', AppState.tournaments);
        loadTournaments();
        showSuccess('Турнір видалено!');
    });
};"""

new_delete = """// Delete tournament
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
};"""
content = content.replace(old_delete, new_delete)

with open(r'd:\zvit4\diplom\frontend\js\admin.js', 'w', encoding='utf-8') as f:
    f.write(content)
