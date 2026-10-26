"""Legacy acceptance archive helpers; the fixed-company live test is retired.

Use the real selected-episode workflow for provider calls. These constants and
SQLite helpers remain available solely to inspect/recover historical artifacts.
"""
import json
import subprocess
from pathlib import Path

FOLDER = Path('dist/final-directed-acceptance')
COMPANY = 'BlackBerry'
TOPIC = 'Por qué perdió su liderazgo en el mercado de teléfonos y cómo cambió su negocio'


def store(action, **body):
    result = subprocess.run(['node', 'tools/episode_acceptance_store.mjs'],
        input=json.dumps({'action': action, **body}), text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError('El contrato de persistencia editorial rechazó la prueba')
    return json.loads(result.stdout)


def main():
    raise SystemExit(
        'Prueba fija de BlackBerry retirada: usa phase=episode con una solicitud '
        'del episodio realmente seleccionado por el estudio o por el propietario. '
        'Este comando no realiza búsquedas ni llamadas de IA.')


if __name__ == '__main__':
    main()
