#!/usr/bin/env python3
# Arma la GUÍA DE PUNTA DEL ESTE (ES / PT / EN): portada, zonas, temporada y preguntas frecuentes.
# Usa como molde la página legal de cada idioma (mismo encabezado, menú, pie y estilos base) y los textos de
# tools/guia_contenido.py. Los botones "Ver propiedades en <zona>" salen solo para las zonas que hoy tienen propiedades
# en la central de reservas (se lee el catálogo del backend); las demás ofrecen escribir por WhatsApp.
# Uso (desde la raíz del repo): python3 tools/generar-guia.py [URL_DEL_BACKEND]
# Se commitean las páginas generadas. Volver a correrlo cuando cambian los textos o las zonas con propiedades.
import datetime, html, json, os, re, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from guia_contenido import ACTUALIZADO, T, WA, ZONAS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITIO = 'https://phpunta.uy'
BACKEND = sys.argv[1] if len(sys.argv) > 1 else 'https://phpunta-backend-production.up.railway.app'
PLANTILLA = {'es': 'condiciones-generales.html', 'pt': 'pt/termos.html', 'en': 'en/terms.html'}
HREFLANG = {'es': ['es', 'es-uy'], 'pt': ['pt', 'pt-br'], 'en': ['en', 'en-us']}
PAGINAS = ['hub', 'zonas', 'temporada', 'faq']
IMG = {'hub': 'home-atmosphere-aerea.jpg', 'zonas': 'gal-01-peninsula-aerea.jpg', 'temporada': 'gal-04-playa-brava.jpg',
       'faq': 'gal-14-mansa-atardecer.jpg'}
CARD_IMG = {'zonas': 'gal-07-aerea-barra.jpg', 'temporada': 'gal-04-playa-brava.jpg', 'faq': 'gal-11-puerto-puntaeste.jpg'}
ESC = html.escape


def zonas_con_propiedades():
  try:
    req = urllib.request.Request(BACKEND + '/web/catalogo', headers={'User-Agent': 'phpunta-web-guia'})
    j = json.load(urllib.request.urlopen(req, timeout=40))
    return set(p.get('barrio') for p in j.get('propiedades', []) if p.get('barrio'))
  except Exception as e:
    print('AVISO: no se pudo leer el catálogo (' + str(e) + '): todas las zonas ofrecen WhatsApp')
    return set()


def url(lang, pag):
  return SITIO + '/' + T[lang]['archivos'][pag]


def href(lang, pag):
  return '/' + T[lang]['archivos'][pag]


def fecha_txt(lang, iso):
  d = datetime.date.fromisoformat(iso)
  m = T[lang]['ui']['meses'][d.month - 1]
  return '%s %d, %d' % (m, d.day, d.year) if lang == 'en' else '%d de %s de %d' % (d.day, m, d.year)


def pascua(y):
  a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
  h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
  m = (a + 11 * h + 22 * l) // 451; mes = (h + l - 7 * m + 114) // 31; dia = ((h + l - 7 * m + 114) % 31) + 1
  return datetime.date(y, mes, dia)


def rango(lang, a, b, unido=False):
  u = T[lang]['ui']; M = u['meses']
  sep = (' ' + u['y'] + ' ') if unido else (' ' + u['al'] + ' ')
  if lang == 'en':
    if a.month == b.month:
      return '%s %d%s%d, %d' % (M[a.month - 1], a.day, ' and ' if unido else '–', b.day, b.year)
    return '%s %d – %s %d, %d' % (M[a.month - 1], a.day, M[b.month - 1], b.day, b.year)
  if a.month == b.month:
    return '%d%s%d de %s de %d' % (a.day, sep, b.day, M[a.month - 1], b.year)
  return '%d de %s%s%d de %s de %d' % (a.day, M[a.month - 1], sep, b.day, M[b.month - 1], b.year)


def fechas_clave(lang, hoy):
  # Las dos próximas temporadas altas, con sus Carnavales y Semanas de Turismo.
  u = T[lang]['ui']; out = []
  y0 = hoy.year if hoy < datetime.date(hoy.year, 3, 1) else hoy.year + 1   # año en que TERMINA la próxima temporada alta
  for y in (y0, y0 + 1):
    ini = datetime.date(y - 1, 12, 15); fin = datetime.date(y, 3, 1) - datetime.timedelta(days=1)
    p = pascua(y)
    alta = {'es': 'Temporada alta', 'pt': 'Alta temporada', 'en': 'High season'}[lang]
    out.append((alta + ' ' + str(y - 1) + '–' + str(y), rango(lang, ini, fin)))
    out.append((u['carnaval'] + ' ' + str(y), rango(lang, p - datetime.timedelta(days=48), p - datetime.timedelta(days=47), True)))
    out.append((u['turismo'] + ' ' + str(y), rango(lang, p - datetime.timedelta(days=6), p)))
  return out


