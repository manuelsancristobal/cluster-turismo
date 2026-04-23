---
layout: project
title: "Atractivos Ancla y Brechas en los Clústeres Turísticos de Chile"
category: Estadística e Inferencia
description: "Análisis de brechas turísticas en Chile: identificación de oportunidades de inversión mediante clustering espacial HDBSCAN de 3,996 atractivos permanentes."
github_url: "https://github.com/manuelsancristobal/cluster-turismo"
tech_stack:
  - Python
  - HDBSCAN
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

Chile cuenta con diversos atractivos turísticos distribuidos a lo largo de su territorio. Algunos cuentan con atractivos de jerarquía internacional que funcionan como **anclas** que "tiran" la oferta turística del territorio. En este análisis identifico qué proporción de los clústeres turísticos carecen de estas anclas, qué caracteriza a esas agrupaciones y cuáles representan oportunidades de inversión.

Mediante clustering espacial (**HDBSCAN** con métrica Haversine) sobre las coordenadas de **3.996 atractivos permanentes**, identifiqué **79 clústeres territoriales**. El hallazgo principal: **uno de cada tres clústeres identificados** ya posee masa crítica turística reconocida a nivel nacional, pero carece de un atractivo de proyección internacional — representando oportunidades concretas de inversión para elevar la competitividad de esos destinos.

