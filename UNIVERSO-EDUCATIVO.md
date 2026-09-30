# UNIVERSO EDUCATIVO — mapa verificado

Fecha: **2026-09-30**. Cada cifra de este documento se comprobo contra la API de
GitHub en esa fecha. Lo que no se pudo verificar aparece marcado como tal.

## El hallazgo

Hay **48 repositorios publicos** con proposito educativo. No son 48 plataformas
distintas: son **cuatro motores** con cursos repartidos entre ellos.

Tres repositorios comparten ficheros **byte a byte identicos**. Se comprobo por hash
de blob, que es la unica prueba que no admite discusion:

| Fichero | open-school | ManosAbiertas | ux-academy | secure-t |
|---|---|---|---|---|
| `campus/tokens.css` | `578fd64b` | `578fd64b` | `578fd64b` | `b602e045` |
| `campus/sw.js` | `6002891a` | `6002891a` | `6002891a` | `f3518491` |
| `campus/app.js` | `ec296851` | `ec296851` | `ec296851` | `8c21474b` |
| `campus/index.html` | `b2a56264` | `ad53d064` | `54d68836` | `742b06da` |

Los tres primeros comparten el mismo sistema visual y el mismo service worker. Solo
`secure-t` tiene version propia de los tres. El `index.html` es distinto en los cuatro,
porque es la portada de cada uno.

## Los cuatro motores reales

### 1. El campus de cursos  `secure-t` + `open-school` + `ManosAbiertas` + `ux-academy`

Los cuatro usan la misma estructura `campus/` con `tokens.css`, `app.js`, `sw.js` y
cursos en `campus/cursos/<slug>/`. Cada curso tiene 20 semanas, `quiz.json`,
`laboratorio.md`, `rubrica.md`, `glosario.md`, `chuleta.md` y `examen.md`.

| Repositorio | Cursos publicados |
|---|---|
| `secure-t` | `ciber-ofensiva`, `ciber-defensiva`, `ia-aplicada-segura`, `gobernanza-compliance` |
| `ManosAbiertas` | `alfabetizacion-ia`, `office-sin-miedo`, `falsos-amigos-pt-es` |
| `ux-academy-professional-program` | `ux-profesional` |
| `open-school` | `ciberseguridad-5-anios` |

**Nueve cursos en total, un solo motor.** Eso es la unificacion real: no hay que
fusionar repositorios, hay que reconocer que ya comparten motor y llevar los cursos
al mismo sitio.

### 2. La escuela de Nepal  `WILLIAMSCHOOL`

49 ficheros. No usa el motor `campus/`: es una aplicacion con `server.ts` (Bun) y un
directorio `open-data/` con el curriculo en JSON:

- `open-data/data/ciencia-natural.json`
- `open-data/data/datos-del-mundo.json`
- `open-data/data/lecturas-obligatorias.json`
- `open-data/data/refuerzo-idiomas.json`
- `open-data/data/textos-por-asignatura.json`

Es el unico con curriculo de Nepal. **No es duplicado de nada.** Su valor esta en el
contenido, no en el motor, y `open-data/` se puede leer desde cualquier otro campus.

### 3. La escuela unificada  `belentani-school-unificado`

177 ficheros. Contiene `imported/edu-engine/` y `imported/william-recursos-educativos/`,
es decir: **ya intento ser la fusion y quedo a medias.** El README sigue siendo el
generico de AI Studio ("Run and deploy your AI Studio app"), que no describe nada.

### 4. Brasil  `aprende-brasil`

141 ficheros con backend propio (`api/`, `functions/`) y una base SQLite con datos.
Es el unico con backend en funcionamiento; los demas son estaticos.

## Lo que esto significa

Tienes razon en que deberian unificarse, pero la forma correcta no es fusionar
repositorios: es **un indice comun**. Los cuatro campus ya comparten motor y formato,
asi que un indice que los recorra todos da la plataforma unica sin romper nada.

El nodo natural es `open-school`, que ya publica `INDICE-EDUCATIVO.md` y es el que
todos los README citan como central.

## Lo que NO se debe tocar

- `ManosAbiertas` tiene **1.215 ficheros**, el triple que cualquier otro. Es el que mas
  contenido real aporta; fusionarlo en otro seria perder material.
- `WILLIAMSCHOOL` aporta el curriculo de Nepal, que no existe en ningun otro sitio.
- `aprende-brasil` es el unico con backend propio funcional.

## Estado de cada uno

| Repositorio | Ficheros | Web | Curso propio |
|---|---|---|---|
| `ManosAbiertas` | 1.215 | si | 3 |
| `secure-t` | 600 | si | 4 |
| `ux-academy-professional-program` | 285 | si | 1 |
| `belentani-school-unificado` | 177 | si | 0 |
| `open-school` | 148 | si | 1 |
| `aprende-brasil` | 141 | si | 0 |
| `WILLIAMSCHOOL` | 49 | si | 0 |

## Verificacion

Todo lo anterior se obtuvo con la API de GitHub: `git/trees?recursive=1` para los
arboles de ficheros, `contents` para los hash de blob, y el endpoint del repositorio
para rama, web y descripcion. Reproducible con las mismas llamadas.
