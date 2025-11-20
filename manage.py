import os
import sys

if __name__ == "__main__":
    # ejecuta comandos de Django (runserver, shell, etc.)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taller_mecanico.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Asegurate de tener Django instalado") from exc
    execute_from_command_line(sys.argv)
