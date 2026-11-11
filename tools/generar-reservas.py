#!/usr/bin/env python3
"""Arma la CENTRAL DE RESERVAS en español, portugués e inglés, con el SEO de cada propiedad, sin intervención manual.

Corre en cada deploy y una vez por día (workflow deploy.yml): una propiedad que se publica en el panel aparece sola,
en los tres idiomas, con su título, descripción, imagen, datos estructurados (JSON-LD), hreflang y entrada en el sitemap.

Plantillas (no se publican: empiezan con _):
  reservas/_lista.html   buscador + lista + mapa
  reservas/_ficha.html   página de una propiedad
Textos de la interfaz en PT/EN: tools/i18n_reservas.py (PARES + traducir()).
Datos: backend /web/seo?lang=xx (una llamada por idioma; textos de las propiedades traducidos y cacheados en el servidor).

Salida (no versionada, ver .gitignore):
  {ES}/index.html, pt/reservas/index.html, en/reservas/index.html
  {ES}/<slug>/index.html, pt/reservas/<slug>/index.html, en/reservas/<slug>/index.html
  sitemap-reservas.xml (solo con la central publicada)
  y, con la central en /reservas, redirecciones en reservasnueva/ para los links viejos.
{ES} = carpeta en español: 'reservas' (publicada) o 'reservasnueva' (oculta). La elige RESERVAS_ES_DIR.

Uso: python3 tools/generar-reservas.py [URL_DEL_BACKEND] [archivo_lista_salida]
Si el backend no responde, genera solo las páginas de lista (sin fichas nuevas) y termina bien."""
import hashlib, html, json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n_reservas as I18N

API = (sys.argv[1] if len(sys.argv) > 1 else 'https://phpunta-backend-production.up.railway.app').rstrip('/')
SALIDA = sys.argv[2] if len(sys.argv) > 2 else None
RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SITIO = 'https://phpunta.uy'
ES_DIR = os.environ.get('RESERVAS_ES_DIR', 'reservasnueva').strip('/') or 'reservasnueva'
PUBLICADA = ES_DIR == 'reservas'   # oculta = noindex, sin sitemap ni links desde el sitio
LANGS = ['es', 'pt', 'en']
DIRS = {'es': ES_DIR, 'pt': 'pt/reservas', 'en': 'en/reservas'}
OG_LOCALE = {'es': 'es_UY', 'pt': 'pt_BR', 'en': 'en_US'}
HREFLANG = {'es': ['es', 'es-uy'], 'pt': ['pt', 'pt-br'], 'en': ['en', 'en-us']}
IMG_DEF = SITIO + '/assets/img/home-hero-loop.jpg'

