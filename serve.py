# Простий скрипт для запуску HTTP сервера

import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Сервер запущено на http://localhost:{PORT}")
    print(f"Відкрийте у браузері: http://localhost:{PORT}/index.html")
    print("Натисніть Ctrl+C для зупинки сервера")
    httpd.serve_forever()
