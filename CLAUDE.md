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

## Deploy
Pendiente de definir (ver el hilo de la sesión). Hasta entonces, nada de este repo se publica solo.
