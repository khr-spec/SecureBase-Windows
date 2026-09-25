#!/usr/bin/env python3
"""Offline validation of generated HTML, anchors, assets and original evidence.

Usage: python site/check.py [_site]
This is a website check, not a validation of the running Windows lab.
"""
from __future__ import annotations
import hashlib
import json
import posixpath
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

def check(output: Path, source: Path = ROOT) -> dict:
    output = output.resolve(); source = source.resolve()
    config = json.loads((source / 'site/content.json').read_text(encoding='utf-8'))
    base_path = urlsplit(config['site_url']).path
    errors = []; links = 0; anchors = {}; soups = {}
    pages = sorted(output.rglob('*.html'))
    for page in pages:
        text = page.read_text(encoding='utf-8')
        rel = page.relative_to(output).as_posix()
        soup = BeautifulSoup(text, 'html.parser'); soups[rel] = soup
        ids = [n['id'] for n in soup.find_all(id=True)]
        if len(ids) != len(set(ids)): errors.append(f'{rel}: duplicate ids')
        anchors[rel] = set(ids)
        if len(soup.find_all('h1')) != 1: errors.append(f'{rel}: expected one h1')
        if not soup.html or soup.html.get('lang') != 'da': errors.append(f'{rel}: missing Danish document language')
        if not soup.find('meta', attrs={'charset': 'utf-8'}): errors.append(f'{rel}: UTF-8 not declared')
        for token in ['\ufffd', '\u00c3\u00a6', '\u00c3\u00b8', '\u00c3\u00a5', '\u00c2\u00b7']:
            if token in text: errors.append(f'{rel}: possible encoding damage ({token})')
        for image in soup.find_all('img'):
            if not image.has_attr('alt'): errors.append(f'{rel}: missing image alternative')
        for script in soup.find_all('script', src=True):
            if urlsplit(script['src']).scheme: errors.append(f'{rel}: external runtime script')
        if not soup.find('a', class_='skip-link'): errors.append(f'{rel}: skip navigation missing')
        for ext in soup.select('a[target="_blank"]'):
            if 'noopener' not in ext.get('rel', []): errors.append(f'{rel}: unsafe external tab link')
    for rel, soup in soups.items():
        for element, attr in [('a','href'),('img','src'),('script','src'),('link','href')]:
            for node in soup.find_all(element):
                value = node.get(attr)
                if not value: continue
                parsed = urlsplit(value)
                if parsed.scheme or parsed.netloc: continue
                path = unquote(parsed.path)
                if not path: target = rel
                elif path.startswith('/'):
                    if not path.startswith(base_path): errors.append(f'{rel}: wrong absolute project prefix {value}'); continue
                    target = path[len(base_path):]
                else: target = posixpath.normpath(posixpath.join(posixpath.dirname(rel), path))
                destination = output / target
                if destination.is_dir(): target = target.rstrip('/') + '/index.html'; destination = output / target
                if not destination.resolve().is_relative_to(output) or not destination.is_file():
                    errors.append(f'{rel}: broken {attr}: {value} -> {target}'); continue
                links += 1
                if parsed.fragment and target in anchors and unquote(parsed.fragment) not in anchors[target]:
                    errors.append(f'{rel}: missing anchor {target}#{parsed.fragment}')
    originals = sorted((source / 'evidence').rglob('*.png'))
    for src in originals + [source / config['architecture'], source / 'scripts/New-SecureBaseSupport.ps1']:
        dst = output / src.relative_to(source)
        if not dst.exists() or hashlib.sha256(src.read_bytes()).digest() != hashlib.sha256(dst.read_bytes()).digest():
            errors.append(f'Original file changed or missing: {src.relative_to(source)}')
    for image in list(output.rglob('*.png')) + list(output.rglob('*.webp')):
        try:
            with Image.open(image) as im: im.verify()
        except Exception as exc: errors.append(f'Invalid image {image}: {exc}')
    if len(soups.get('beviser/index.html', BeautifulSoup('', 'html.parser')).select('.evidence-card')) != len(originals):
        errors.append('Gallery does not cover every original screenshot')
    excluded = ('.git', '.obsidian', '.env', 'INSTALLER.py', 'requirements.txt', 'content.json')
    for path in output.rglob('*'):
        if path.name in excluded: errors.append(f'Non-public file in output: {path}')
    if not (output / '404.html').is_file(): errors.append('404 page missing')
    if not (output / 'sitemap.xml').is_file(): errors.append('Sitemap missing')
    if errors: raise ValueError('\n'.join(errors))
    return {'html_pages':len(pages),'local_references':links,'original_screenshots':len(originals),
            'original_script_unchanged':True,'architecture_unchanged':True,'errors':0}

if __name__ == '__main__':
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / '_site'
    try:
        result = check(output)
    except (ValueError, OSError) as exc:
        print(f'[FAIL] {exc}',file=sys.stderr);raise SystemExit(1)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print('[OK] Website links, anchors, images and original files verified.')