TX = {
  'es': {
    'lista_tit': 'Alquiler de casas y apartamentos en Punta del Este | Reservas Premium Host Punta',
    'lista_desc': 'Casas y apartamentos premium para alquilar en Punta del Este, La Barra, Manantiales, José Ignacio y Montevideo. Reservá directo con Premium Host Punta: disponibilidad y precio real al instante, sin comisiones de plataformas.',
    'lista_h1': 'Alquileres en Punta del Este',
    'tipo': {'casa': 'Casa', 'apartamento': 'Apartamento'},
    'en': 'en', 'dorm': ('dormitorio', 'dormitorios'), 'banos': ('baño', 'baños'), 'hues': 'hasta {n} huéspedes',
    'tit_sufijo': ' | Alquiler en {barrio}',
    'cola': 'Reservá directo con Premium Host Punta: precio final y disponibilidad al instante.',
    'retirada_tit': 'Propiedad no disponible', 'retirada_desc': 'Esta propiedad ya no está disponible.',
    'inicio': 'Inicio', 'reservas': 'Reservas', 'comodidades': 'Comodidades', 'cargando': 'Cargando…',
    'ver': 'Ver propiedades',
  },
  'pt': {
    'lista_tit': 'Aluguel de casas e apartamentos em Punta del Este | Reservas Premium Host Punta',
    'lista_desc': 'Casas e apartamentos premium para alugar em Punta del Este, La Barra, Manantiales, José Ignacio e Montevidéu. Reserve direto com a Premium Host Punta: disponibilidade e preço real na hora, sem taxas de plataformas.',
    'lista_h1': 'Aluguéis em Punta del Este',
    'tipo': {'casa': 'Casa', 'apartamento': 'Apartamento'},
    'en': 'em', 'dorm': ('quarto', 'quartos'), 'banos': ('banheiro', 'banheiros'), 'hues': 'até {n} hóspedes',
    'tit_sufijo': ' | Aluguel em {barrio}',
    'cola': 'Reserve direto com a Premium Host Punta: preço final e disponibilidade na hora.',
    'retirada_tit': 'Propriedade indisponível', 'retirada_desc': 'Esta propriedade não está mais disponível.',
    'inicio': 'Início', 'reservas': 'Reservas', 'comodidades': 'Comodidades', 'cargando': 'Carregando…',
    'ver': 'Ver propriedades',
  },
  'en': {
    'lista_tit': 'Punta del Este vacation rentals: houses and apartments | Premium Host Punta',
    'lista_desc': 'Premium houses and apartments for rent in Punta del Este, La Barra, Manantiales, José Ignacio and Montevideo. Book direct with Premium Host Punta: real availability and final price instantly, no platform fees.',
    'lista_h1': 'Vacation rentals in Punta del Este',
    'tipo': {'casa': 'House', 'apartamento': 'Apartment'},
    'en': 'in', 'dorm': ('bedroom', 'bedrooms'), 'banos': ('bathroom', 'bathrooms'), 'hues': 'up to {n} guests',
    'tit_sufijo': ' | Rental in {barrio}',
    'cola': 'Book direct with Premium Host Punta: final price and availability instantly.',
    'retirada_tit': 'Property not available', 'retirada_desc': 'This property is no longer available.',
    'inicio': 'Home', 'reservas': 'Book', 'comodidades': 'Amenities', 'cargando': 'Loading…',
    'ver': 'See properties',
  },
}
INICIO = {'es': SITIO + '/', 'pt': SITIO + '/pt/', 'en': SITIO + '/en/'}

hechas = []
manifest = {}


def leer(path):
  req = urllib.request.Request(API + path, headers={'Accept': 'application/json', 'User-Agent': 'phpunta-web-deploy'})
  with urllib.request.urlopen(req, timeout=120) as r:
    return json.loads(r.read().decode('utf-8'))


def esc(s):
  return html.escape(str(s or ''), quote=True)


def url_lista(lang):
  return SITIO + '/' + DIRS[lang] + '/'


def url_ficha(lang, slug):
  return url_lista(lang) + slug + '/'


def escribir(rel, contenido):
  ruta = os.path.join(RAIZ, rel)
  os.makedirs(os.path.dirname(ruta), exist_ok=True)
  open(ruta, 'w', encoding='utf-8').write(contenido)
  hechas.append(rel)
  manifest[rel] = hashlib.sha1(contenido.encode('utf-8')).hexdigest()


