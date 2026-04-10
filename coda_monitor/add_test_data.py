import os
from pathlib import Path


def check_structure():
    base = Path.cwd()
    print(f"Checking structure in: {base}")
    print("=" * 50)

    # Required files
    required_files = [
        'manage.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        '.env',
        'entrypoint.sh'
    ]

    print("\n✅ Required files:")
    for file in required_files:
        exists = (base / file).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")

    # Required directories
    required_dirs = [
        'coda_monitor',  # Settings directory
        'monitor',  # App directory
        'logs'  # Logs directory
    ]

    print("\n📁 Required directories:")
    for dir_name in required_dirs:
        exists = (base / dir_name).is_dir()
        status = "✓" if exists else "✗"
        print(f"  {status} {dir_name}/")

    # Check settings
    settings_file = base / 'coda_monitor' / 'settings.py'
    if settings_file.exists():
        print("\n✅ Django settings found")
    else:
        print("\n❌ Django settings missing!")

    # Check app
    app_dir = base / 'monitor'
    if app_dir.exists():
        models_file = app_dir / 'models.py'
        views_file = app_dir / 'views.py'
        print(f"  ✓ models.py: {models_file.exists()}")
        print(f"  ✓ views.py: {views_file.exists()}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    check_structure()