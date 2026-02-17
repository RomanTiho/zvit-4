// API клієнт для взаємодії з Django backend
const API_BASE_URL = 'http://localhost:8001/api';

class APIClient {
    /**
     * GET запит до API
     */
    static async get(endpoint, params = {}) {
        const url = new URL(`${API_BASE_URL}${endpoint}`);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    }

    /**
     * POST запит до API
     */
    static async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }

    /**
     * PUT запит до API
     */
    static async put(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            throw error;
        }
    }

    /**
     * DELETE запит до API
     */
    static async delete(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return true;
        } catch (error) {
            console.error('API DELETE Error:', error);
            throw error;
        }
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
