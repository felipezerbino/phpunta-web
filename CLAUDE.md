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
- **Push a `main` → `.github/workflows/deploy.yml` → publica en la raíz de phpunta.uy por HTTPS** con un receptor PROPIO en `phpunta.uy/deployer/deploy.php` (app `web`; mismo código que el de las apps, que sigue en `limpiezas/deployer/` sin tocar). Secret del repo: `DEPLOY_TOKEN` (= `deployer/deploy_token.txt` de la raíz).
- Sube SOLO lo que cambió desde lo publicado (`https://phpunta.uy/web-version.json` guarda el commit). La primera vez la base es el commit de importación. "Subir todo": Actions → Publicar la web → Run workflow → tildar "completo".
- **Nunca borra.** Un archivo eliminado del repo sigue en el hosting: borrarlo a mano.
- El receptor solo acepta en la web: archivos sueltos en la raíz y carpetas `assets/`, `en/`, `pt/`; html/css/js/imágenes/video/sitemap. Nada `.php`, `.htaccess` ni ocultos. Una carpeta nueva fuera de esas tres exige cambiar `deploy.php` (repo phpunta-comunicaciones) y re-subirlo a mano a `deployer/` de la raíz.
- Lotes de ≤1,5 MB: el tope de subida del PHP del hosting no está medido. Un archivo más grande (los videos de 6-7 MB) puede ser rechazado: el workflow lo dice y hay que subirlo por el Administrador de archivos.
- Verificación: el último paso compara `web-version.json` publicado con el commit.

## Central de reservas (`reservasnueva/`, OCULTA — fase 1 vitrina, 11-nov-2026)
Reemplaza al sitio de reservas de Avantio (reservas.phpunta.uy). Oculta: `noindex`, fuera del sitemap y sin links desde la web; se publica cuando Felipe la apruebe (ahí: sacar noindex, canonical, sitemap, links del menú y decidir la URL final — `alquileres/` ya está habilitada en el receptor).
- `reservasnueva/index.html`: buscador (fechas, huéspedes, zona), filtros que sirven (tipo, dormitorios, piscina, frente al mar, playa, parrillero, jacuzzi, orden), lista con scroll continuo y mapa (Leaflet + CARTO) con "Buscar en esta zona" / "Buscar al mover el mapa". El estado vive en la URL (se puede compartir).
- `reservasnueva/_ficha.html`: PLANTILLA de la página de cada propiedad. El deploy corre `tools/generar-fichas.py`, que lee `/web/slugs` del backend y escribe `reservasnueva/<slug>/index.html` (no se versionan: `.gitignore`). Los archivos que empiezan con `_` no se publican. El workflow corre también una vez por día (propiedades nuevas, títulos nuevos). Una propiedad que deja de publicarse conserva su página con "ya no está disponible" (el receptor nunca borra).
- Datos: backend `/web/*` (v2.738): catálogo, ficha, calendario, cotización, búsqueda. El slug (URL) no cambia una vez creado. Títulos = los de Airbnb sin "PHPunta" con el nombre del edificio adelante; precios = total directo (tabla de Avantio con descuentos + limpieza REAL) × (1 + recargo). Config en `app_config.web_reservas` (`recargo_pct`, `sena_pct`, `whatsapp_reservas`).
- Fase 1 NO cobra: "Reservar" abre WhatsApp de Reservas con fechas, huéspedes y total. Fase 2: pago (seña 50% al reservar, 50% + garantía al llegar), bloqueo en Avantio y alta en nuestras apps.
- Probar local: `python3 -m http.server` en la raíz y abrir `/reservasnueva/?api=http://localhost:<puerto>` (el `?api=` solo se acepta en localhost).
- Pendiente: el logo del menú todavía se carga desde reservas.phpunta.uy (Avantio): copiarlo a `assets/` antes de dar de baja ese sitio — lo usan TODAS las páginas.