CSS = r'''
/* ===== GUÍA DE PUNTA DEL ESTE ===== */
.gp-zcards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
@media (min-width: 700px) { .gp-zcards { grid-template-columns: repeat(3, 1fr); gap: 16px; } }
@media (min-width: 1100px) { .gp-zcards { grid-template-columns: repeat(5, 1fr); } }
.gp-zcard { position: relative; display: block; aspect-ratio: 3 / 4; overflow: hidden; background: var(--navy); color: var(--cream); }
.gp-zcard img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .8s var(--ease); }
.gp-zcard::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(7,19,31,0) 40%, rgba(7,19,31,.85) 100%); }
.gp-zcard:hover img { transform: scale(1.05); }
.gp-zcard-t { position: absolute; left: 0; right: 0; bottom: 0; z-index: 1; padding: 16px 16px 18px; display: flex; flex-direction: column; gap: 4px; }
.gp-zcard-t b { font-family: var(--serif); font-weight: 400; font-size: 1.35rem; line-height: 1.15; color: var(--cream); }
.gp-zcard-t small { font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: var(--gold); line-height: 1.4; }
.gp-sec.alt .gp-ideal span { background: #fff; }
.gp-tabla td:first-child { white-space: nowrap; }
@media (max-width: 699px) { .gp-tabla td:first-child { white-space: normal; } }
.gp { --navy-deep: #07131f; --cream-paper: #ede7d6; }
.gp a { border-bottom: none; }
.gp img { max-width: 100%; display: block; }
.gp-hero { position: relative; min-height: 560px; display: flex; align-items: flex-end; color: var(--cream); overflow: hidden; background: var(--navy); }
.gp-hero > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.gp-hero::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(7,19,31,.35) 0%, rgba(7,19,31,.45) 45%, rgba(7,19,31,.88) 100%); }
.gp-hero .container { position: relative; z-index: 1; width: 100%; padding-top: 120px; padding-bottom: 56px; }
.gp-crumbs { font-size: 11px; letter-spacing: .18em; text-transform: uppercase; color: rgba(240,236,224,.75); margin-bottom: 22px; }
.gp-crumbs a { color: rgba(240,236,224,.85); }
.gp-crumbs a:hover { color: var(--gold); }
.gp-crumbs span { margin: 0 8px; color: var(--gold); }
.gp-eyebrow { font-size: 11px; font-weight: 500; letter-spacing: .28em; text-transform: uppercase; color: var(--gold); display: inline-flex; align-items: center; gap: 14px; }
.gp-eyebrow::before { content: ''; width: 28px; height: 1px; background: currentColor; opacity: .7; }
.gp-hero h1 { font-family: var(--serif); font-weight: 300; font-size: clamp(2.6rem, 6vw, 5.2rem); line-height: 1.04; letter-spacing: -.01em; margin: 18px 0 20px; max-width: 16ch; color: var(--cream); }
.gp-hero h1 em { color: var(--gold); font-style: italic; font-weight: 300; }
.gp-hero .gp-sub { font-size: 1.12rem; line-height: 1.7; max-width: 56ch; color: rgba(240,236,224,.88); }
.gp-meta { display: flex; flex-wrap: wrap; gap: 10px 24px; align-items: center; margin-top: 30px; font-size: 12px; letter-spacing: .08em; color: rgba(240,236,224,.7); }
.gp-langs a { color: rgba(240,236,224,.85); padding: 2px 4px; }
.gp-langs a:hover, .gp-langs b { color: var(--gold); }
.gp-langs b { font-weight: 500; padding: 2px 4px; }
.gp-sec { padding: 72px 0; }
.gp-sec.alt { background: var(--cream-warm); }
.gp-wrap { max-width: 860px; }
.gp-h2 { font-family: var(--serif); font-weight: 400; font-size: clamp(2rem, 3.6vw, 3rem); line-height: 1.1; margin: 14px 0 26px; color: var(--navy); }
.gp-h2 em { color: var(--gold-deep); font-style: italic; font-weight: 300; }
.gp-p { font-size: 1.05rem; line-height: 1.8; color: var(--text-soft); margin-bottom: 18px; }
.gp-resp { margin-top: -44px; position: relative; z-index: 2; }
.gp-resp-box { background: #fff; border: 1px solid var(--border-light); border-left: 3px solid var(--gold); padding: 30px 34px; box-shadow: 0 30px 60px -36px rgba(13,27,42,.35); max-width: 900px; }
.gp-resp-box .gp-eyebrow { color: var(--gold-deep); margin-bottom: 12px; }
.gp-resp-box p { font-family: var(--serif); font-size: clamp(1.25rem, 2vw, 1.5rem); line-height: 1.5; color: var(--navy); font-weight: 400; }
.gp-chips { display: flex; flex-wrap: wrap; gap: 10px; }
.gp-chip { display: inline-flex; align-items: center; gap: 8px; padding: 9px 16px; border: 1px solid var(--border-light); border-radius: 40px; font-size: 13px; color: var(--navy); background: #fff; transition: all .25s var(--ease); }
.gp-chip:hover { border-color: var(--gold); color: var(--gold-deep); }
.gp-cards { display: grid; grid-template-columns: 1fr; gap: 22px; }
@media (min-width: 800px) { .gp-cards { grid-template-columns: repeat(3, 1fr); } }
.gp-card { display: flex; flex-direction: column; background: #fff; border: 1px solid var(--border-light); transition: transform .35s var(--ease), box-shadow .35s var(--ease); color: var(--text); }
.gp-card:hover { transform: translateY(-4px); box-shadow: 0 26px 50px -30px rgba(13,27,42,.4); }
.gp-card img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; }
.gp-card-b { padding: 24px 26px 28px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
.gp-card h3 { font-family: var(--serif); font-weight: 400; font-size: 1.7rem; color: var(--navy); line-height: 1.15; }
.gp-card p { font-size: .95rem; line-height: 1.65; color: var(--text-soft); flex: 1; }
.gp-more { font-size: 11px; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: var(--gold-deep); }
.gp-btns { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; }
.gp-btn { display: inline-flex; align-items: center; gap: 10px; padding: 15px 24px; font-size: 11.5px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; border-radius: 2px; transition: all .3s var(--ease); max-width: 100%; white-space: normal; text-align: left; line-height: 1.35; }
.gp-btn-gold { background: var(--gold); color: var(--navy); }
.gp-btn-gold:hover { background: var(--navy); color: var(--cream); }
.gp-btn-line { border: 1px solid var(--navy); color: var(--navy); }
.gp-btn-line:hover { background: var(--navy); color: var(--cream); }
.gp-btn-light { border: 1px solid rgba(240,236,224,.45); color: var(--cream); }
.gp-btn-light:hover { border-color: var(--cream); background: rgba(240,236,224,.08); }
.gp-zona { display: grid; grid-template-columns: 1fr; gap: 28px; padding: 56px 0; border-top: 1px solid var(--border-light); scroll-margin-top: 90px; }
.gp-zona:first-of-type { border-top: none; }
@media (min-width: 900px) {
  .gp-zona { grid-template-columns: 1fr 1.1fr; gap: 56px; align-items: center; }
  .gp-zona.inv .gp-zona-img { order: 2; }
}
.gp-zona-img img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; }
.gp-zona h2 { font-family: var(--serif); font-weight: 400; font-size: clamp(2rem, 3.4vw, 2.8rem); color: var(--navy); line-height: 1.08; margin: 12px 0 10px; }
.gp-tag { font-family: var(--serif); font-style: italic; font-size: 1.3rem; color: var(--gold-deep); line-height: 1.4; margin-bottom: 18px; }
.gp-dist { font-size: 11px; font-weight: 500; letter-spacing: .2em; text-transform: uppercase; color: var(--text-muted); }
.gp-ideal { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 6px 0 22px; }
.gp-ideal b { font-size: 11px; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: var(--navy); margin-right: 4px; }
.gp-ideal span { font-size: 12.5px; padding: 6px 12px; background: var(--cream-warm); border-radius: 30px; color: var(--navy); }
.gp-tabla { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid var(--border-light); font-size: .95rem; }
.gp-tabla th { text-align: left; font-size: 10.5px; font-weight: 600; letter-spacing: .18em; text-transform: uppercase; color: var(--gold-deep); padding: 16px 18px; border-bottom: 1px solid var(--border-light); background: var(--cream); }
.gp-tabla td { padding: 15px 18px; border-bottom: 1px solid var(--border-light); color: var(--text-soft); vertical-align: top; }
.gp-tabla td:first-child a { font-family: var(--serif); font-size: 1.2rem; color: var(--navy); }
.gp-tabla td:first-child a:hover { color: var(--gold-deep); }
@media (max-width: 699px) {
  .gp-tabla thead { display: none; }
  .gp-tabla, .gp-tabla tbody, .gp-tabla tr, .gp-tabla td { display: block; width: 100%; }
  .gp-tabla tr { border-bottom: 1px solid var(--border-light); padding: 12px 0; }
  .gp-tabla td { border: none; padding: 3px 18px; }
}
.gp-mvd { margin-top: 24px; padding: 30px 32px; background: var(--navy); color: var(--cream); }
.gp-mvd h3 { font-family: var(--serif); font-weight: 400; font-size: 1.8rem; margin-bottom: 10px; color: var(--cream); }
.gp-mvd p { color: rgba(240,236,224,.8); line-height: 1.7; margin-bottom: 18px; }
.gp-tempos { display: grid; grid-template-columns: 1fr; gap: 20px; }
@media (min-width: 900px) { .gp-tempos { grid-template-columns: repeat(3, 1fr); } }
.gp-tempo { padding: 32px 30px; background: #fff; border: 1px solid var(--border-light); }
.gp-tempo.dark { background: var(--navy); color: var(--cream); border-color: var(--navy); }
.gp-tempo .gp-dist { color: var(--gold-deep); }
.gp-tempo.dark .gp-dist { color: var(--gold); }
.gp-tempo h3 { font-family: var(--serif); font-weight: 400; font-size: 1.9rem; margin: 10px 0 14px; color: var(--navy); }
.gp-tempo.dark h3 { color: var(--cream); }
.gp-tempo p { font-size: .97rem; line-height: 1.7; color: var(--text-soft); }
.gp-tempo.dark p { color: rgba(240,236,224,.8); }
.gp-fechas { display: grid; grid-template-columns: 1fr; gap: 0; background: #fff; border: 1px solid var(--border-light); }
@media (min-width: 700px) { .gp-fechas { grid-template-columns: 1fr 1fr; } }
.gp-fecha { display: flex; justify-content: space-between; gap: 16px; padding: 16px 22px; border-bottom: 1px solid var(--border-light); flex-wrap: wrap; }
.gp-fecha span { font-size: .92rem; color: var(--text-soft); }
.gp-fecha b { font-weight: 500; color: var(--navy); }
.gp-list { list-style: none; display: grid; gap: 16px; }
.gp-list li { position: relative; padding-left: 26px; font-size: 1.03rem; line-height: 1.75; color: var(--text-soft); }
.gp-list li::before { content: ''; position: absolute; left: 0; top: .78em; width: 12px; height: 1px; background: var(--gold); }
.gp-faq { border-top: 1px solid var(--border-light); }
.gp-faq details { border-bottom: 1px solid var(--border-light); }
.gp-faq summary { list-style: none; cursor: pointer; padding: 22px 44px 22px 0; position: relative; font-family: var(--serif); font-size: clamp(1.2rem, 1.8vw, 1.45rem); color: var(--navy); line-height: 1.35; }
.gp-faq summary::-webkit-details-marker { display: none; }
.gp-faq summary::after { content: '+'; position: absolute; right: 6px; top: 18px; font-family: var(--sans); font-weight: 300; font-size: 26px; color: var(--gold-deep); transition: transform .3s var(--ease); }
.gp-faq details[open] summary::after { transform: rotate(45deg); }
.gp-faq details p { padding: 0 0 24px; font-size: 1.02rem; line-height: 1.8; color: var(--text-soft); max-width: 72ch; }
.gp-faq-g { font-size: 11px; font-weight: 600; letter-spacing: .22em; text-transform: uppercase; color: var(--gold-deep); margin: 46px 0 8px; }
.gp-faq-g:first-child { margin-top: 0; }
.gp-cta { background: var(--navy); color: var(--cream); padding: 84px 0; text-align: center; }
.gp-cta h2 { font-family: var(--serif); font-weight: 300; font-size: clamp(2.2rem, 4vw, 3.4rem); line-height: 1.1; margin-bottom: 16px; color: var(--cream); }
.gp-cta h2 em { color: var(--gold); font-style: italic; }
.gp-cta p { color: rgba(240,236,224,.78); max-width: 52ch; margin: 0 auto 32px; line-height: 1.7; }
.gp-cta .gp-btns { justify-content: center; }
.gp-upd { font-size: 12px; color: var(--text-muted); margin-top: 28px; letter-spacing: .04em; }
.gp-k { font-size: 11px; font-weight: 600; letter-spacing: .22em; text-transform: uppercase; color: var(--gold-deep); margin-bottom: 18px; }
@media (max-width: 699px) {
  .gp-hero { min-height: 480px; }
  .gp-hero .container { padding-top: 90px; padding-bottom: 72px; }
  .gp-sec { padding: 56px 0; }
  .gp-resp-box { padding: 24px 22px; }
  .gp-btn { width: 100%; justify-content: center; text-align: center; }
}
'''


