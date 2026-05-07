"""
Script to export data from local MySQL database to a JSON fixture.
Run this LOCALLY before deploying to Render.

Usage:
    python scripts/export_to_fixture.py

After running:
    git add fixtures/render_migration.json
    git commit -m "chore: add data fixture for Render migration"
    git push
"""

import os
import sys
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root is one level above the scripts/ directory
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "fixtures"
OUTPUT_FILE = FIXTURES_DIR / "render_migration.json"

SETTINGS_MODULE = "my_project.settings.local"

# ---------------------------------------------------------------------------
# Tables to exclude from the dump
# ---------------------------------------------------------------------------
EXCLUDE_TABLES = [
    "contenttypes",                       # auto-recreated after migrate
    "auth.permission",                    # auto-recreated after migrate
    "admin.logentry",                     # not needed
    "token_blacklist.outstandingtoken",   # JWT tokens - do not migrate
    "token_blacklist.blacklistedtoken",
    "sessions",                           # sessions - do not migrate
]


def run_dumpdata() -> bool:
    """Run manage.py dumpdata and save JSON to fixtures/render_migration.json."""
    FIXTURES_DIR.mkdir(exist_ok=True)

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "manage.py"),
        "dumpdata",
        f"--settings={SETTINGS_MODULE}",
        "--natural-foreign",  # safer ForeignKey serialization across DBs
        "--natural-primary",  # safer PrimaryKey serialization across DBs
        "--indent=2",
        # Do NOT use --output: on Windows it uses the system codec (cp1252)
        # and fails on Cyrillic content. We capture stdout and write utf-8 manually.
    ]

    for table in EXCLUDE_TABLES:
        cmd += ["--exclude", table]

    print("=" * 60)
    print("Export data: local MySQL -> JSON fixture")
    print("=" * 60)
    print(f"  Settings : {SETTINGS_MODULE}")
    print(f"  Output   : {OUTPUT_FILE}")
    print()

    result = subprocess.run(
        cmd,
        capture_output=True,   # get raw bytes - avoids cp1252 decoding
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )

    if result.returncode != 0:
        print("ERROR during dumpdata:")
        print(result.stderr.decode("utf-8", errors="replace"))
        return False

    stderr_text = result.stderr.decode("utf-8", errors="replace").strip()
    if stderr_text:
        print("Warnings:")
        print(stderr_text)

    # Write raw bytes (already utf-8 JSON from Django)
    OUTPUT_FILE.write_bytes(result.stdout)

    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\nDone! File size: {size_kb:.1f} KB")
    return True


def print_next_steps():
    print()
    print("=" * 60)
    print("Next steps:")
    print("=" * 60)
    print()
    print("  1. Add fixture to git:")
    print("       git add fixtures/render_migration.json")
    print()
    print("  2. Commit:")
    print('       git commit -m "chore: add data fixture for Render"')
    print()
    print("  3. Push to GitHub:")
    print("       git push")
    print()
    print("  Render will pick up the changes and run build.sh,")
    print("  which loads the fixture into PostgreSQL via loaddata.")
    print()


if __name__ == "__main__":
    success = run_dumpdata()
    if success:
        print_next_steps()
    else:
        print()
        print("Check that your local MySQL server is running")
        print("and settings in my_project/settings/local.py are correct.")
        sys.exit(1)
