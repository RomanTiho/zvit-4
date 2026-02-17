// ===== Global State Management =====
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

// ===== Initialize Sample Data =====
function initializeSampleData() {
    const existingData = Storage.load('tournaments');
    if (!existingData || existingData.length === 0) {
        const sampleTournaments = [
            {
                id: 1,
                name: 'Літній Кубок 2026',
                startDate: '2026-06-15',
                endDate: '2026-06-30',
                format: 'league',
                maxTeams: 8,
                location: 'Київ, Україна',
                description: 'Запрошуємо всіх любителів футболу взяти участь у нашому літньому турнірі! Це чудова можливість показати свої навички.',
                status: 'upcoming',
                teams: [
                    { id: 1, name: 'Динамо', captain: 'Іван Петренко', email: 'ivan@example.com', phone: '+380501234567', players: 11 },
                    { id: 2, name: 'Шахтар', captain: 'Петро Іваненко', email: 'petro@example.com', phone: '+380501234568', players: 11 },
                    { id: 3, name: 'Зоря', captain: 'Олег Сидоренко', email: 'oleg@example.com', phone: '+380501234569', players: 11 },
                    { id: 4, name: 'Ворскла', captain: 'Андрій Коваленко', email: 'andriy@example.com', phone: '+380501234570', players: 11 },
                    { id: 5, name: 'Олімпік', captain: 'Сергій Мельник', email: 'sergiy@example.com', phone: '+380501234571', players: 11 },
                    { id: 6, name: 'Колос', captain: 'Максим Бондаренко', email: 'maxim@example.com', phone: '+380501234572', players: 11 }
                ],
                standings: [],
                matches: []
            },
            {
                id: 2,
                name: 'Весняний Чемпіонат 2026',
                startDate: '2026-04-10',
                endDate: '2026-04-25',
                format: 'knockout',
                maxTeams: 16,
                location: 'Львів, Україна',
                description: 'Турнір на вибування для найсильніших команд регіону. Переможець отримає кубок та грошовий приз.',
                status: 'upcoming',
                teams: [],
                standings: [],
                matches: []
            },
            {
                id: 3,
                name: 'Літній Кубок 2025',
                startDate: '2025-06-15',
                endDate: '2025-06-30',
                format: 'league',
                maxTeams: 8,
                location: 'Київ, Україна',
                description: 'Літній турнір 2025 року пройшов з великим успіхом! Команда Динамо стала переможцем.',
                status: 'completed',
                teams: [
                    { id: 1, name: 'Динамо', captain: 'Іван Петренко', email: 'ivan@example.com', phone: '+380501234567', players: 11 },
                    { id: 2, name: 'Шахтар', captain: 'Петро Іваненко', email: 'petro@example.com', phone: '+380501234568', players: 11 },
                    { id: 3, name: 'Зоря', captain: 'Олег Сидоренко', email: 'oleg@example.com', phone: '+380501234569', players: 11 },
                    { id: 4, name: 'Ворскла', captain: 'Андрій Коваленко', email: 'andriy@example.com', phone: '+380501234570', players: 11 },
                    { id: 5, name: 'Олімпік', captain: 'Сергій Мельник', email: 'sergiy@example.com', phone: '+380501234571', players: 11 },
                    { id: 6, name: 'Колос', captain: 'Максим Бондаренко', email: 'maxim@example.com', phone: '+380501234572', players: 11 }
                ],
                standings: [
                    { teamId: 1, teamName: 'Динамо', played: 5, won: 4, drawn: 1, lost: 0, goalsFor: 12, goalsAgainst: 3, points: 13 },
                    { teamId: 2, teamName: 'Шахтар', played: 5, won: 3, drawn: 2, lost: 0, goalsFor: 10, goalsAgainst: 4, points: 11 },
                    { teamId: 3, teamName: 'Зоря', played: 5, won: 3, drawn: 0, lost: 2, goalsFor: 9, goalsAgainst: 7, points: 9 },
                    { teamId: 4, teamName: 'Ворскла', played: 5, won: 2, drawn: 1, lost: 2, goalsFor: 7, goalsAgainst: 8, points: 7 },
                    { teamId: 5, teamName: 'Олімпік', played: 5, won: 1, drawn: 0, lost: 4, goalsFor: 5, goalsAgainst: 11, points: 3 },
                    { teamId: 6, teamName: 'Колос', played: 5, won: 0, drawn: 0, lost: 5, goalsFor: 2, goalsAgainst: 12, points: 0 }
                ],
                matches: [
                    { id: 1, date: '2025-06-15 15:00', homeTeam: 'Динамо', awayTeam: 'Шахтар', homeScore: 2, awayScore: 1, status: 'completed' },
                    { id: 2, date: '2025-06-15 17:00', homeTeam: 'Зоря', awayTeam: 'Ворскла', homeScore: 3, awayScore: 1, status: 'completed' },
                    { id: 3, date: '2025-06-16 15:00', homeTeam: 'Олімпік', awayTeam: 'Колос', homeScore: 1, awayScore: 0, status: 'completed' },
                    { id: 4, date: '2025-06-20 15:00', homeTeam: 'Динамо', awayTeam: 'Зоря', homeScore: 2, awayScore: 2, status: 'completed' },
                    { id: 5, date: '2025-06-20 17:00', homeTeam: 'Шахтар', awayTeam: 'Ворскла', homeScore: 2, awayScore: 1, status: 'completed' },
                    { id: 6, date: '2025-06-21 15:00', homeTeam: 'Колос', awayTeam: 'Олімпік', homeScore: 0, awayScore: 1, status: 'completed' }
                ]
            },
            {
                id: 4,
                name: 'Кубок Дружби 2025',
                startDate: '2025-05-01',
                endDate: '2025-05-15',
                format: 'league',
                maxTeams: 6,
                location: 'Одеса, Україна',
                description: 'Дружній турнір для аматорських команд Одеси. Акцент на спортивний дух та командну роботу.',
                status: 'completed',
                teams: [
                    { id: 1, name: 'Чорноморець-Аматори', captain: 'Дмитро Ковальчук', email: 'dmytro@example.com', phone: '+380501111111', players: 11 },
                    { id: 2, name: 'Портовики', captain: 'Олександр Морозов', email: 'oleksandr@example.com', phone: '+380502222222', players: 11 },
                    { id: 3, name: 'Приморські Леви', captain: 'Віктор Савченко', email: 'viktor@example.com', phone: '+380503333333', players: 11 },
                    { id: 4, name: 'Одеса Юнайтед', captain: 'Ігор Павленко', email: 'igor@example.com', phone: '+380504444444', players: 11 },
                    { id: 5, name: 'Морські Вовки', captain: 'Артем Кравченко', email: 'artem@example.com', phone: '+380505555555', players: 11 },
                    { id: 6, name: 'Дюк', captain: 'Сергій Бойко', email: 'sergiy@example.com', phone: '+380506666666', players: 11 }
                ],
                standings: [
                    { teamId: 1, teamName: 'Чорноморець-Аматори', played: 5, won: 4, drawn: 0, lost: 1, goalsFor: 14, goalsAgainst: 5, points: 12 },
                    { teamId: 2, teamName: 'Портовики', played: 5, won: 3, drawn: 1, lost: 1, goalsFor: 11, goalsAgainst: 6, points: 10 },
                    { teamId: 3, teamName: 'Приморські Леви', played: 5, won: 3, drawn: 0, lost: 2, goalsFor: 10, goalsAgainst: 8, points: 9 },
                    { teamId: 4, teamName: 'Одеса Юнайтед', played: 5, won: 2, drawn: 1, lost: 2, goalsFor: 8, goalsAgainst: 9, points: 7 },
                    { teamId: 5, teamName: 'Морські Вовки', played: 5, won: 1, drawn: 1, lost: 3, goalsFor: 6, goalsAgainst: 11, points: 4 },
                    { teamId: 6, teamName: 'Дюк', played: 5, won: 0, drawn: 1, lost: 4, goalsFor: 4, goalsAgainst: 14, points: 1 }
                ],
                matches: [
                    { id: 1, date: '2025-05-01 15:00', homeTeam: 'Чорноморець-Аматори', awayTeam: 'Портовики', homeScore: 3, awayScore: 1, status: 'completed' },
                    { id: 2, date: '2025-05-01 17:00', homeTeam: 'Приморські Леви', awayTeam: 'Одеса Юнайтед', homeScore: 2, awayScore: 1, status: 'completed' },
                    { id: 3, date: '2025-05-02 15:00', homeTeam: 'Морські Вовки', awayTeam: 'Дюк', homeScore: 1, awayScore: 1, status: 'completed' },
                    { id: 4, date: '2025-05-05 15:00', homeTeam: 'Чорноморець-Аматори', awayTeam: 'Приморські Леви', homeScore: 4, awayScore: 2, status: 'completed' },
                    { id: 5, date: '2025-05-05 17:00', homeTeam: 'Портовики', awayTeam: 'Одеса Юнайтед', homeScore: 2, awayScore: 2, status: 'completed' },
                    { id: 6, date: '2025-05-06 15:00', homeTeam: 'Дюк', awayTeam: 'Морські Вовки', homeScore: 1, awayScore: 2, status: 'completed' },
                    { id: 7, date: '2025-05-09 15:00', homeTeam: 'Чорноморець-Аматори', awayTeam: 'Одеса Юнайтед', homeScore: 3, awayScore: 0, status: 'completed' },
                    { id: 8, date: '2025-05-09 17:00', homeTeam: 'Приморські Леви', awayTeam: 'Портовики', homeScore: 2, awayScore: 3, status: 'completed' },
                    { id: 9, date: '2025-05-10 15:00', homeTeam: 'Морські Вовки', awayTeam: 'Одеса Юнайтед', homeScore: 1, awayScore: 2, status: 'completed' },
                    { id: 10, date: '2025-05-12 15:00', homeTeam: 'Портовики', awayTeam: 'Морські Вовки', homeScore: 3, awayScore: 1, status: 'completed' },
                    { id: 11, date: '2025-05-12 17:00', homeTeam: 'Одеса Юнайтед', awayTeam: 'Дюк', homeScore: 2, awayScore: 0, status: 'completed' },
                    { id: 12, date: '2025-05-13 15:00', homeTeam: 'Приморські Леви', awayTeam: 'Морські Вовки', homeScore: 3, awayScore: 1, status: 'completed' },
                    { id: 13, date: '2025-05-14 15:00', homeTeam: 'Портовики', awayTeam: 'Дюк', homeScore: 2, awayScore: 1, status: 'completed' },
                    { id: 14, date: '2025-05-14 17:00', homeTeam: 'Одеса Юнайтед', awayTeam: 'Чорноморець-Аматори', homeScore: 1, awayScore: 2, status: 'completed' },
                    { id: 15, date: '2025-05-15 15:00', homeTeam: 'Дюк', awayTeam: 'Приморські Леви', homeScore: 1, awayScore: 1, status: 'completed' }
                ]
            }
        ];

        Storage.save('tournaments', sampleTournaments);
        AppState.tournaments = sampleTournaments;
    } else {
        AppState.tournaments = existingData;
    }
}

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
            btn.addEventListener('click', () => {
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
    initializeSampleData();
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