def crumbs(lang, pag):
  u = T[lang]['ui']
  inicio = '/' if lang == 'es' else '/' + lang + '/'
  h = '<nav class="gp-crumbs" aria-label="breadcrumb"><a href="' + inicio + '">' + u['inicio'] + '</a><span>/</span>'
  if pag == 'hub':
    h += u['guia']
  else:
    h += '<a href="' + href(lang, 'hub') + '">' + u['guia'] + '</a><span>/</span>' + ESC(titulo_corto(lang, pag))
  return h + '</nav>'


def titulo_corto(lang, pag):
  if pag == 'hub':
    return T[lang]['ui']['guia']
  for k, t, _ in T[lang]['paginas']['hub']['cards']:
    if k == pag:
      return t
  return ''


def langs(lang, pag):
  out = []
  for lg in ('es', 'pt', 'en'):
    if lg == lang:
      out.append('<b>' + lg.upper() + '</b>')
    else:
      out.append('<a href="' + href(lg, pag) + '" hreflang="' + lg + '">' + lg.upper() + '</a>')
  return '<span class="gp-langs">' + ' · '.join(out) + '</span>'


def hero(lang, pag):
  d = T[lang]['paginas'][pag]; u = T[lang]['ui']
  return ('<section class="gp-hero"><img src="/assets/img/' + IMG[pag] + '" alt="" fetchpriority="high" decoding="async" />'
          '<div class="container">' + crumbs(lang, pag) + '<span class="gp-eyebrow">' + u['eyebrow'] + '</span>'
          '<h1>' + d['h1'] + '</h1><p class="gp-sub">' + ESC(d['sub']) + '</p>'
          '<div class="gp-meta"><span>' + u['actualizado'] + ' ' + fecha_txt(lang, ACTUALIZADO) + '</span>' + langs(lang, pag) + '</div>'
          '</div></section>')


