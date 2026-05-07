# #!/usr/bin/env bash
# set -o errexit

# # ----------------------------------------------------------------
# # Render build script
# # Виконується на Linux-сервері Render при кожному деплої.
# # DJANGO_SETTINGS_MODULE=my_project.settings.prod (з render.yaml)
# # ----------------------------------------------------------------

# pip install -r requirements.txt

# python manage.py collectstatic --no-input

# python manage.py migrate

# # ----------------------------------------------------------------
# # Завантаження даних з фікстури (міграція з локальної MySQL)
# # Файл fixtures/render_migration.json генерується локально через:
# #   python scripts/export_to_fixture.py
# # і комітиться в репозиторій перед деплоєм.
# # ----------------------------------------------------------------
# FIXTURE_FILE="fixtures/render_migration.json"

# if [ -f "$FIXTURE_FILE" ]; then
#     echo ">>> Знайдено фікстуру $FIXTURE_FILE — завантаження даних..."
#     python manage.py loaddata "$FIXTURE_FILE" && \
#         echo ">>> Дані успішно завантажено з фікстури." || \
#         echo ">>> УВАГА: помилка при завантаженні фікстури (дані могли вже існувати)."
# else
#     echo ">>> Фікстуру $FIXTURE_FILE не знайдено — пропускаємо завантаження даних."
# fi

# # ----------------------------------------------------------------
# # Створення суперкористувача (якщо не існує)
# # Змінні DJANGO_SUPERUSER_* задаються в render.yaml або вручну в Render Dashboard.
# # ----------------------------------------------------------------
# python manage.py shell -c "
# import os
# from django.contrib.auth import get_user_model
# User = get_user_model()
# username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
# if not User.objects.filter(username=username).exists():
#     User.objects.create_superuser(
#         username,
#         os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
#         os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123'),
#     )
#     print(f'Суперкористувача {username!r} створено.')
# else:
#     print(f'Суперкористувач {username!r} вже існує.')
# "

# # якщо є dump файл у репозиторії
# if [ -f Football_data.json ]; then
#   echo "📥 Loading initial data..."
#   python manage.py loaddata Football_data.json || echo "⚠️ Data already loaded or failed"
# fi

#!/usr/bin/env bash
set -o errexit

echo ">>> Встановлення залежностей..."
pip install -r requirements.txt

echo ">>> Збір статичних файлів..."
python manage.py collectstatic --no-input

echo ">>> Застосування міграцій..."
python manage.py migrate

echo ">>> Деплой успішний! (Дані та адміна створимо пізніше)"