#!/usr/bin/env python3
# Arma las páginas de BASES Y CONDICIONES DE LA RESERVA y REGLAS DE LA CASA (ES/PT/EN) a partir de las páginas legales que
# ya tiene el sitio (mismo encabezado, menú, estilos y pie). Los textos viven en tools/legales_reserva.py.
# Uso: python3 tools/generar-legales.py   (desde la raíz del repo). Se commitean las páginas generadas.
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from legales_reserva import BASES, REGLAS, VERSION

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITIO = 'https://phpunta.uy'
PLANTILLA = {'es': 'condiciones-generales.html', 'pt': 'pt/termos.html', 'en': 'en/terms.html'}
SALIDA = {
  'bases': {'es': 'condiciones-reserva.html', 'pt': 'pt/condicoes-reserva.html', 'en': 'en/booking-terms.html'},
  'reglas': {'es': 'reglas-de-la-casa.html', 'pt': 'pt/regras-da-casa.html', 'en': 'en/house-rules.html'},
}
TXT = {
  'es': {'eyebrow': 'Reservas', 'version': 'Versión del ', 'duda': '¿Tenés <em>alguna duda?</em>', 'duda_p': 'Escribinos y te respondemos enseguida.', 'contacto': 'Escribinos por WhatsApp', 'inicio': 'Inicio'},
  'pt': {'eyebrow': 'Reservas', 'version': 'Versão de ', 'duda': 'Tem <em>alguma dúvida?</em>', 'duda_p': 'Fale conosco e respondemos rapidinho.', 'contacto': 'Fale pelo WhatsApp', 'inicio': 'Início'},
  'en': {'eyebrow': 'Bookings', 'version': 'Version of ', 'duda': 'Any <em>questions?</em>', 'duda_p': 'Message us and we will answer right away.', 'contacto': 'Message us on WhatsApp', 'inicio': 'Home'},
}
HREFLANG = {'es': ['es', 'es-uy'], 'pt': ['pt', 'pt-br'], 'en': ['en', 'en-us']}


def cuerpo(tipo, lang):
  d = (BASES if tipo == 'bases' else REGLAS)[lang]
  t = TXT[lang]
  h = ['<section class="legal-hero">', '  <div class="container">', '    <span class="eyebrow">' + t['eyebrow'] + '</span>',
       '    <h1>' + d['h1'] + '</h1>', '    <div class="updated">' + t['version'] + VERSION + '</div>', '  </div>', '</section>', '',
       '<section class="legal-content">', '  <div class="container">',
       '    <article id="doc" data-tipo="' + tipo + '" data-version="' + VERSION + '">', '    <p>' + html.escape(d['intro']) + '</p>']
  if tipo == 'bases':
    for i, (tit, txt) in enumerate(d['items'], 1):
      h.append('    <h2>' + str(i) + '. ' + html.escape(tit) + '</h2>')
      h.append('    <p>' + html.escape(txt) + '</p>')
    h.append('    <p class="nota">' + d['nota'] + '</p>')
  else:
    h.append('    <ol>')
    for it in d['items']:
      h.append('      <li>' + html.escape(it) + '</li>')
    h.append('    </ol>')
    h.append('    <p>' + html.escape(d['cierre']) + '</p>')
  h += ['    </article>', '  </div>', '</section>', '', '<section class="legal-cta">', '  <div class="container">',
        '    <h3>' + t['duda'] + '</h3>', '    <p>' + t['duda_p'] + '</p>',
        '    <a href="https://api.whatsapp.com/send/?phone=59899716681" target="_blank" rel="noopener">' + t['contacto'] + '</a>',
        '  </div>', '</section>', '', '']
  return '\n'.join(h)


def armar(tipo, lang):
  d = (BASES if tipo == 'bases' else REGLAS)[lang]
  src = open(os.path.join(RAIZ, PLANTILLA[lang]), encoding='utf-8').read()
  url = SITIO + '/' + SALIDA[tipo][lang]
  titulo = d['titulo'] + ' | PHPunta'
  desc = d['desc']
  s = src
  s = re.sub(r'<title>[^<]*</title>', '<title>' + html.escape(titulo) + '</title>', s, count=1)
  s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + html.escape(desc), s, count=1)
  s = re.sub(r'\s*<meta name="keywords"[^>]*>', '', s, count=1)
  s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, s, count=1)
  for prop in ('og:title', 'twitter:title', 'og:image:alt', 'twitter:image:alt'):
    s = re.sub(r'(<meta (?:property|name)="' + prop + r'" content=")[^"]*', lambda m: m.group(1) + html.escape(titulo), s)
  for prop in ('og:description', 'twitter:description'):
    s = re.sub(r'(<meta (?:property|name)="' + prop + r'" content=")[^"]*', lambda m: m.group(1) + html.escape(desc), s)
  s = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, s)
  # hreflang: las tres versiones de ESTA página
  alts = []
  for lg in ('es', 'pt', 'en'):
    for code in HREFLANG[lg]:
      alts.append('<link rel="alternate" hreflang="' + code + '" href="' + SITIO + '/' + SALIDA[tipo][lg] + '" />')
  alts.append('<link rel="alternate" hreflang="x-default" href="' + SITIO + '/' + SALIDA[tipo]['es'] + '" />')
  lineas = s.split('\n')
  idx = [i for i, l in enumerate(lineas) if 'hreflang=' in l]
  if idx:
    lineas[idx[0]:idx[-1] + 1] = alts
    s = '\n'.join(lineas)
  # breadcrumb: el último elemento es esta página
  s = re.sub(r'("name":\s*")[^"]*("\s*,\s*"item":\s*")' + re.escape(SITIO) + r'/' + re.escape(PLANTILLA[lang]) + '"',
             lambda m: m.group(1) + d['titulo'] + m.group(2) + url + '"', s)
  a = s.index('<section class="legal-hero">')
  b = s.index('<footer')
  s = s[:a] + cuerpo(tipo, lang) + s[b:]
  out = os.path.join(RAIZ, SALIDA[tipo][lang])
  open(out, 'w', encoding='utf-8').write(s)
  print('ok', SALIDA[tipo][lang])


if __name__ == '__main__':
  for tipo in ('bases', 'reglas'):
    for lang in ('es', 'pt', 'en'):
      armar(tipo, lang)
