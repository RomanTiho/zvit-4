import os
import re

unified_header = '''<nav class="navbar">
    <div class="container">
        <div class="nav-content">
            <a href="/index.html" class="logo">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <circle cx="16" cy="16" r="14" stroke="currentColor" stroke-width="2" />
                    <path d="M16 2C16 2 10 8 10 16C10 24 16 30 16 30" stroke="currentColor" stroke-width="2" />
                    <path d="M16 2C16 2 22 8 22 16C22 24 16 30 16 30" stroke="currentColor" stroke-width="2" />
                    <path d="M2 16H30" stroke="currentColor" stroke-width="2" />
                </svg>
                <span>FootballHub</span>
            </a>
            <ul class="nav-links" id="mainNavLinks">
                <li><a href="/index.html">Головна</a></li>
                <li><a href="/tournaments.html">Турніри</a></li>
                <li><a href="/players.html">Рейтинг</a></li>
                <li><a id="featuresLink" href="/index.html#features">Можливості</a></li>
            </ul>
            <div style="display: flex; gap: 1rem; align-items: center;" id="headerActions">
                <button class="btn btn-primary" id="createTournamentBtn" style="display:none">Створити турнір</button>
                <button class="btn btn-primary" id="registerTeamBtn" style="display:none">Зареєструвати команду</button>
                <button class="btn btn-secondary" id="adminLogoutBtn" style="display:none">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="margin-right: 0.5rem;">
                        <path d="M6 14H3C2.5 14 2 13.5 2 13V3C2 2.5 2.5 2 3 2H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                        <path d="M11 11L14 8L11 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        <path d="M14 8H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                    Вийти з адміна
                </button>
            </div>
            
            <!-- Auth navigation container to be populated by auth-nav.js -->
            <div class="auth-nav-container" id="authNavContainer"></div>
        </div>
    </div>
</nav>'''

html_dir = r'd:\zvit4\diplom\frontend\html'

for file in os.listdir(html_dir):
    if not file.endswith('.html'):
        continue
    filepath = os.path.join(html_dir, file)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace nav block
    content = re.sub(r'<nav class="navbar".*?</nav>', unified_header, content, flags=re.DOTALL)
    
    # Add favicon if not exists
    if 'favicon.svg' not in content:
        content = content.replace('</title>', '</title>\n    <link rel="icon" href="/favicon.svg" type="image/svg+xml">')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Headers and Favicon updated.')