def head_seo(lang, titulo, desc, url, imagen, alt_urls, tipo_og='website', jsonld=None):
  """Bloque de SEO para el <head> (reemplaza al marcador <!--SEO--> de la plantilla)."""
  h = []
  h.append('<title>' + esc(titulo) + '</title>')
  h.append('<meta name="description" content="' + esc(desc) + '" />')
  h.append('<meta name="robots" content="' + ('index, follow, max-image-preview:large, max-snippet:-1' if PUBLICADA else 'noindex, nofollow') + '" />')
  h.append('<link rel="canonical" href="' + esc(url) + '" />')
  for lg in LANGS:
    for code in HREFLANG[lg]:
      h.append('<link rel="alternate" hreflang="' + code + '" href="' + esc(alt_urls[lg]) + '" />')
  h.append('<link rel="alternate" hreflang="x-default" href="' + esc(alt_urls['es']) + '" />')
  for lg in LANGS:
    h.append('<meta name="php-alt-' + lg + '" content="' + esc(alt_urls[lg].replace(SITIO, '')) + '" />')
  h.append('<meta property="og:type" content="' + tipo_og + '" />')
  h.append('<meta property="og:site_name" content="Premium Host Punta" />')
  h.append('<meta property="og:locale" content="' + OG_LOCALE[lang] + '" />')
  for lg in LANGS:
    if lg != lang: h.append('<meta property="og:locale:alternate" content="' + OG_LOCALE[lg] + '" />')
  h.append('<meta property="og:title" content="' + esc(titulo) + '" />')
  h.append('<meta property="og:description" content="' + esc(desc) + '" />')
  h.append('<meta property="og:url" content="' + esc(url) + '" />')
  h.append('<meta property="og:image" content="' + esc(imagen) + '" />')
  h.append('<meta name="twitter:card" content="summary_large_image" />')
  h.append('<meta name="twitter:title" content="' + esc(titulo) + '" />')
  h.append('<meta name="twitter:description" content="' + esc(desc) + '" />')
  h.append('<meta name="twitter:image" content="' + esc(imagen) + '" />')
  for j in (jsonld or []):
    h.append('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False).replace('</', '<\\/') + '</script>')
  return '\n'.join(h)


def armar(tpl, lang, base_path, seo, cuerpo_pre=None, slug='', estado=''):
  out = I18N.traducir(tpl, lang)
  out = re.sub(r'<html lang="[a-z-]+"', '<html lang="' + lang + '"', out, count=1)
  out = out.replace('<meta name="php-base" content="/reservasnueva/" />', '<meta name="php-base" content="' + base_path + '" />')
  # Lo que la plantilla trae de SEO (título, description, robots, og) lo reemplaza el bloque nuevo.
  a, b = out.find('<!--SEO-->'), out.find('<!--/SEO-->')
  if a < 0 or b < 0:
    raise SystemExit('La plantilla no tiene los marcadores <!--SEO--> … <!--/SEO-->')
  out = out[:a] + seo + out[b + len('<!--/SEO-->'):]
  out = out.replace('__SLUG__', esc(slug)).replace('__ESTADO__', esc(estado))
  if cuerpo_pre is not None:
    out = out.replace('<!--PRE-->', cuerpo_pre)
  # Las rutas fijas a la carpeta vieja que hayan quedado en la plantilla.
  out = out.replace('/reservasnueva/', base_path)
  return out


def descripcion(lang, p):
  t = TX[lang]
  tipo = t['tipo'].get(p.get('tipo') or 'apartamento', t['tipo']['apartamento'])
  partes = [tipo + ' ' + t['en'] + ' ' + (p.get('barrio') or 'Punta del Este')]
  if p.get('dormitorios'): partes.append('%s %s' % (p['dormitorios'], t['dorm'][0 if p['dormitorios'] == 1 else 1]))
  if p.get('huespedes'): partes.append(t['hues'].format(n=p['huespedes']))
  base = ', '.join(partes) + '. '
  extra = re.sub(r'\s+', ' ', str(p.get('resumen') or '')).strip()
  d = base + (extra + ' ' if extra else '') + t['cola']
  if len(d) > 300:
    d = base + (extra[:300 - len(base) - len(t['cola']) - 3].rsplit(' ', 1)[0] + '… ' if extra else '') + t['cola']
  return d[:320]


def jsonld_ficha(lang, p, url, desc):
  fotos = [f for f in (p.get('fotos') or []) if isinstance(f, str) and f.startswith('https://')][:8]
  ld = {'@context': 'https://schema.org', '@type': 'VacationRental', 'name': p.get('titulo'), 'url': url, 'description': desc,
        'inLanguage': lang, 'identifier': p.get('slug'),
        'brand': {'@type': 'Organization', 'name': 'Premium Host Punta', 'url': SITIO + '/'},
        'address': {'@type': 'PostalAddress', 'addressLocality': p.get('barrio') or 'Punta del Este', 'addressRegion': 'Maldonado', 'addressCountry': 'UY'}}
  if fotos: ld['image'] = fotos
  c = p.get('coord') or {}
  if isinstance(c.get('lat'), (int, float)) and isinstance(c.get('lng'), (int, float)):
    ld['latitude'] = round(c['lat'], 3); ld['longitude'] = round(c['lng'], 3)
  acc = {'@type': 'Accommodation', 'additionalType': 'House' if p.get('tipo') == 'casa' else 'Apartment'}
  if p.get('huespedes'): acc['occupancy'] = {'@type': 'QuantitativeValue', 'maxValue': p['huespedes']}
  if p.get('dormitorios'): acc['numberOfBedrooms'] = p['dormitorios']
  if p.get('banos'): acc['numberOfBathroomsTotal'] = p['banos']
  am = [a for a in (p.get('amenities') or []) if isinstance(a, str)][:25]
  if am: acc['amenityFeature'] = [{'@type': 'LocationFeatureSpecification', 'name': a, 'value': True} for a in am]
  ld['containsPlace'] = acc
  if p.get('checkin'): ld['checkinTime'] = p['checkin']
  if p.get('checkout'): ld['checkoutTime'] = p['checkout']
  bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': 1, 'name': TX[lang]['inicio'], 'item': INICIO[lang]},
    {'@type': 'ListItem', 'position': 2, 'name': TX[lang]['reservas'], 'item': url_lista(lang)},
    {'@type': 'ListItem', 'position': 3, 'name': p.get('titulo'), 'item': url}]}
  return [ld, bc]


