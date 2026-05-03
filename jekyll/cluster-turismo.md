---
layout: project
title: "Atractivos Ancla y Brechas en los Clústeres Turísticos de Chile"
category: Estadística e Inferencia
description: "Análisis de brechas turísticas en Chile: identificación de oportunidades de inversión mediante clustering espacial HDBSCAN de 3,996 atractivos permanentes."
github_url: "https://github.com/manuelsancristobal/cluster-turismo"
tech_stack:
  - Python
  - scikit-learn/HDBSCAN
  - Pandas
  - NumPy
  - Shapely
  - SciPy
  - Folium
  - PyDeck
  - Matplotlib
  - Seaborn
  - pytest
---

**Chile posee territorios con masa crítica suficiente para ser destinos consolidados que permanecen invisibles para la política pública.** Mediante el uso de clustering espacial HDBSCAN sobre **3.996 atractivos permanentes**, este análisis identifica 94 clústeres consolidados y descubre 26 clústeres emergentes que operan fuera del radar oficial, constituyendo lo que defino como la "Masa Crítica Invisible".

<div style="position: relative; width: 100%; padding-bottom: 75%; overflow: hidden; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
  <iframe
    src="/proyectos/cluster-turismo/assets/mapa_interactivo.html"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
    loading="lazy"
    title="Mapa interactivo de atractivos turísticos de Chile"
    allowfullscreen>
  </iframe>
</div>

## 1. Hallazgo: La "Masa Crítica Invisible"

**Existen clústeres emergentes con un volumen de atractivos idéntico al de los destinos principales de Chile.** Al re-analizar los datos descartados por el modelo inicial, identifiqué territorios con una mediana de ~25 atractivos locales y regionales. Estos destinos poseen el potencial necesario para captar flujos, pero carecen de la jerarquía requerida para "activar" el radar de inversión pública de modo automático.

![Boxplot: Destinos oficiales vs clústeres rezagados](./assets/img/comparativa_boxplot.png)

## 2. Diagnóstico de Superposición y Gestión de Brechas

**La identificación de clústeres "de forma genuina rezagados" permite focalizar esfuerzos de gobernanza donde no existen estructuras previas.** Como se aprecia en la clasificación de superposición, estos vacíos de cobertura son prioridades para la implementación de nuevos modelos de gestión. Por otro lado, los clústeres con superposición parcial ofrecen oportunidades de especialización sin duplicar esfuerzos institucionales.

![Clasificación de superposición entre clústeres](./assets/img/donut_superposicion.png)

## 3. Análisis de Atractivos Ancla e Impacto en Rutas

**Uno de cada tres clústeres posee infraestructura nacional pero carece de un atractivo ancla de jerarquía internacional.** Según la *Anchor-Point Theory*, la ausencia de un motor de desplazamiento global limita el potencial de crecimiento del entorno. Como se puede apreciar en el proyecto de [**Bar Chart Race: Movimiento Aéreo**](/proyectos/barchart-race/), la resiliencia de las rutas internacionales hacia Chile está ligada de modo estrecho a la jerarquía de los destinos que conectan.

![Distribución de clústeres por categoría de ancla](./assets/img/donut_anclas.png)

## 4. Metodología de Clustering Espacial HDBSCAN

**El uso de HDBSCAN permite capturar agrupaciones de densidad variable a lo largo de la geografía nacional.** A diferencia de otros modelos, este algoritmo se adapta de forma orgánica a zonas de alta concentración como Santiago y a áreas dispersas en la Patagonia. La aplicación de la métrica Haversine asegura un cálculo de distancia esférica real de modo exacto sobre la superficie terrestre.

## 5. Caracterización de Atractivos no Agrupados

**Regiones como O'Higgins y Biobío concentran la mayor cantidad de atractivos fragmentados con potencial de consolidación.** Estos puntos, clasificados en una primera instancia como ruido, revelan una oportunidad de crecimiento territorial subutilizado. La consolidación de estos atractivos en destinos integrados es una de las mayores brechas identificadas de modo estructural en el estudio.

---

## Conclusión: Motores Listos para la Inversión

El desarrollo turístico de Chile no requiere crear destinos desde cero, sino elevar la jerarquía de los motores existentes:
- **Arbitraje de inversión:** Crear anclas internacionales en clústeres de "solo ancla nacional" para potenciar el flujo capturado en las rutas analizadas en [**Bar Chart Race**](/proyectos/barchart-race/).
- **Gestión Inteligente:** Utilizar datos espaciales para localizar las gobernanzas propuestas por el sector público de modo estratégico.

<div class="methodology-box" style="margin-top: 2rem; padding: 1.5rem; background: var(--bg-light); border-radius: 8px; border-left: 4px solid var(--secondary);">
    <p style="margin: 0; font-size: 0.95rem;">📌 <strong>Sobre este proyecto:</strong> Esta es una versión rediseñada como aplicación interactiva. El proyecto original está disponible en
    <a href="https://colab.research.google.com/drive/1S8SzY1u5VMOl1POjpBA1c02yPm-uK5r1?usp=sharing" target="_blank" style="color: var(--secondary); font-weight: 600;">Google Colab</a>.</p>
</div>
