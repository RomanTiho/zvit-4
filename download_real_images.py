import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

urls = [
    ("https://upload.wikimedia.org/wikipedia/commons/4/4b/Estadio_O%C3%A1sis.jpg", "d:/zvit4/diplom/frontend/images/hero_1.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/b/b8/Football_in_bloemfontein.jpg", "d:/zvit4/diplom/frontend/images/hero_2.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Football_match.jpg/1280px-Football_match.jpg", "d:/zvit4/diplom/frontend/images/hero_3.jpg")
]

# Важливо: Вікіпедія вимагає унікальний User-Agent, інакше блокує (помилка 429)
req_headers = {
    'User-Agent': 'FootballHubApp/1.0 (https://github.com/romantiho; contact@example.com)'
}

for url, dest in urls:
    print(f"Завантаження {url} ...")
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req) as response:
            with open(dest, 'wb') as f:
                f.write(response.read())
        print(f"Успішно збережено: {dest}")
    except Exception as e:
        print(f"Помилка завантаження: {e}")
