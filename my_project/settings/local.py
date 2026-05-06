from .base import *

DEBUG = True

DB_ENGINE = os.environ.get("DB_ENGINE", default_engine)
DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
        "NAME": os.environ.get("DB_NAME", default_db_name),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "1234"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
    }
}

if "mysql" in DB_ENGINE:
    DATABASES["default"]["OPTIONS"] = {"charset": "utf8mb4"}