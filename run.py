"""
Punto de entrada del proyecto Cluster Turismo.

Uso:
    python run.py                   Ver comandos disponibles
    python run.py generate-assets   Genera gráficos y mapa interactivo
    python run.py deploy            Copia archivos al repo Jekyll
    python run.py test              Ejecuta tests + linting
    python run.py all               Pipeline completo: generate-assets -> deploy
"""

from __future__ import annotations

import os
import subprocess
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _run(cmd: list[str], label: str) -> bool:
    print(f"\n> {label}\n  {' '.join(cmd)}\n")
    env = os.environ.copy()
    # Asegurar que el directorio actual esté en PYTHONPATH para ejecuciones directas
    env["PYTHONPATH"] = os.path.join(_PROJECT_ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")
    
    result = subprocess.run(cmd, cwd=_PROJECT_ROOT, env=env)
    if result.returncode != 0:
        print(f"\nFALLÓ: {label} (exit code {result.returncode})")
        return False
    print(f"\nOK: {label}")
    return True


def cmd_generate() -> bool:
    return _run([sys.executable, "-m", "cluster_turismo.cli.generate"], "Generate Assets")


def cmd_deploy() -> bool:
    return _run([sys.executable, "-m", "cluster_turismo.cli.deploy"], "Deploy a Jekyll")


def cmd_test() -> bool:
    ok1 = _run([sys.executable, "-m", "pytest", "tests/", "-v"], "pytest")
    ok2 = _run([sys.executable, "-m", "ruff", "check", "src/", "tests/"], "ruff")
    return ok1 and ok2


def cmd_all() -> bool:
    if not cmd_generate():
        return False
    return cmd_deploy()


COMMANDS = {
    "generate-assets": lambda _: cmd_generate(),
    "deploy":          lambda _: cmd_deploy(),
    "test":            lambda _: cmd_test(),
    "all":             lambda _: cmd_all(),
}


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)
    command = args[0]
    if command not in COMMANDS:
        print(f"Comando desconocido: '{command}'")
        sys.exit(1)
    ok = COMMANDS[command](args[1:])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
