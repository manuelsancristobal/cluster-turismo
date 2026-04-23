"""Copia assets y markdown del proyecto al repo Jekyll local."""

from __future__ import annotations

import logging
import shutil

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
    if JEKYLL_ASSETS_DIR.exists():
        shutil.rmtree(JEKYLL_ASSETS_DIR)
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
