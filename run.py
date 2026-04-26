"""
Punto de entrada del proyecto Cluster Turismo.

Uso:
    python run.py              Ver comandos disponibles
    python run.py assets       Genera gráficos y mapa interactivo
    python run.py deploy       Copia archivos al repo Jekyll
    python run.py ver          Abre servidor local
    python run.py test         Ejecuta tests + linting
    python run.py all          Pipeline completo: assets -> deploy
"""

from __future__ import annotations

import os
import subprocess
import sys
import webbrowser

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- Colores ANSI (se desactivan si la terminal no soporta) -----------

def _supports_color() -> bool:
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True

_COLOR = _supports_color()

def _green(text: str) -> str:
    return f"\033[92m{text}\033[0m" if _COLOR else text

def _cyan(text: str) -> str:
    return f"\033[96m{text}\033[0m" if _COLOR else text

def _red(text: str) -> str:
    return f"\033[91m{text}\033[0m" if _COLOR else text

def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m" if _COLOR else text

def _yellow(text: str) -> str:
    return f"\033[93m{text}\033[0m" if _COLOR else text


def _run(cmd: list[str], label: str) -> bool:
    print(f"\n{_cyan('>')} {_bold(label)}")
    print(f"  {' '.join(cmd)}\n")
    env = os.environ.copy()
    # Asegurar que el directorio actual esté en PYTHONPATH para ejecuciones directas
    env["PYTHONPATH"] = os.path.join(_PROJECT_ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(cmd, cwd=_PROJECT_ROOT, env=env)
    if result.returncode != 0:
        print(f"\n{_red('X')} {label} fallo (exit code {result.returncode})")
        return False
    print(f"\n{_green('OK')} {label}")
    return True


def cmd_assets() -> bool:
    return _run([sys.executable, "-m", "cluster_turismo.cli.generate"], "Assets - Generando gráficos y mapas")


def cmd_deploy() -> bool:
    return _run([sys.executable, "-m", "cluster_turismo.cli.deploy"], "Deploy - Copiando al repo Jekyll")


def cmd_ver() -> bool:
    url = "http://127.0.0.1:8000/assets/mapa_interactivo.html"
    print(f"\n{_cyan('>')} {_bold('Servidor local')}")
    print(f"  Abriendo {url} en el navegador...")
    print(f"  Presiona Ctrl+C para detener el servidor.\n")
    webbrowser.open(url)
    try:
        subprocess.run(
            [sys.executable, "-m", "http.server", "8000", "--bind", "127.0.0.1"],
            cwd=_PROJECT_ROOT,
        )
    except KeyboardInterrupt:
        print(f"\n{_green('OK')} Servidor detenido.")
    return True


def cmd_test() -> bool:
    ok1 = _run([sys.executable, "-m", "pytest", "tests/", "-v"], "Tests - pytest")
    ok2 = _run([sys.executable, "-m", "ruff", "check", "src/", "tests/"], "Linting - ruff")
    return ok1 and ok2


def cmd_all() -> bool:
    if not cmd_assets():
        return False
    return cmd_deploy()


COMMANDS = {
    "assets":  lambda _: cmd_assets(),
    "deploy":  lambda _: cmd_deploy(),
    "ver":     lambda _: cmd_ver(),
    "test":    lambda _: cmd_test(),
    "all":     lambda _: cmd_all(),
}


def cmd_help() -> None:
    print(f"""
{_bold('Cluster Turismo - Comandos disponibles')}

  python run.py {_green('assets')}   Genera gráficos y mapas interactivos
  python run.py {_green('deploy')}   Copia archivos al repo Jekyll
  python run.py {_green('ver')}      Abre servidor local
  python run.py {_green('test')}     Ejecuta tests (pytest) + linting (ruff)
  python run.py {_green('all')}      Pipeline completo: assets -> deploy

{_yellow('Ejemplo:')} python run.py all
""")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        cmd_help()
        sys.exit(0)
    command = args[0]
    if command not in COMMANDS:
        print(f"{_red('Error:')} Comando desconocido '{command}'")
        cmd_help()
        sys.exit(1)
    ok = COMMANDS[command](args[1:])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