def pre_ficha(lang, p, desc):
  """Contenido visible para buscadores dentro de la página (la app lo reemplaza al cargar)."""
  t = TX[lang]
  am = [a for a in (p.get('amenities') or []) if isinstance(a, str)][:20]
  foto = (p.get('fotos') or [None])[0]
  return ('<div class="seo-pre"><h1 style="font-weight:300">' + esc(p.get('titulo')) + '</h1>'
          + ('<img src="' + esc(foto) + '" alt="' + esc(p.get('titulo')) + '" width="600" style="max-width:100%;height:auto;margin:14px 0" />' if foto else '')
          + '<p style="margin-top:10px">' + esc(desc) + '</p>'
          + ('<h2 style="font-size:1.2rem;margin-top:14px">' + t['comodidades'] + '</h2><ul>' + ''.join('<li>' + esc(a) + '</li>' for a in am) + '</ul>' if am else '')
          + '<p style="margin-top:10px">' + t['cargando'] + '</p></div>')


def pre_lista(lang, props):
  t = TX[lang]
  items = ''.join('<li><a href="' + esc(url_ficha(lang, p['slug'])) + '">' + esc(p.get('titulo')) + '</a> — ' + esc(t['tipo'].get(p.get('tipo') or 'apartamento', '')) + ', ' + esc(p.get('barrio') or '') + '</li>' for p in props)
  return '<div class="seo-pre" id="seoPre"><h1 style="font-weight:300;font-size:1.6rem">' + esc(t['lista_h1']) + '</h1><ul>' + items + '</ul></div>'


