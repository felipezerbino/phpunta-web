#!/usr/bin/env python3
"""Prueba de la traducción de la central de reservas (tools/i18n_reservas.py).
Para pt y en: traduce index.html y _ficha.html, escribe el resultado, corre restos() y `node --check` sobre cada <script> sin src.
Uso: python3 tools/probar-i18n-reservas.py [carpeta_de_salida]
Sale con código 1 si hay restos, pares sin usar o errores de sintaxis."""
import os, re, subprocess, sys, tempfile
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n_reservas as I

SALIDA = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-user/33caf91b-d724-55d2-ad8f-a34158e6992d/scratchpad/i18n'
ARCH = ['_lista', '_ficha']
mal = 0
usados = {}
for lang in ('pt', 'en'):
    os.makedirs(os.path.join(SALIDA, lang), exist_ok=True)
    for a in ARCH:
        src = open(os.path.join(RAIZ, 'reservas', a + '.html'), encoding='utf-8').read()
        uso = {}
        out = I.traducir(src, lang, uso)
        for k, n in uso.items():
            usados.setdefault((lang, k), 0)
            usados[(lang, k)] += n
        ruta = os.path.join(SALIDA, lang, a + '.html')
        open(ruta, 'w', encoding='utf-8').write(out)
        r = I.restos(out, lang)
        print('%s/%-11s restos: %d' % (lang, a, len(r)))
        for t in r:
            print('    RESTO:', t[:140].replace('\n', ' '))
        mal += len(r)
        # node --check de cada <script> sin src
        scripts = re.findall(r'<script(?![^>]*\bsrc=)(?![^>]*type="application/ld\+json")[^>]*>(.*?)</script>', out, re.S)
        for i, js in enumerate(scripts):
            with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
                f.write(js)
            p = subprocess.run(['node', '--check', f.name], capture_output=True, text=True)
            os.unlink(f.name)
            print('    node --check script #%d: %s' % (i + 1, 'OK' if p.returncode == 0 else 'ERROR\n' + p.stderr[:600]))
            if p.returncode: mal += 1
# pares que no se usaron en NINGUNA plantilla/idioma (el es no existe en el texto): señal de plantilla cambiada
sin = []
for es, pt, en in I.PARES:
    if (('pt', es) not in usados) and (('en', es) not in usados):
        # un par con pt==es y en==es se usa igual (se cuenta), así que si no aparece es porque no está en las plantillas
        sin.append(es)
print('pares: %d | sin usar en ninguna plantilla: %d' % (len(I.PARES), len(sin)))
for es in sin:
    print('    SIN USAR:', es[:120].replace('\n', ' '))
mal += len(sin)
sys.exit(1 if mal else 0)