def respuesta(lang, pag):
  d = T[lang]['paginas'][pag]
  return ('<section class="gp-resp"><div class="container"><div class="gp-resp-box"><span class="gp-eyebrow">' + T[lang]['ui']['respuesta'] +
          '</span><p>' + ESC(d['resp']) + '</p></div></div></section>')


def faq_html(items):
  h = ['<div class="gp-faq">']
  for i, (q, a) in enumerate(items):
    h.append('<details' + (' open' if i == 0 else '') + '><summary>' + ESC(q) + '</summary><p>' + ESC(a) + '</p></details>')
  h.append('</div>')
  return ''.join(h)


def faq_sec(lang, items, alt=True):
  u = T[lang]['ui']
  return ('<section class="gp-sec' + (' alt' if alt else '') + '"><div class="container gp-wrap"><span class="gp-eyebrow">' + u['faq_t'] + '</span>'
          '<h2 class="gp-h2">' + u['faq_t'] + '</h2>' + faq_html(items) + '</div></section>')


def cta(lang):
  u = T[lang]['ui']
  return ('<section class="gp-cta"><div class="container"><h2>' + u['cta_t'] + '</h2><p>' + ESC(u['cta_p']) + '</p><div class="gp-btns">'
          '<a class="gp-btn gp-btn-gold" href="' + T[lang]['reservas'] + '">' + u['cta_res'] + ' →</a>'
          '<a class="gp-btn gp-btn-light" href="' + WA + '" target="_blank" rel="noopener">' + u['cta_wa'] + '</a></div></div></section>')


