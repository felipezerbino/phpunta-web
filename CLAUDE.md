# CLAUDE.md — Página Web PHPunta (phpunta.uy)

Sitio público de Premium Host Punta. Dueño: **Felipe** (arquitecto, no programador). **Todo en español**, directo y sintético.

## Qué hay acá
- Sitio estático trilingüe: español en la raíz, `/en/` y `/pt/`. 9 páginas por idioma, un `.html` autónomo por página (sin frameworks ni build).
- `assets/img/` (fotos), íconos/favicons, `site.webmanifest`, `sitemap.xml`, `robots.txt`.
- Estética: navy `#0d1b2a`, dorado `#c9a84c`/`#a88a3a`, crema `#faf7f0`; Cormorant Garamond + Jost. SEO completo (meta, OG, JSON-LD, hreflang): mantenerlo al tocar una página y en los tres idiomas.

## Origen (5-nov-2026)
Importado de lo publicado en `https://phpunta.uy` (descarga de las 27 páginas del sitemap + lo que referencian). **Lo que NO está en el repo** porque el servidor no lo entrega:
- `enviar.php` (lo usan los formularios de contacto y de propietarios) — vive solo en el hosting.
- `.htaccess` u otra configuración del servidor, si la hay.
Un deploy NUNCA debe borrar esos archivos del hosting.

## Hosting
cPanel `phpunta.uy` (hostingmontevideo), raíz `public_html/`. Ahí conviven carpetas INTOCABLES de otras apps: `comunicacion/`, `limpiezas/`, `operaciones/`, `pagos/`, `portalpropietarios/`, `portalinmobiliarias/`, `optimizer/`, `mensajes/`, `reservas/`, `wp/`, `wpr/`, `deployer/`. El deploy de la web solo puede escribir los archivos de este repo, sin borrar nada.
Cloudflare: no se usa (la zona se dio de baja el 2-nov-2026; Felipe decidió no seguir por ahora).

## Deploy (6-nov-2026)
- **Push a `main` → `.github/workflows/deploy.yml` → publica en la raíz de phpunta.uy por HTTPS** por el receptor `phpunta.uy/limpiezas/deployer/deploy.php` (app `web`). Secret del repo: `DEPLOY_TOKEN` (= `deployer/deploy_token.txt` de la raíz). Desde el 11-nov ese receptor acepta ese token SOLO para app=web, porque el de la raíz no se puede actualizar por FTP (la cuenta principal está enjaulada en `comunicacion/`). El `deployer/deploy.php` de la raíz quedó viejo y sin uso.
- Sube SOLO lo que cambió desde lo publicado (`https://phpunta.uy/web-version.json` guarda el commit). La primera vez la base es el commit de importación. "Subir todo": Actions → Publicar la web → Run workflow → tildar "completo".
- **Nunca borra.** Un archivo eliminado del repo sigue en el hosting: borrarlo a mano.
- El receptor solo acepta en la web: archivos sueltos en la raíz y carpetas `assets/`, `en/`, `pt/`, `reservas/`, `reservasnueva/`, `alquileres/`; html/css/js/imágenes/video/sitemap. Nada `.php`, `.htaccess` ni ocultos. Una carpeta nueva exige cambiar `deploy.php` (repo phpunta-comunicaciones) y correr allá el workflow "Instalar deploy.php en limpiezas/deployer" (FTP plano: solo con OK de Felipe).
- Lotes de ≤1,5 MB: el tope de subida del PHP del hosting no está medido. Un archivo más grande (los videos de 6-7 MB) puede ser rechazado: el workflow lo dice y hay que subirlo por el Administrador de archivos.
- Verificación: el último paso compara `web-version.json` publicado con el commit.

## Central de reservas (ES/PT/EN — PUBLICADA en /reservas, /pt/reservas, /en/reservas desde el 11-nov-2026)
- **Plantillas** (no se publican, empiezan con _): `reservas/_lista.html` (buscador + lista + mapa) y `reservas/_ficha.html`
  (cada propiedad). Están en ESPAÑOL; `tools/i18n_reservas.py` (PARES es→pt→en aplicados en el armado) genera PT y EN.
  **Regla: todo texto nuevo que vea el visitante lleva su par PT/EN en ese archivo en el mismo cambio** (probar con
  `python3 tools/probar-i18n-reservas.py`: `restos()` tiene que dar 0). Rutas en JS: `BASE` (meta php-base); links entre
  idiomas: `__BASE_ES__/__BASE_PT__/__BASE_EN__` en los pares.
- **Generador** `tools/generar-reservas.py` (corre en cada deploy y una vez por día): lee `/web/seo?lang=` del backend y arma
  la lista y una página por propiedad en los 3 idiomas con SEO completo (title, description, canonical, hreflang, OG, JSON-LD
  VacationRental + BreadcrumbList/ItemList, contenido pre-armado para buscadores) y `sitemap-reservas.xml`. Una propiedad
  nueva publicada en el panel aparece sola. Las páginas generadas no se versionan (.gitignore) y el deploy sube solo las que
  cambiaron (`reservas-manifest.json`).
- **Publicada (11-nov-2026, OK de Felipe):** deploy.yml con `RESERVAS_ES_DIR: reservas` (sin noindex, con
  `sitemap-reservas.xml` en robots.txt); `/reservasnueva/…` quedan como redirecciones a `/reservas/…` (conservan fechas y
  `?sel=`); menús y botones del sitio apuntan a la central de cada idioma (`tools/enlazar-reservas.py`, ya corrido). En el
  hosting la raíz es `public_html/phpunta.uy/`: ahí había `reservas/index.php` redirigiendo a reservas.phpunta.uy, y el
  receptor lo renombra a `index.php.anterior` la primera vez que publica `reservas/index.html` (la respuesta trae
  `retirado`). Para volver atrás: `RESERVAS_ES_DIR: reservasnueva` y renombrar ese archivo a mano.
