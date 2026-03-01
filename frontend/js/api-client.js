// API клієнт для взаємодії з Django backend
const API_BASE_URL = CONFIG.API_BASE_URL;

class APIClient {
    /**
     * Внутрішній метод для виконання fetch-запитів з обробкою токенів
     */
    static async _fetch(url, options = {}) {
        let token = localStorage.getItem('access_token');
        options.headers = options.headers || {};
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        let response = await fetch(url, options);

        // Якщо токен протух (401), спробуємо оновити
        if (response.status === 401 && localStorage.getItem('refresh_token')) {
            try {
                const refreshResponse = await fetch(`${API_BASE_URL}/token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
                });

                if (refreshResponse.ok) {
                    const data = await refreshResponse.json();
                    localStorage.setItem('access_token', data.access);
                    if (data.refresh) localStorage.setItem('refresh_token', data.refresh);

                    // Повторюємо оригінальний запит з новим токеном
                    options.headers['Authorization'] = `Bearer ${data.access}`;
                    response = await fetch(url, options);
                } else {
                    // Refresh токен протух або недійсний
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/auth.html';
                    throw new Error('Session expired');
                }
            } catch (e) {
                console.error('Token refresh failed', e);
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/auth.html';
                throw e;
            }
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Для DELETE запитів часто немає тіла (204 No Content)
        if (response.status === 204) return true;

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return await response.json();
        } else {
            return await response.text();
        }
    }

    /**
     * GET запит до API
     */
    static async get(endpoint, params = {}) {
        const url = new URL(`${API_BASE_URL}${endpoint}`, window.location.origin);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        return await this._fetch(url);
    }

    /**
     * POST запит до API
     */
    static async post(endpoint, data) {
        return await this._fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT запит до API
     */
    static async put(endpoint, data) {
        return await this._fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE запит до API
     */
    static async delete(endpoint) {
        return await this._fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'DELETE'
        });
    }
}

// API методи для турнірів
class TournamentsAPI {
    static async getTournaments(params = {}) {
        return await APIClient.get('/tournaments/', params);
    }
    static async getTournament(id) {
        return await APIClient.get(`/tournaments/${id}/`);
    }
    static async createTournament(data) {
        return await APIClient.post('/tournaments/', data);
    }
}

// API методи для гравців
class PlayersAPI {
    /**
     * Отримати список всіх гравців
     */
    static async getPlayers(params = {}) {
        return await APIClient.get('/players/', params);
    }

    /**
     * Отримати деталі гравця
     */
    static async getPlayer(id) {
        return await APIClient.get(`/players/${id}/`);
    }

    /**
     * Отримати таблицю лідерів
     */
    static async getLeaderboard(position = null, limit = 50) {
        const params = { limit };
        if (position) params.position = position;
        return await APIClient.get('/players/leaderboard/', params);
    }

    /**
     * Оновити статистику гравця
     */
    static async updateStats(playerId, stats) {
        return await APIClient.post(`/players/${playerId}/update_stats/`, stats);
    }

    /**
     * Отримати історію рейтингу
     */
    static async getRatingHistory(playerId) {
        return await APIClient.get(`/players/${playerId}/rating_history/`);
    }

    /**
     * Пошук гравців
     */
    static async searchPlayers(query, filters = {}) {
        const params = { q: query, ...filters };
        return await APIClient.get('/players/search/', params);
    }
}

// API методи для аналітики
class AnalyticsAPI {
    /**
     * Отримати аналітику команди
     */
    static async getTeamAnalytics(teamId) {
        return await APIClient.get(`/analytics/teams/${teamId}/`);
    }

    /**
     * Отримати тренд продуктивності
     */
    static async getPerformanceTrend(teamId) {
        return await APIClient.get(`/analytics/teams/${teamId}/performance_trend/`);
    }

    /**
     * Аналіз сильних/слабких сторін
     */
    static async getStrengthsWeaknesses(teamId) {
        return await APIClient.get(`/analytics/teams/${teamId}/strengths_weaknesses/`);
    }
}

// API методи для досягнень
class AchievementsAPI {
    /**
     * Отримати всі досягнення
     */
    static async getAchievements() {
        return await APIClient.get('/achievements/');
    }

    /**
     * Отримати досягнення користувача
     */
    static async getUserAchievements() {
        return await APIClient.get('/user-achievements/');
    }

    /**
     * Перевірити прогрес досягнень
     */
    static async checkProgress() {
        return await APIClient.get('/user-achievements/check_progress/');
    }
}

// API методи для повідомлень
class NotificationsAPI {
    /**
     * Отримати всі повідомлення
     */
    static async getNotifications() {
        return await APIClient.get('/notifications/');
    }

    /**
     * Отримати непрочитані
     */
    static async getUnread() {
        return await APIClient.get('/notifications/unread/');
    }

    /**
     * Позначити як прочитане
     */
    static async markAsRead(notificationId) {
        return await APIClient.post(`/notifications/${notificationId}/mark_read/`);
    }

    /**
     * Позначити всі як прочитані
     */
    static async markAllAsRead() {
        return await APIClient.post('/notifications/mark_all_read/');
    }
}

// API методи для пошуку гравців
class PlayerFinderAPI {
    /**
     * Пошук доступних гравців
     */
    static async searchAvailablePlayers(filters = {}) {
        return await APIClient.get('/player-finder/search/', filters);
    }

    /**
     * Отримати запити команд
     */
    static async getTeamRequests() {
        return await APIClient.get('/team-requests/');
    }
}

// ===== API методи для складів УПЛ (api-football.com) =====
class UPLAPI {
    /**
     * Отримати реальний склад команди УПЛ з бекенду (кешується 24 год)
     * @param {string} teamName - назва команди (напр. 'Динамо')
     * @returns {Promise<{players: Array, source: string, fetched_at: string}>}
     */
    static async getSquad(teamName) {
        try {
            const encoded = encodeURIComponent(teamName);
            const resp = await fetch(`${API_BASE_URL}/upl/squad/${encoded}/`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            return await resp.json();
        } catch (err) {
            console.warn(`[UPLAPI] Could not fetch squad for "${teamName}":`, err);
            return { players: [], source: 'error' };
        }
    }
}