Los datos provienen del registro oficial de atractivos turísticos 2020 del [Servicio Nacional de Turismo de Chile](https://www.sernatur.cl).

El mapa a continuación muestra los 3.996 atractivos coloreados por jerarquía. Haz click en cualquier punto para ver su detalle, o activa capas adicionales desde el panel de checkboxes. Más abajo encontrarás el análisis completo.

<div style="position: relative; width: 100%; padding-bottom: 75%; overflow: hidden; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
  <iframe
    src="/proyectos/cluster-turismo/assets/mapa_interactivo.html"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
    loading="lazy"
    title="Mapa interactivo de atractivos turísticos de Chile"
    allowfullscreen>
  </iframe>
</div>

## 1. Exploración Inicial

El dataset contiene 4.048 atractivos turísticos. Para este análisis nos centramos en los **atractivos permanentes**, descartando los "Acontecimientos Programados" (eventos temporales). Tras validar coordenadas dentro de los límites continentales de Chile, quedamos con **3.996 registros**.

Cada atractivo está clasificado por jerarquía: Local, Regional, Nacional o Internacional.

![Distribución de atractivos por jerarquía](./assets/img/jerarquias.png)

Los histogramas de coordenadas confirman la cobertura esperada: Chile continental entre -17° y -56° de latitud, y -66° a -75° de longitud. Se identifican también los registros de las islas Robinson Crusoe y Rapa Nui.

![Distribución geográfica de coordenadas](./assets/img/histogramas_coordenadas.png)

## 2. Clustering Espacial

### ¿Por qué HDBSCAN?

Los atractivos turísticos en Chile presentan densidades muy variables — zonas densas como Santiago versus zonas dispersas como Aysén. Utilicé **HDBSCAN** porque se adapta automáticamente a diferentes niveles de densidad sin necesidad de fijar un radio de búsqueda ni la cantidad de clústeres.

Respecto a la métrica de distancia, inicialmente probé K-means, pero los clústeres resultantes mostraban puntos lejanos como agrupados. Esto ocurre porque K-means usa distancia euclidiana, que no considera la curvatura de la Tierra. La **métrica Haversine** calcula la distancia esférica real entre coordenadas geográficas.

Para el parámetro `min_cluster_size=10`, un grupo de al menos 10 atractivos constituye un clúster territorial relevante.

**Resultado:** 79 clústeres identificados. El 33.2% de los atractivos no se asigna a ningún clúster — estos puntos de ruido requieren un análisis más profundo que abordamos en la sección 5.

### Distribución por Clústeres

![Top 15 clústeres por cantidad de atractivos](./assets/img/top_clusters.png)

## 3. Análisis de Brechas: Clústeres sin Atractivo Ancla

### ¿Qué es un atractivo ancla?

El concepto proviene del **retail**: en un centro comercial, la tienda ancla es aquella marca de alto reconocimiento que genera el flujo de visitantes del que se benefician todas las demás tiendas. En turismo, la lógica es la misma: un **atractivo ancla** es aquel de jerarquía superior cuyo reconocimiento motiva el desplazamiento de turistas hacia un destino, beneficiando al resto de la oferta turística local.

Esta idea se formaliza en la *anchor-point theory* (Golledge, 1978), que propone que las personas organizan su conocimiento espacial de forma jerárquica alrededor de puntos ancla de mayor importancia.

### Clasificación de clústeres

Definí tres categorías según la presencia de atractivos de jerarquía superior para los 79 clústeres:

| Categoría | Definición | N° Clústeres |
|---|---|---|
| **Con ancla internacional** | Al menos 1 atractivo de jerarquía INTERNACIONAL | 52 |
| **Solo ancla nacional** | Al menos 1 NACIONAL, pero 0 INTERNACIONAL | 26 |
| **Sin ancla** | Sin atractivos NACIONAL ni INTERNACIONAL | 1 |

Los clústeres **"solo ancla nacional"** (33% del total) son los más interesantes para la política pública: ya tienen masa crítica turística reconocida a nivel país, pero carecen de un atractivo de proyección internacional. Estos representan **oportunidades de inversión** claras para elevar su competitividad.

![Distribución de clústeres por categoría de ancla](./assets/img/donut_anclas.png)

## 4. Conclusión Parcial: Clustering General

El análisis clustering inicial revela que 79 clústeres territoriales se forman a nivel nacional usando HDBSCAN con la métrica Haversine. De estos, una proporción significativa opera sin un atractivo ancla de jerarquía internacional. Los clústeres clasificados como **"solo ancla nacional"** (26 en total) son especialmente relevantes: ya poseen reconocimiento a nivel país y masa crítica de atractivos, pero carecen del elemento diferenciador que atraiga turismo internacional.

Sin embargo, este análisis inicial solo captura **el 66.8% de los atractivos** en clústeres coherentes. El restante **33.2% (1.325 atractivos)** queda como "ruido" o sin agrupación espacial clara bajo los parámetros de densidad iniciales. Estos **atractivos no agrupados** representan una segunda oportunidad de análisis: ¿forman efectivamente clústeres subrepresentados? La siguiente sección aborda esta pregunta.

## 5. Clústeres Emergentes: Una Segunda Capa de Análisis

En HDBSCAN, los puntos que no se asignan a ningún clúster se denominan técnicamente "ruido" (*noise*). Sin embargo, **"ruido estadístico" no equivale a "irrelevancia turística"**. En este proyecto, hemos re-analizado este grupo para identificar **clústeres emergentes**: agrupaciones de atractivos que no alcanzaron la densidad requerida por el modelo principal pero que forman unidades territoriales con potencial.

Los 1.325 atractivos no agrupados inicialmente no son simplemente puntos aislados. Al aplicar nuevamente el algoritmo a este subconjunto, se identifican **21 clústeres adicionales** que agrupan a 855 atractivos (el 64.5% de los que antes eran "ruido").

Estos clústeres emergentes representan atractivos que:

- No alcanzan masa crítica turística visible para el modelo principal
- Están dispersos geográficamente pero con cierta proximidad
- Frecuentemente carecen de atractivos de jerarquía nacional o internacional

Es decir, son zonas turísticas incipientes que podrían beneficiarse de agrupamiento estratégico e inversión focalizada.

## 6. Caracterización Geográfica de Atractivos no Agrupados

La distribución regional de los 1.325 atractivos no agrupados muestra concentración en ciertas zonas:

![Atractivos rezagados por región](./assets/img/rezagados_por_region.png)

Las regiones de O'Higgins, Biobío y Los Ríos lideran en cantidad de atractivos sin agrupamiento claro. Esto puede indicar:

1. **Oportunidades de crecimiento:** Si estos atractivos se desarrollan estratégicamente, podrían formar clústeres competitivos
2. **Fragmentación territorial:** La ausencia de anclas fuertes podría dificultar la coordinación turística regional

## 7. Diagnóstico de Superposición: Clústeres Emergentes vs Clústeres Principales

Un aspecto crítico es entender **cómo se relacionan estos 21 clústeres emergentes con los 79 clústeres del análisis principal**. ¿Se solapan? ¿Son complementarios? ¿Genuinamente independientes?

![Clasificación de superposición entre clústeres](./assets/img/donut_superposicion.png)

La clasificación revela tres tipos de relación territorial para esta segunda capa (porcentajes calculados geométricamente sobre las envolventes convexas):

- **Contenido:** Clústeres emergentes que caen totalmente dentro de los límites del clustering principal. Representan micro-destinos o atractivos secundarios dentro de zonas ya consolidadas.
- **Parcialmente superpuesto:** Intersectan con clústeres generales pero mantienen su propia autonomía espacial. Podrían constituir subzonas de especialización.
- **Genuinamente rezagado:** Clústeres completamente fuera de los límites de la capa principal. Estos representan **vacíos de cobertura** en el análisis inicial y son prioridades para el desarrollo de nuevos destinos.

### Implicancias de Política Pública: De la Masa Crítica a la Gobernanza

El **Informe de Sistematización de Gobernanzas Turísticas (Sernatur, 2024)** subraya que la brecha más crítica en los destinos chilenos es la falta de estructuras de coordinación local o "gobernanzas". Mi análisis permite priorizar dónde implementar estas estructuras:

1. **Laboratorios de Gobernanza:** Los clústeres emergentes "Genuinamente Rezagados" son candidatos ideales para los nuevos modelos de gobernanza propuestos por Sernatur. Al tener masa crítica pero carecer de estructura oficial (como una ZOIT), representan el escenario perfecto para una intervención desde cero basada en evidencia.
2. **Especialización de nichos:** Los clústeres "parcialmente superpuestos" pueden evitar la "duplicidad de esfuerzos" mencionada en el informe de 2024, enfocándose en nichos que complementen a los destinos maduros cercanos.
3. **Optimización de recursos municipales:** Al identificar clústeres que cruzan límites comunales, se facilita la articulación inter-municipal, un desafío clave detectado por Sernatur para superar la fragmentación del presupuesto público.

## 8. Comparación de Tamaños: El Hallazgo de la "Masa Crítica Invisible"

Una pregunta natural es: ¿Qué tan grandes son realmente estos clústeres emergentes? ¿Existen diferencias sustantivas de volumen frente a los destinos ya establecidos?

![Boxplot: Tamaño de destinos oficiales vs clústeres rezagados](./assets/img/comparativa_boxplot.png)

El boxplot revela un hallazgo contra-intuitivo: la mediana de atractivos en los clústeres emergentes (~25) es **prácticamente idéntica** a la de los clústeres principales y destinos oficiales. 

Esto nos lleva a un insight clave: la **"Masa Crítica Invisible"**. Los datos demuestran que existen territorios en Chile que ya poseen el volumen de atractivos necesario para ser destinos consolidados, pero permanecen fuera del radar de la política pública. Su invisibilidad no se debe a la falta de masa crítica, sino a la **jerarquía de sus componentes**: al estar formados mayoritariamente por atractivos locales o regionales, no logran "activar" el radar oficial que prioriza las anclas internacionales.

## 9. Conclusión Final: Hacia un Mapeo Integral de Oportunidades

El análisis de dos capas — clústeres principales + clústeres emergentes — revela un panorama turístico chileno más complejo que lo que sugiere el clustering convencional:

1. **Los 79 clústeres principales** representan espacios turísticos con masa crítica y (frecuentemente) anclas de jerarquía nacional o internacional. De estos, 26 carecen de anclas internacionales, generando oportunidades concretas de inversión.
2. **Los 21 clústeres emergentes** —surgidos de atractivos no agrupados en el análisis principal— representan espacios de **desarrollo emergente**. No son espacios vacíos, sino territorios con potencial subutilizado.
3. **La Paradoja de la Masa Crítica:** Chile posee "motores listos" —clústeres con masa crítica suficiente (25+ atractivos)— que hoy operan en las sombras. El desarrollo de estos destinos no requiere necesariamente crear nuevos atractivos, sino "encender" la jerarquía de los existentes.

**Recomendaciones Estratégicas:**

- **Arbitraje de inversión:** En lugar de saturar destinos maduros, existe una oportunidad de alto impacto en los clústeres emergentes de gran tamaño. Invertir en una única **ancla internacional** en estas zonas podría convertir un clúster invisible en un destino competitivo.
- **Gestión Inteligente de Destinos:** Alineado con la visión de Sernatur (2024), se recomienda transitar hacia una toma de decisiones basada en datos espaciales. Este mapa de clústeres es la base para identificar dónde la "masa crítica" ya existe y solo falta el impulso de una gobernanza profesional.
- **Fondos para conectividad y visibilidad:** Priorizar los clústeres "genuinamente rezagados" para integrarlos formalmente a la red de Destinos Turísticos Oficiales de Chile.


<div class="methodology-box" style="margin-top: 2rem; padding: 1.5rem; background: var(--bg-light); border-radius: 8px; border-left: 4px solid var(--secondary);">
    <p style="margin: 0; font-size: 0.95rem;">📓 <strong>Metodología completa:</strong> El detalle del análisis, incluyendo la comparación con destinos oficiales de SERNATUR y el diagnóstico de atractivos rezagados, está disponible en el
    <a href="https://colab.research.google.com/drive/1S8SzY1u5VMOl1POjpBA1c02yPm-uK5r1?usp=sharing" target="_blank" style="color: var(--secondary); font-weight: 600;">notebook de Google Colab</a>.</p>
</div>