def cards(lang, excluir=None):
  h = ['<div class="gp-cards">']
  for k, t, p in T[lang]['paginas']['hub']['cards']:
    if k == excluir:
      continue
    h.append('<a class="gp-card" href="' + href(lang, k) + '"><img src="/assets/img/guia/' + CARD_IMG[k].replace('.jpg', '-900.jpg') + '" alt="" loading="lazy" decoding="async" />'
             '<div class="gp-card-b"><h3>' + ESC(t) + '</h3><p>' + ESC(p) + '</p><span class="gp-more">' + T[lang]['ui']['leer'] + ' →</span></div></a>')
  h.append('</div>')
  return ''.join(h)


def seguir(lang, pag):
  u = T[lang]['ui']
  return ('<section class="gp-sec"><div class="container"><span class="gp-eyebrow">' + u['seguir'] + '</span><h2 class="gp-h2">' +
          u['guia'] + '</h2>' + cards(lang, pag) + '</div></section>')


def boton_zona(lang, k, con_props):
  u = T[lang]['ui']; z = T[lang]['zonas'][k]
  if k in con_props:
    return '<a class="gp-btn gp-btn-gold" href="' + T[lang]['reservas'] + '?zona=' + k + '">' + u['ver_en'] + ' ' + ESC(z['n'].replace('The ', 'the ').replace('A Península', 'Península').replace('La Península', 'la Península')) + ' →</a>'
  msg = urllib.parse.quote(u['consultar_msg'] + z['n'])
  return '<a class="gp-btn gp-btn-line" href="' + WA + '&text=' + msg + '" target="_blank" rel="noopener">' + u['consultar'] + '</a>'


