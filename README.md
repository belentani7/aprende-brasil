# Aprende Brasil

Aprende Brasil es un MVP de plataforma educativa web en portugués brasileño. La experiencia está diseñada alrededor de pequeños pasos de aprendizaje y combina tres trilhas: **Informática**, **Matemática** e **Idiomas**. El objetivo de catálogo es de 2.000 módulos, distribuidos en 680 de Informática, 720 de Matemática y 600 de Idiomas.

## Estado actual

La primera versión entrega un dashboard responsive de estudiante con navegación lateral, saludo contextual, módulo recomendado, progreso general, tiempo de estudio semanal, meta de sesiones, selección de trilha, búsqueda de módulos, agenda, modal de detalle e interacción con el tutor Nilo. Todos los botones principales tienen feedback visible y la interfaz se adapta a escritorio y móvil.

Nilo se ejecuta mediante un procedimiento server-side (`tutor.ask`) que valida el mensaje, fija el área de estudio y utiliza el helper LLM preconfigurado del proyecto. El prompt del tutor limita la respuesta, favorece pistas antes que soluciones y evita inventar notas, progreso o datos personales. La interfaz también ofrece una alternativa local con `speechSynthesis` en pt-BR para probar lectura en voz alta sin exponer ninguna clave.

La integración de OpenVoice está preparada a nivel de producto y contrato, pero no se presenta como activa porque todavía no existe un endpoint o una credencial de inferencia suministrada para este proyecto. Cuando exista el proveedor, debe conectarse detrás de un adaptador server-side y no desde el navegador.

## Arquitectura

El proyecto utiliza React, TypeScript, Vite, TailwindCSS, Express, tRPC, Drizzle, MySQL/TiDB, almacenamiento de objetos y autenticación gestionada por Manus OAuth. El frontend vive en `client/`, los procedimientos en `server/`, el esquema en `drizzle/` y la documentación operativa en la raíz.

La estructura prevista para producción es:

| Capa | Responsabilidad |
| --- | --- |
| Experiencia | Dashboard, catálogo, progreso, agenda, tutor, accesibilidad y responsive design. |
| API | Procedimientos tRPC tipados, validación Zod, autorización y límites de uso. |
| Datos | Usuarios, trilhas, módulos, pasos, progreso, favoritos, metas, conversaciones y versiones editoriales. |
| Objetos | Vídeos, audios, imágenes, exportaciones y materiales descargables mediante storage, no dentro del bundle. |
| IA | Tutor server-side con prompt de sistema, moderación, métricas y fallback controlado. |
| Voz | Captura opcional, transcripción, síntesis configurable y perfil de voz con consentimiento. |

“Dos gigabytes de plataforma” debe entenderse como una capacidad de almacenamiento planificada. El bundle web debe continuar siendo pequeño. Los binarios grandes deben ir a almacenamiento de objetos con metadatos, hash de integridad, límites de tamaño, control de acceso y política de retención.

## 2.000 módulos

El catálogo no se infla con placeholders sin valor pedagógico. La aplicación ya muestra una muestra representativa y la estructura está preparada para cargar el catálogo curado mediante importaciones versionadas. Antes de publicar un módulo se requiere objetivo observable, explicación, ejemplo, práctica, comprobación, siguiente paso, nivel, duración, prerequisitos, idioma, versión y revisión editorial. La distribución editorial objetivo es:

| Área | Módulos | Rutas de ejemplo |
| --- | ---: | --- |
| Informática | 680 | Alfabetización digital, pensamiento computacional, datos, creación web, programación y automatización. |
| Matemática | 720 | Numeración, álgebra, funciones, geometría, medida, estadística, probabilidad y modelación. |
| Idiomas | 600 | Inglés, español, portugués para hablantes de otras lenguas y comunicación profesional. |

## Voz OpenVoice

OpenVoice describe clonación de color tonal desde una referencia corta, control de estilo y uso multilingüe; su repositorio oficial publica V1 y V2 bajo MIT.[1] El artículo académico describe control de emoción, acento, ritmo, pausas, entonación y clonación cross-lingual zero-shot.[2]

Para la integración real se recomienda un servicio aislado de voz con cola de trabajos, límites de duración, caché de audio, borrado y observabilidad. El entorno web no debe ejecutar inferencia pesada dentro de una petición corta si el runtime no la soporta. Las variables sugeridas son `OPENVOICE_API_URL`, `OPENVOICE_API_KEY`, `OPENVOICE_MODEL` y `OPENVOICE_VERSION`, administradas como secretos server-side. El flujo debe comprobar que la persona tiene derecho a usar la grabación, permitir borrar el perfil y conservar únicamente el audio necesario. En ausencia del endpoint, la aplicación comunica la limitación y utiliza `speechSynthesis` del navegador.

## Desarrollo local

```bash
pnpm install
pnpm check
pnpm test
pnpm build
```

El prompt maestro de producto se encuentra en [`MASTER_PROMPT.md`](./MASTER_PROMPT.md) y contiene la especificación de contenido, UX, seguridad, accesibilidad, analítica, voz, criterios de aceptación y camino de escalado.

## Calidad y próximos pasos

La versión actual incluye pruebas del logout y del contrato `tutor.ask`. Antes de producción se deben añadir migraciones y procedimientos para el catálogo, eventos de progreso, favoritos, metas y agenda. Después conviene implementar roles de docente y editor, paginación real, importador de módulos, moderación de conversaciones, consentimiento de voz, proveedor OpenVoice, telemetría de aprendizaje y revisión WCAG 2.2 AA con usuarios reales.

No se deben publicar los 2.000 módulos sólo por alcanzar una cifra. La prioridad es que cada módulo tenga competencia verificable, revisión humana, derechos de contenido y una práctica que ayude a transferir lo aprendido.

## Referencias

[1]: https://github.com/myshell-ai/OpenVoice "myshell-ai/OpenVoice — repositorio oficial y documentación"

[2]: https://arxiv.org/abs/2312.01479 "OpenVoice: Versatile Instant Voice Cloning — artículo académico"
