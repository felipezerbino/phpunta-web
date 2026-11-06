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
- **Push a `main` → `.github/workflows/deploy.yml` → publica en la raíz de phpunta.uy por HTTPS** con el receptor de las apps (`limpiezas/deployer/deploy.php`, app `web`). Secret del repo: `DEPLOY_TOKEN` (= `limpiezas/deployer/deploy_token.txt` del hosting).
- Sube SOLO lo que cambió desde lo publicado (`https://phpunta.uy/web-version.json` guarda el commit). La primera vez la base es el commit de importación. "Subir todo": Actions → Publicar la web → Run workflow → tildar "completo".
- **Nunca borra.** Un archivo eliminado del repo sigue en el hosting: borrarlo a mano.
- El receptor solo acepta en la web: archivos sueltos en la raíz y carpetas `assets/`, `en/`, `pt/`; html/css/js/imágenes/video/sitemap. Nada `.php`, `.htaccess` ni ocultos. Una carpeta nueva fuera de esas tres exige cambiar `deploy.php` (repo phpunta-comunicaciones) y re-subirlo a mano.
- Lotes de ≤1,5 MB: el tope de subida del PHP del hosting no está medido. Un archivo más grande (los videos de 6-7 MB) puede ser rechazado: el workflow lo dice y hay que subirlo por el Administrador de archivos.
- Verificación: el último paso compara `web-version.json` publicado con el commit.