def dist_txt(lang, z):
  u = T[lang]['ui']
  if z['km'] is None:
    return u['pegada']
  return '%d km · %d min %s %s' % (z['km'], z['min'], u['en_auto'], u['desde_pen'])


def cuerpo(lang, pag, con_props):
  d = T[lang]['paginas'][pag]; u = T[lang]['ui']
  h = ['<main class="gp">', hero(lang, pag), respuesta(lang, pag)]
  if pag == 'hub':
    h.append('<section class="gp-sec"><div class="container"><span class="gp-eyebrow">' + ESC(d['guias_t']) + '</span><h2 class="gp-h2">' +
             ESC(d['guias_t']) + '</h2>' + cards(lang) + '</div></section>')
    h.append('<section class="gp-sec alt"><div class="container"><span class="gp-eyebrow">' + ESC(d['zonas_t']) + '</span><h2 class="gp-h2">' +
             ESC(d['zonas_t']) + '</h2><div class="gp-zcards">')
    for z in ZONAS:
      t = T[lang]['zonas'][z['k']]
      h.append('<a class="gp-zcard" href="' + href(lang, 'zonas') + '#zona-' + z['k'] + '"><img src="/assets/img/guia/' + z['img'].replace('.jpg', '-900.jpg') + '" alt="" loading="lazy" decoding="async" />'
               '<span class="gp-zcard-t"><b>' + ESC(t['n']) + '</b><small>' + ESC(dist_txt(lang, z)) + '</small></span></a>')
    h.append('</div></div></section>')
    h.append(faq_sec(lang, d['faq'], alt=False))
  elif pag == 'zonas':
    h.append('<section class="gp-sec"><div class="container"><span class="gp-eyebrow">' + ESC(d['tabla_t']) + '</span><h2 class="gp-h2">' + ESC(d['tabla_t']) +
             '</h2><table class="gp-tabla"><thead><tr><th>' + u['tabla_z'] + '</th><th>' + u['tabla_a'] + '</th><th>' + u['ideal'] + '</th><th>' + u['tabla_d'] +
             '</th></tr></thead><tbody>')
    for z in ZONAS:
      t = T[lang]['zonas'][z['k']]
      h.append('<tr><td><a href="#zona-' + z['k'] + '">' + ESC(t['n']) + '</a></td><td>' + ESC(t['amb']) + '</td><td>' + ESC(', '.join(t['ideal'])) +
               '</td><td>' + ESC(dist_txt(lang, z)) + '</td></tr>')
    h.append('</tbody></table></div></section>')
    h.append('<section class="gp-sec alt" style="padding-top:56px"><div class="container"><span class="gp-eyebrow">' + ESC(d['det_t']) + '</span>')
    for i, z in enumerate(ZONAS):
      t = T[lang]['zonas'][z['k']]
      h.append('<article class="gp-zona' + (' inv' if i % 2 else '') + '" id="zona-' + z['k'] + '"><div class="gp-zona-img"><img src="/assets/img/guia/' + z['img'].replace('.jpg', '-900.jpg') +
               '" alt="' + ESC(t['n']) + '" loading="lazy" decoding="async" /></div><div>'
               '<span class="gp-dist">' + ESC(dist_txt(lang, z)) + '</span><h2>' + ESC(t['n']) + '</h2><p class="gp-tag">' + ESC(t['tag']) + '</p>' +
               ''.join('<p class="gp-p">' + ESC(p) + '</p>' for p in t['p']) +
               '<div class="gp-ideal"><b>' + u['ideal'] + '</b>' + ''.join('<span>' + ESC(x) + '</span>' for x in t['ideal']) + '</div>'
               '<div class="gp-btns">' + boton_zona(lang, z['k'], con_props) + '</div></div></article>')
    mvd_btn = ('<a class="gp-btn gp-btn-gold" href="' + T[lang]['reservas'] + '?zona=montevideo">' + u['ver_en'] + ' Montevideo →</a>') if 'montevideo' in con_props else \
              ('<a class="gp-btn gp-btn-light" href="' + WA + '" target="_blank" rel="noopener">' + u['cta_wa'] + '</a>')
    h.append('<div class="gp-mvd"><h3>' + ESC(d['mvd_t']) + '</h3><p>' + ESC(d['mvd_p']) + '</p><div class="gp-btns">' + mvd_btn + '</div></div>')
    h.append('</div></section>')
    h.append(faq_sec(lang, d['faq'], alt=False))
    h.append(seguir(lang, pag))
  elif pag == 'temporada':
    h.append('<section class="gp-sec"><div class="container"><div class="gp-tempos">')
    for i, (t, cuando, p) in enumerate(d['tempos']):
      h.append('<div class="gp-tempo' + (' dark' if i == 0 else '') + '"><span class="gp-dist">' + ESC(cuando) + '</span><h3>' + ESC(t) + '</h3><p>' + ESC(p) + '</p></div>')
    h.append('</div></div></section>')
    h.append('<section class="gp-sec alt"><div class="container gp-wrap"><span class="gp-eyebrow">' + u['fechas_t'] + '</span><h2 class="gp-h2">' + u['fechas_t'] +
             '</h2><div class="gp-fechas">')
    for n, f in fechas_clave(lang, datetime.date.today()):
      h.append('<div class="gp-fecha"><b>' + ESC(n) + '</b><span>' + ESC(f) + '</span></div>')
    h.append('</div></div></section>')
    for i, (t, ps) in enumerate(d['secs']):
      h.append('<section class="gp-sec' + (' alt' if i % 2 else '') + '"><div class="container gp-wrap"><h2 class="gp-h2">' + ESC(t) + '</h2>' +
               ('<ul class="gp-list">' + ''.join('<li>' + ESC(p) + '</li>' for p in ps) + '</ul>' if len(ps) > 1 else '<p class="gp-p">' + ESC(ps[0]) + '</p>') +
               ('<div class="gp-btns" style="margin-top:18px"><a class="gp-btn gp-btn-gold" href="' + WA + '" target="_blank" rel="noopener">' + u['cta_wa'] + '</a></div>' if i == len(d['secs']) - 1 else '') +
               '</div></section>')
    h.append(faq_sec(lang, d['faq'], alt=len(d['secs']) % 2 == 1))
    h.append(seguir(lang, pag))
  elif pag == 'faq':
    h.append('<section class="gp-sec"><div class="container gp-wrap">')
    for g, items in d['grupos']:
      h.append('<h2 class="gp-faq-g">' + ESC(g) + '</h2>' + faq_html(items))
    h.append('</div></section>')
    h.append(seguir(lang, pag))
  h.append(cta(lang))
  h.append('</main>\n\n')
  return '\n'.join(h)


