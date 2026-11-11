#!/usr/bin/env python3
"""Cambia los links del sitio de la central vieja (reservas.phpunta.uy, Avantio) a la nueva (phpunta.uy/reservas),
en el idioma de cada página. Se corre UNA vez al publicar la central (idempotente). Uso: python3 tools/enlazar-reservas.py"""
import glob, os, re

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
VIEJA = 'https://reservas.phpunta.uy/renta-vacacional/renta-rentas-d0/'
cambios = 0
for ruta in sorted(glob.glob(os.path.join(RAIZ, '*.html')) + glob.glob(os.path.join(RAIZ, 'en', '*.html')) + glob.glob(os.path.join(RAIZ, 'pt', '*.html'))):
  rel = os.path.relpath(ruta, RAIZ)
  base = '/en/reservas/' if rel.startswith('en/') else ('/pt/reservas/' if rel.startswith('pt/') else '/reservas/')
  s = open(ruta, encoding='utf-8').read()
  n = s
  n = n.replace(VIEJA, base)
  n = n.replace('"urlTemplate": "https://reservas.phpunta.uy/?q={search_term_string}"', '"urlTemplate": "https://phpunta.uy' + base + '?q={search_term_string}"')
  n = re.sub(r'\n?<link rel="dns-prefetch" href="https://reservas\.phpunta\.uy" />', '', n)
  n = n.replace('href="https://reservas.phpunta.uy"', 'href="' + base + '"').replace('href="https://reservas.phpunta.uy/"', 'href="' + base + '"')
  if n != s:
    open(ruta, 'w', encoding='utf-8').write(n)
    cambios += 1
    print('ok', rel)
restos = [os.path.relpath(r, RAIZ) for r in glob.glob(os.path.join(RAIZ, '**', '*.html'), recursive=True) if 'reservas.phpunta.uy' in open(r, encoding='utf-8').read()]
print('Páginas cambiadas: %d · con links viejos todavía: %s' % (cambios, restos or 'ninguna'))
