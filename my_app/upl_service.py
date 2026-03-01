import requests
from datetime import datetime, timezone, timedelta
from django.conf import settings


# ===== UPL Team ID mapping (api-football.com, league 333, verified IDs) =====
UPL_TEAM_IDS = {
    'Динамо':       572,
    'Шахтар':       550,
    'Зоря':         599,
    'Ворскла':      1121,
    'Колос':        3627,
    'Чорноморець':  3615,
    'Карпати':      3617,
    'Олександрія':  3619,
    'Інгулець':     3625,
    'Рух':          3632,
    'Кривбас':      6489,
    'Металіст':     3628,
    'Минай':        4658,
    'Полісся':      6496,
    'Верес':        6501,
}

API_BASE = 'https://v3.football.api-sports.io'
SEASON   = 2024
CACHE_TTL_HOURS = 24


def _get_headers():
    return {'x-apisports-key': settings.API_FOOTBALL_KEY}


def _fetch_squad_from_api(team_id: int) -> list:
    """
    Try /players/squads first (current registered squad).
    Fall back to /players?team&season (players who appeared in stats).
    """
    headers = _get_headers()

    # --- Attempt 1: squad endpoint ---
    try:
        resp = requests.get(
            f'{API_BASE}/players/squads',
            headers=headers,
            params={'team': team_id},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        players = data.get('response', [{}])[0].get('players', [])
        if players:
            return _normalise_squad(players)
    except Exception as exc:
        print(f'[UPL Service] /squads error for team {team_id}: {exc}')

    # --- Attempt 2: players-by-team endpoint (paginated, page 1 only) ---
    try:
        resp = requests.get(
            f'{API_BASE}/players',
            headers=headers,
            params={'team': team_id, 'season': SEASON},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data.get('response', [])
        if raw:
            return [
                {
                    'name':     p['player'].get('name', ''),
                    'age':      p['player'].get('age'),
                    'number':   None,
                    'position': p['statistics'][0].get('games', {}).get('position', '') if p.get('statistics') else '',
                    'photo':    p['player'].get('photo', ''),
                }
                for p in raw
            ]
    except Exception as exc:
        print(f'[UPL Service] /players error for team {team_id}: {exc}')

    return []


def _normalise_squad(players: list) -> list:
    return [
        {
            'name':     p.get('name', ''),
            'age':      p.get('age'),
            'number':   p.get('number'),
            'position': p.get('position', ''),
            'photo':    p.get('photo', ''),
        }
        for p in players
    ]


def get_squad(team_name: str) -> dict:
    """
    Return squad data for the given team name.
    Uses SQLite cache; refreshes if older than CACHE_TTL_HOURS.
    """
    from .models import UPLSquadCache

    team_id = UPL_TEAM_IDS.get(team_name)
    if not team_id:
        return {'players': [], 'source': 'fallback', 'error': f'Unknown team: {team_name}'}

    # Check cache
    cache_obj = UPLSquadCache.objects.filter(team_name=team_name).first()
    now = datetime.now(timezone.utc)

    if cache_obj and (now - cache_obj.fetched_at) < timedelta(hours=CACHE_TTL_HOURS):
        return {
            'players':    cache_obj.squad_json,
            'source':     'cache',
            'fetched_at': cache_obj.fetched_at.isoformat(),
        }

    # Fetch from API
    players = _fetch_squad_from_api(team_id)

    if players:
        UPLSquadCache.objects.update_or_create(
            team_name=team_name,
            defaults={'api_team_id': team_id, 'squad_json': players, 'fetched_at': now}
        )
        return {'players': players, 'source': 'api', 'fetched_at': now.isoformat()}

    # Return stale cache or empty
    if cache_obj:
        return {'players': cache_obj.squad_json, 'source': 'stale_cache', 'fetched_at': cache_obj.fetched_at.isoformat()}

    return {'players': [], 'source': 'fallback', 'error': 'No data available'}