def main():
  tpl_lista = open(os.path.join(RAIZ, 'reservas', '_lista.html'), encoding='utf-8').read()
  tpl_ficha = open(os.path.join(RAIZ, 'reservas', '_ficha.html'), encoding='utf-8').read()
  datos = {}
  for lang in LANGS:
    try:
      d = leer('/web/seo?lang=' + lang)
      if d.get('ok'): datos[lang] = d
    except Exception as e:
      print('No se pudo leer /web/seo?lang=%s (%s)' % (lang, e))
  props_es = (datos.get('es') or {}).get('publicadas') or []
  sitemap = []
  hoy = __import__('datetime').date.today().isoformat()
  for lang in LANGS:
    t = TX[lang]
    d = datos.get(lang) or datos.get('es') or {}
    props = d.get('publicadas') or []
    base_path = '/' + DIRS[lang] + '/'
    alt = {lg: url_lista(lg) for lg in LANGS}
    ld_lista = [{'@context': 'https://schema.org', '@type': 'ItemList', 'name': t['lista_h1'], 'url': url_lista(lang),
                 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': url_ficha(lang, p['slug']), 'name': p.get('titulo')} for i, p in enumerate(props)]}]
    seo = head_seo(lang, t['lista_tit'], t['lista_desc'], url_lista(lang), (props[0].get('fotos') or [IMG_DEF])[0] if props else IMG_DEF, alt, 'website', ld_lista)
    escribir(DIRS[lang] + '/index.html', armar(tpl_lista, lang, base_path, seo, pre_lista(lang, props)))
    sitemap.append((url_lista(lang), alt, 'daily', '0.9'))
    for p in props:
      slug = p.get('slug') or ''
      if not re.fullmatch(r'[a-z0-9-]{1,60}', slug): continue
      url = url_ficha(lang, slug)
      desc = descripcion(lang, p)
      titulo = (p.get('titulo') or 'Premium Host Punta') + t['tit_sufijo'].format(barrio=p.get('barrio') or 'Punta del Este')
      alt = {lg: url_ficha(lg, slug) for lg in LANGS}
      seo = head_seo(lang, titulo, desc, url, (p.get('fotos') or [IMG_DEF])[0], alt, 'website', jsonld_ficha(lang, p, url, desc))
      escribir(DIRS[lang] + '/' + slug + '/index.html', armar(tpl_ficha, lang, base_path, seo, pre_ficha(lang, p, desc), slug, 'publicada'))
      sitemap.append((url, alt, 'weekly', '0.8', (p.get('fotos') or [])[:5], p.get('titulo')))
    for slug in (d.get('retiradas') or []):
      if not re.fullmatch(r'[a-z0-9-]{1,60}', slug or ''): continue
      url = url_ficha(lang, slug)
      alt = {lg: url_ficha(lg, slug) for lg in LANGS}
      seo = head_seo(lang, t['retirada_tit'], t['retirada_desc'], url, IMG_DEF, alt).replace('index, follow, max-image-preview:large, max-snippet:-1', 'noindex, follow')
      escribir(DIRS[lang] + '/' + slug + '/index.html', armar(tpl_ficha, lang, base_path, seo, '', slug, 'retirada'))
  # Con la central publicada: los links viejos de /reservasnueva/ llevan a /reservas/ (con fechas, selección, etc.).
  if PUBLICADA:
    def redir(destino):
      return ('<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8" /><meta name="robots" content="noindex, follow" />'
              '<link rel="canonical" href="' + SITIO + destino + '" /><meta http-equiv="refresh" content="0; url=' + destino + '" />'
              '<script>location.replace(' + json.dumps(destino) + ' + location.search + location.hash);</script>'
              '<title>Reservas · Premium Host Punta</title></head><body><a href="' + destino + '">Reservas</a></body></html>')
    escribir('reservasnueva/index.html', redir('/reservas/'))
    for p in props_es:
      if re.fullmatch(r'[a-z0-9-]{1,60}', p.get('slug') or ''):
        escribir('reservasnueva/' + p['slug'] + '/index.html', redir('/reservas/' + p['slug'] + '/'))
    xs = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for it in sitemap:
      loc, alt, freq, pri = it[0], it[1], it[2], it[3]
      xs.append('  <url><loc>' + esc(loc) + '</loc><lastmod>' + hoy + '</lastmod><changefreq>' + freq + '</changefreq><priority>' + pri + '</priority>')
      for lg in LANGS:
        for code in HREFLANG[lg]:
          xs.append('    <xhtml:link rel="alternate" hreflang="' + code + '" href="' + esc(alt[lg]) + '"/>')
      xs.append('    <xhtml:link rel="alternate" hreflang="x-default" href="' + esc(alt['es']) + '"/>')
      if len(it) > 4:
        for f in it[4]:
          xs.append('    <image:image><image:loc>' + esc(f) + '</image:loc><image:title>' + esc(it[5]) + '</image:title></image:image>')
      xs.append('  </url>')
    xs.append('</urlset>')
    escribir('sitemap-reservas.xml', '\n'.join(xs) + '\n')
  # Lo que se generó, con su huella: el deploy sube solo lo que cambió respecto de lo publicado.
  escribir('reservas-manifest.json', json.dumps(manifest, sort_keys=True))
  print('Páginas generadas: %d (español en /%s/%s)' % (len(hechas), ES_DIR, '' if PUBLICADA else ', oculta'))
  if SALIDA:
    open(SALIDA, 'w').write('\n'.join(hechas) + '\n')


main()
