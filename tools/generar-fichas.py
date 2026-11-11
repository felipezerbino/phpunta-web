#!/usr/bin/env python3
"""Genera reservasnueva/<slug>/index.html para cada propiedad de la web de reservas.
Lee la lista de /web/slugs del backend y rellena la plantilla reservasnueva/_ficha.html.
Uso: python3 tools/generar-fichas.py [URL_DEL_BACKEND] [archivo_lista_salida]
Escribe en la salida (una por línea) las rutas generadas, para que el workflow las suba.
Si el backend no responde, no genera nada y termina bien: las páginas ya publicadas siguen."""
import html, json, os, re, sys, urllib.request

API = (sys.argv[1] if len(sys.argv) > 1 else 'https://phpunta-backend-production.up.railway.app').rstrip('/')
SALIDA = sys.argv[2] if len(sys.argv) > 2 else None
BASE_URL = 'https://phpunta.uy/reservasnueva/'
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PLANTILLA = os.path.join(RAIZ, 'reservasnueva', '_ficha.html')

def leer():
    req = urllib.request.Request(API + '/web/slugs', headers={'Accept': 'application/json', 'User-Agent': 'phpunta-web-deploy'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

def main():
    try:
        d = leer()
    except Exception as e:
        print('No se pudo leer /web/slugs (%s): no se generan fichas.' % e)
        return
    if not d.get('ok'):
        print('El backend respondió sin datos: no se generan fichas.')
        return
    tpl = open(PLANTILLA, encoding='utf-8').read()
    hechas = []
    def escribir(slug, rep):
        if not re.fullmatch(r'[a-z0-9-]{1,60}', slug or ''):
            return
        out = tpl
        for k, v in rep.items():
            out = out.replace('__' + k + '__', v)
        carpeta = os.path.join(RAIZ, 'reservasnueva', slug)
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, 'index.html')
        open(ruta, 'w', encoding='utf-8').write(out)
        hechas.append('reservasnueva/' + slug + '/index.html')
    for p in d.get('publicadas') or []:
        slug = p.get('slug') or ''
        titulo = p.get('titulo') or 'Propiedad'
        tipo = 'Casa' if p.get('tipo') == 'casa' else 'Apartamento'
        barrio = p.get('barrio') or 'Punta del Este'
        partes = [tipo + ' en ' + barrio]
        if p.get('dormitorios'): partes.append('%s dormitorios' % p['dormitorios'])
        if p.get('huespedes'): partes.append('hasta %s huéspedes' % p['huespedes'])
        desc = ', '.join(partes) + '. Reservá directo con Premium Host Punta: disponibilidad y precio real al instante.'
        url = BASE_URL + slug + '/'
        ld = {'@context': 'https://schema.org', '@type': 'VacationRental', 'name': titulo, 'url': url, 'description': desc,
              'address': {'@type': 'PostalAddress', 'addressLocality': barrio, 'addressRegion': 'Maldonado', 'addressCountry': 'UY'},
              'brand': {'@type': 'Organization', 'name': 'Premium Host Punta'}}
        if p.get('foto'): ld['image'] = [p['foto']]
        if p.get('huespedes'): ld['containsPlace'] = {'@type': 'Accommodation', 'occupancy': {'@type': 'QuantitativeValue', 'maxValue': p['huespedes']}}
        escribir(slug, {'TITULO': html.escape(titulo), 'DESC': html.escape(desc), 'SLUG': html.escape(slug), 'ESTADO': 'publicada',
                        'OG': html.escape(p.get('foto') or 'https://phpunta.uy/assets/img/home-hero-loop.jpg'), 'URL': html.escape(url),
                        'JSONLD': json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')})
    for slug in d.get('retiradas') or []:
        escribir(slug, {'TITULO': 'Propiedad no disponible', 'DESC': 'Esta propiedad ya no está disponible.', 'SLUG': html.escape(slug), 'ESTADO': 'retirada',
                        'OG': 'https://phpunta.uy/assets/img/home-hero-loop.jpg', 'URL': html.escape(BASE_URL + slug + '/'), 'JSONLD': '{}'})
    print('Fichas generadas: %d' % len(hechas))
    if SALIDA:
        open(SALIDA, 'w').write('\n'.join(hechas) + ('\n' if hechas else ''))

main()
