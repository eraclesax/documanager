#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv

# carica variabili di ambiente subito, metterle qui serve per l'ambiente di sviluppo
load_dotenv('.env')
# Fix per alcuni sistemi windows
WIN_DLL_FIX = os.getenv("WIN_DLL_FIX", "false").lower() == "true"
if WIN_DLL_FIX:
    import ctypes
    os.add_dll_directory(r"C:\msys64\mingw64\bin")
    ctypes.CDLL("libpango-1.0-0.dll")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
