import ssl
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context

urls = [
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Allianz_Arena_M%C3%BCnchen.jpg/1280px-Allianz_Arena_M%C3%BCnchen.jpg",
        "d:/zvit4/diplom/frontend/images/hero_1.jpg",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Football_pitch_%28soccer_field%29.jpg/1280px-Football_pitch_%28soccer_field%29.jpg",
        "d:/zvit4/diplom/frontend/images/hero_2.jpg",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Football_in_bloemfontein.jpg/1280px-Football_in_bloemfontein.jpg",
        "d:/zvit4/diplom/frontend/images/hero_3.jpg",
    ),
]

req_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

for url, dest in urls:
    print(f"Downloading {url} to {dest}...")
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req) as response:
            with open(dest, "wb") as f:
                f.write(response.read())
        print("Done")
    except Exception as e:
        print(f"Failed: {e}")