def jsonld(lang, pag):
  d = T[lang]['paginas'][pag]; u = T[lang]['ui']
  inicio = SITIO + ('/' if lang == 'es' else '/' + lang + '/')
  bc = [{'@type': 'ListItem', 'position': 1, 'name': u['inicio'], 'item': inicio},
        {'@type': 'ListItem', 'position': 2, 'name': u['guia'], 'item': url(lang, 'hub')}]
  if pag != 'hub':
    bc.append({'@type': 'ListItem', 'position': 3, 'name': titulo_corto(lang, pag), 'item': url(lang, pag)})
  org = {'@type': 'Organization', 'name': 'Premium Host Punta', 'url': SITIO + '/', 'logo': SITIO + '/assets/img/logo-premium-host-punta.jpg'}
  grafo = [{'@type': 'BreadcrumbList', 'itemListElement': bc},
           {'@type': 'Article', 'headline': re.sub(r'<[^>]+>', '', d['h1']).strip(), 'description': d['desc'], 'inLanguage': T[lang]['inlang'],
            'image': SITIO + '/assets/img/' + IMG[pag], 'datePublished': '2026-11-17', 'dateModified': ACTUALIZADO,
            'author': dict(org, name=u['autor']), 'publisher': org, 'mainEntityOfPage': url(lang, pag),
            'about': {'@type': 'TouristDestination', 'name': 'Punta del Este', 'address': {'@type': 'PostalAddress', 'addressRegion': 'Maldonado', 'addressCountry': 'UY'}}}]
  if pag == 'faq':
    items = [x for _, g in d['grupos'] for x in g]
  else:
    items = d.get('faq', [])
  if items:
    grafo.append({'@type': 'FAQPage', 'inLanguage': T[lang]['inlang'], 'mainEntity': [
      {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]})
  if pag == 'zonas':
    grafo.append({'@type': 'ItemList', 'name': d['tabla_t'], 'itemListElement': [
      {'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'Place', 'name': T[lang]['zonas'][z['k']]['n'],
       'description': T[lang]['zonas'][z['k']]['tag'], 'url': url(lang, 'zonas') + '#zona-' + z['k']}} for i, z in enumerate(ZONAS)]})
  return '<script type="application/ld+json">\n' + json.dumps({'@context': 'https://schema.org', '@graph': grafo}, ensure_ascii=False, indent=1) + '\n</script>'