- Textos de las propiedades en PT/EN: los traduce el backend con la IA en el fondo (v2.754, cache en guias_traducciones);
  mientras no están, salen en español. Estado: `/diag/web-traducciones`.
- Bases y condiciones y Reglas de la casa: `tools/legales_reserva.py` → `python3 tools/generar-legales.py` arma
  `condiciones-reserva.html`, `reglas-de-la-casa.html` y sus versiones PT/EN. La reserva exige aceptar los dos y la política
  (backend v2.753). Horarios de las reglas: check-in 16 h, check-out 10 h.

## Central de reservas (`reservasnueva/`, historia — fase 1 vitrina, 11-nov-2026)
Reemplaza al sitio de reservas de Avantio (reservas.phpunta.uy). Oculta: `noindex`, fuera del sitemap y sin links desde la web; se publica cuando Felipe la apruebe (ahí: sacar noindex, canonical, sitemap, links del menú y decidir la URL final — `alquileres/` ya está habilitada en el receptor).
- `reservasnueva/index.html`: buscador (fechas, huéspedes, zona), filtros que sirven (tipo, dormitorios, piscina, frente al mar, playa, parrillero, jacuzzi, orden), lista con scroll continuo y mapa (Leaflet + OpenStreetMap; CARTO pide clave desde nov-2026) con "Buscar en esta zona" / "Buscar al mover el mapa". El estado vive en la URL (se puede compartir).
- `reservasnueva/_ficha.html`: PLANTILLA de la página de cada propiedad. El deploy corre `tools/generar-fichas.py`, que lee `/web/slugs` del backend y escribe `reservasnueva/<slug>/index.html` (no se versionan: `.gitignore`). Los archivos que empiezan con `_` no se publican. El workflow corre también una vez por día (propiedades nuevas, títulos nuevos). Una propiedad que deja de publicarse conserva su página con "ya no está disponible" (el receptor nunca borra).
- Datos: backend `/web/*` (v2.738): catálogo, ficha, calendario, cotización, búsqueda. El slug (URL) no cambia una vez creado. Títulos = los de Airbnb sin "PHPunta" y nada más (el número del título es sugerente a propósito: no poner la unidad real); precios = total directo (tabla de Avantio con descuentos + limpieza REAL) × (1 + recargo). Config en `app_config.web_reservas` (`recargo_pct`, `sena_pct`, `whatsapp_reservas`).
- **Inmediata o por solicitud (11-nov, backend v2.742):** solo las propiedades marcadas "Inmediata" en el panel (Portal › Web › Lista rápida) pagan la seña online (insignia "⚡ Reserva inmediata" en tarjeta y ficha, filtro en el buscador); el resto —y las inmediatas con menos de 2 días a la llegada— muestran "Solicitar reserva": formulario sin pago, el equipo la aprueba en el panel y manda el link. Las páginas por propiedad generadas (`reservasnueva/<slug>/`) están en `.gitignore`: si quedan carpetas viejas en el disco, al probar local se sirven ésas y no `_ficha.html` (borrarlas con `git clean -Xdf reservasnueva/`).
- **Reserva online (11-nov, backend v2.741):** "Reservar" abre un formulario (nombre, email, teléfono, aceptar la política) → `POST /web/reservar` → link de pago de PHPunta Payments (dLocal) por la seña, sin recargo extra. No bloquea Avantio: el equipo confirma al ver el pago. Política de cancelación en una sección propia de la ficha y, por estadía con fechas exactas, en la caja de precio y en el formulario. Propiedades inactivas = vitrina (sin precio, sin calendario, solo WhatsApp; no aparecen al buscar con fechas). Pendiente fase 2: bloqueo automático en Avantio y alta en nuestras apps.
- Probar local: `python3 -m http.server` en la raíz y abrir `/reservasnueva/?api=http://localhost:<puerto>` (el `?api=` solo se acepta en localhost).
- **Ficha (11-nov, v2):** descripción y comodidades del anuncio de Airbnb (backend v2.740), camas por dormitorio, puntaje y
  reseñas, calendario SIN precios por día (pedido de Felipe) con la nota "actualizados en tiempo real", total por N noches sin
  desglose ("incluye la tarifa de limpieza"; con descuento, el precio sin descuento tachado en rojo y el descuento en negativo),
  "en otras plataformas te hubiera costado hasta USD X" (factor de Airbnb, sin nombrar plataforma ni %), Compartir (con o sin
  fechas), "Hacé preguntas sobre este alojamiento" (IA) y mapa con los lugares de la guía por categoría.
- **Selecciones:** con la sesión del equipo (la misma de Comunicaciones o el Portal: mismo dominio; si no, `?equipo=1` o
  "Acceso equipo" en el pie) aparece "Armar selección": círculos en las tarjetas y "Crear link" → `?sel=<id>` muestra solo
  esas propiedades con las fechas y precios elegidos. Funciona solo en `phpunta.uy` (sin www: localStorage es por origen).
- El calendario del buscador va por encima de la barra de filtros (`body.pop-on .hero`): el `.hero` tiene `isolation`.
- Logo del menú: `assets/img/logo.webp` (11-nov, copiado de reservas.phpunta.uy). Los links del menú "Reservas" ya van a /reservas (11-nov).
