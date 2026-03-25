@echo off
echo Starting Django server on port 8001...
start http://127.0.0.1:8001/admin/
python manage.py runserver 8001
