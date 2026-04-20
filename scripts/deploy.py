"""Copia assets y markdown del proyecto al repo Jekyll local."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rutas ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_IMG_DIR = ASSETS_DIR / "img"

_jekyll_env = os.getenv("JEKYLL_REPO")
if not _jekyll_env:
    raise OSError(
        "Variable JEKYLL_REPO no definida. "
        "Exporta la ruta al repo Jekyll: export JEKYLL_REPO=/path/to/repo"
    )
JEKYLL_REPO = Path(_jekyll_env)
JEKYLL_BASE = JEKYLL_REPO / "proyectos" / "cluster-turismo"
JEKYLL_ASSETS_DIR = JEKYLL_BASE / "assets"
JEKYLL_IMG_DIR = JEKYLL_ASSETS_DIR / "img"
JEKYLL_PROJECTS_DIR = JEKYLL_REPO / "_projects"
JEKYLL_PROJECT_MD = PROJECT_ROOT / "jekyll" / "cluster-turismo.md"


def deploy() -> None:
    """Copia assets y .md al repo Jekyll. El push es manual."""
    # ── Mapa interactivo (HTML) ──
    mapa_src = ASSETS_DIR / "mapa_interactivo.html"
    if mapa_src.exists():
        JEKYLL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mapa_src, JEKYLL_ASSETS_DIR / mapa_src.name)
        logger.info("Copiado mapa → %s", JEKYLL_ASSETS_DIR)
    else:
        logger.warning("Mapa no encontrado: %s", mapa_src)

    # ── Imágenes (PNGs) ──
    if ASSETS_IMG_DIR.exists():
        JEKYLL_IMG_DIR.mkdir(parents=True, exist_ok=True)
        count = 0
        for f in ASSETS_IMG_DIR.glob("*.png"):
            shutil.copy2(f, JEKYLL_IMG_DIR / f.name)
            count += 1
        logger.info("Copiados %d PNGs → %s", count, JEKYLL_IMG_DIR)
    else:
        logger.warning("Directorio de imágenes no existe: %s", ASSETS_IMG_DIR)

    # ── Markdown del proyecto ──
    if JEKYLL_PROJECT_MD.exists():
        JEKYLL_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(JEKYLL_PROJECT_MD, JEKYLL_PROJECTS_DIR / JEKYLL_PROJECT_MD.name)
        logger.info("Copiado proyecto .md → %s", JEKYLL_PROJECTS_DIR)
    else:
        logger.warning("Markdown no encontrado: %s", JEKYLL_PROJECT_MD)

    logger.info("Deploy completado. Recuerda hacer git push en el repo Jekyll.")


if __name__ == "__main__":
    deploy()
