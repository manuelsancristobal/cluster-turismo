"""Copia assets y markdown del proyecto al repo Jekyll local."""

from __future__ import annotations

import logging
import os
import shutil
import stat
import time
from pathlib import Path

from cluster_turismo.config import (
    ASSETS_DIR,
    JEKYLL_ASSETS_DIR,
    JEKYLL_IMG_DIR,
    JEKYLL_PROJECT_MD,
    JEKYLL_PROJECTS_DIR,
    JEKYLL_REPO,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def _on_rm_error(func, path, exc_info):
    """Manejador de errores para shutil.rmtree (maneja archivos de solo lectura)."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def _robust_rmtree(path: Path, max_retries: int = 3, delay: float = 0.5) -> None:
    """Elimina un directorio de forma robusta, reintentando en caso de bloqueos (Windows)."""
    if not path.exists():
        return

    for i in range(max_retries):
        try:
            # Usamos onerror para compatibilidad con Python < 3.12
            shutil.rmtree(path, onerror=_on_rm_error)
            return
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(delay)
                continue
            logger.warning(f"No se pudo eliminar completamente {path} tras {max_retries} intentos: {e}")


def deploy() -> None:
    """Copia assets y .md al repo Jekyll. El push es manual."""
    if JEKYLL_REPO is None:
        raise OSError(
            "\n================================================================================\n"
            "ERROR: Variable de entorno 'JEKYLL_REPO' no definida.\n"
            "Asegúrate de configurar JEKYLL_REPO en tu entorno o en src/cluster_turismo/config.py\n"
            "================================================================================"
        )

    # 1. Limpiar y crear directorios
    logger.info(f"Usando repo Jekyll en: {JEKYLL_REPO}")
    _robust_rmtree(JEKYLL_ASSETS_DIR)
    JEKYLL_IMG_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Copiar assets (PNGs y Mapas HTML)
    logger.info("Copiando assets...")
    # Copiar mapa interactivo principal
    main_map = ASSETS_DIR / "mapa_interactivo.html"
    if main_map.exists():
        shutil.copy2(main_map, JEKYLL_ASSETS_DIR / "mapa_interactivo.html")

    # Copiar imágenes (gráficos)
    local_img_dir = ASSETS_DIR / "img"
    if local_img_dir.exists():
        for img_file in local_img_dir.glob("*.png"):
            shutil.copy2(img_file, JEKYLL_IMG_DIR / img_file.name)

    # 3. Copiar archivo Markdown del proyecto
    logger.info("Copiando archivo markdown...")
    if JEKYLL_PROJECT_MD.exists():
        shutil.copy2(JEKYLL_PROJECT_MD, JEKYLL_PROJECTS_DIR / "cluster-turismo.md")
    else:
        logger.warning(f"No se encontró el archivo markdown en {JEKYLL_PROJECT_MD}")

    logger.info("Despliegue local completado exitosamente.")
    logger.info("RECUERDA: Debes hacer git push en el repositorio Jekyll para ver los cambios online.")


if __name__ == "__main__":
    deploy()