def armar(lang, pag, con_props):
  d = T[lang]['paginas'][pag]
  s = open(os.path.join(RAIZ, PLANTILLA[lang]), encoding='utf-8').read()
  u = url(lang, pag)
  titulo = d['title']; desc = d['desc']; img = SITIO + '/assets/img/' + IMG[pag]
  s = re.sub(r'<title>[^<]*</title>', lambda m: '<title>' + ESC(titulo) + '</title>', s, count=1)
  s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + ESC(desc), s, count=1)
  s = re.sub(r'\s*<meta name="keywords"[^>]*>', '', s, count=1)
  s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + u, s, count=1)
  for prop in ('og:title', 'twitter:title', 'og:image:alt', 'twitter:image:alt'):
    s = re.sub(r'(<meta (?:property|name)="' + prop + r'" content=")[^"]*', lambda m: m.group(1) + ESC(titulo), s)
  for prop in ('og:description', 'twitter:description'):
    s = re.sub(r'(<meta (?:property|name)="' + prop + r'" content=")[^"]*', lambda m: m.group(1) + ESC(desc), s)
  s = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + u, s)
  for prop in ('og:image', 'og:image:secure_url'):
    s = re.sub(r'(<meta property="' + prop + r'" content=")[^"]*', lambda m: m.group(1) + img, s)
  s = re.sub(r'(<meta name="twitter:image" content=")[^"]*', lambda m: m.group(1) + img, s)
  s = re.sub(r'\s*<meta property="og:image:(width|height)"[^>]*>', '', s)
  alts = []
  for lg in ('es', 'pt', 'en'):
    for code in HREFLANG[lg]:
      alts.append('<link rel="alternate" hreflang="' + code + '" href="' + url(lg, pag) + '" />')
  alts.append('<link rel="alternate" hreflang="x-default" href="' + url('es', pag) + '" />')
  lineas = s.split('\n')
  idx = [i for i, l in enumerate(lineas) if 'hreflang=' in l and '<link' in l]
  if idx:
    lineas[idx[0]:idx[-1] + 1] = alts
    s = '\n'.join(lineas)
  s = re.sub(r'<script type="application/ld\+json">.*?</script>', '@@JSONLD@@', s, flags=re.S)
  s = s.replace('@@JSONLD@@', jsonld(lang, pag), 1).replace('@@JSONLD@@', '')
  i = s.index('</style>')
  s = s[:i] + CSS + s[i:]
  a = s.index('<section class="legal-hero">')
  b = s.index('<footer')
  s = s[:a] + cuerpo(lang, pag, con_props) + s[b:]
  out = os.path.join(RAIZ, T[lang]['archivos'][pag])
  open(out, 'w', encoding='utf-8').write(s)
  print('ok', T[lang]['archivos'][pag])


if __name__ == '__main__':
  con = zonas_con_propiedades()
  print('zonas con propiedades:', ', '.join(sorted(con)) or '(ninguna)')
  for lang in ('es', 'pt', 'en'):
    for pag in PAGINAS:
      armar(lang, pag, con)
