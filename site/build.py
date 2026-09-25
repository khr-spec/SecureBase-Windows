#!/usr/bin/env python3
"""Build SecureBase's static portfolio from the existing Markdown and evidence.

Run from any working directory: python site/build.py
Only the website output is written. AD scripts are read/copied, never executed.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
import json
import math
import os
import posixpath
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from PIL import Image
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
MD = MarkdownIt('commonmark', {'html': False}).enable('table').enable('strikethrough')


def read_utf8(path: Path) -> str:
    text = path.read_text(encoding='utf-8-sig')
    if '\ufffd' in text:
        raise ValueError(f'Replacement character found in {path}; restore a valid UTF-8 source.')
    return text


def safe_source(root: Path, rel: str) -> Path:
    path = root / rel
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Unsafe source path: {rel}')
    if not path.is_file():
        raise FileNotFoundError(f'Required source is missing: {rel}')
    return path


def github_slug(text: str) -> str:
    """Match ordinary GitHub Markdown heading anchors, including Danish letters."""
    text = text.strip().lower()
    text = ''.join(c for c in text if c in '-_ ' or unicodedata.category(c)[0] in ('L', 'N'))
    return text.replace(' ', '-')


def root_prefix(route: str) -> str:
    return '../' * (len(Path(route).parts) - 1)


def highlighted(code: str, language: str) -> str:
    try:
        lexer = get_lexer_by_name(language)
        return highlight(code, lexer, HtmlFormatter(nowrap=True))
    except ClassNotFound:
        return html.escape(code)


def evidence_items(root: Path, modules: list[dict]) -> list[dict]:
    items = []
    for module in modules:
        rel = f'evidence/{module["key"]}/README.md'
        soup = BeautifulSoup(MD.render(read_utf8(safe_source(root, rel))), 'html.parser')
        seen = set()
        for row in soup.select('table tr'):
            cols = row.find_all('td')
            if not cols:
                continue
            for link in row.find_all('a', href=True):
                raw = urlsplit(link['href']).path
                if not raw.lower().endswith('.png'):
                    continue
                target = posixpath.normpath(posixpath.join(posixpath.dirname(rel), unquote(raw)))
                if not target.startswith(f'evidence/{module["key"]}/'):
                    raise ValueError(f'Evidence outside expected module: {target}')
                safe_source(root, target)
                if target in seen:
                    continue
                seen.add(target)
                caption = cols[1].get_text(' ', strip=True) if len(cols) >= 3 else link.get_text(' ', strip=True)
                number = cols[0].get_text(' ', strip=True)
                items.append({'module': module['id'], 'key': module['key'], 'path': target,
                    'number': number, 'caption': caption,
                    'thumb': 'site-assets/thumbs/' + module['key'] + '/' + Path(target).stem + '.webp',
                    'search': f"{module['title']} {caption} {Path(target).name}"})
        actual = {p.relative_to(root).as_posix() for p in (root / 'evidence' / module['key']).glob('*.png')}
        if seen != actual:
            raise ValueError(f'Evidence index does not match PNG files in {module["key"]}: {actual ^ seen}')
        module['count'] = len(seen)
    return items


def source_mapping(modules: list[dict]) -> dict[str, str]:
    routes = {'README.md': 'index.html', 'scripts/README.md': 'kode/index.html',
              'evidence/README.md': 'beviser/index.html'}
    for m in modules:
        routes[f'docs/{m["key"]}.md'] = f'moduler/{m["key"]}.html'
        routes[f'evidence/{m["key"]}/README.md'] = f'beviser/index.html?modul={m["id"]}'
    return routes


def rewrite_url(value: str, source: str, route: str, mapping: dict[str, str], assets: set[str]) -> str:
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in ('http', 'https', 'mailto'):
            raise ValueError(f'Unsupported external URL in {source}: {value}')
        return value
    if not parsed.path:
        return value
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path)))
    if resolved not in mapping and resolved not in assets:
        raise ValueError(f'Unpublished local link in {source}: {value} -> {resolved}')
    dest = urlsplit(mapping.get(resolved, resolved))
    relative = posixpath.relpath(dest.path, posixpath.dirname(route) or '.')
    return urlunsplit(('', '', quote(relative, safe='/-._~'), dest.query or parsed.query, parsed.fragment))


def render_markdown(root: Path, source: str, route: str, mapping: dict[str, str], assets: set[str]) -> tuple[str, list[dict], int]:
    source_text = read_utf8(safe_source(root, source))
    soup = BeautifulSoup(MD.render(source_text), 'html.parser')
    first = soup.find('h1')
    if first:
        # The site provides its own title and breadcrumb navigation.
        following = first.find_next_sibling()
        if following and following.name == 'p' and following.find('a', href=True):
            following.decompose()
        first.decompose()
    # Remove only the leading summary block; it is represented in the page header.
    first_top = next((t for t in soup.children if getattr(t, 'name', None)), None)
    if first_top is not None and first_top.name == 'blockquote':
        first_top.decompose()
    top_tags = [t for t in soup.children if getattr(t, 'name', None)]
    if len(top_tags) >= 2 and top_tags[-2].name == 'hr' and top_tags[-1].name == 'p' and top_tags[-1].find('a'):
        top_tags[-1].decompose(); top_tags[-2].decompose()
    counts = {}
    toc = []
    for heading in soup.find_all(re.compile(r'^h[2-6]$')):
        text = heading.get_text(' ', strip=True)
        slug = github_slug(text)
        suffix = counts.get(slug, 0)
        counts[slug] = suffix + 1
        heading['id'] = slug + (f'-{suffix}' if suffix else '')
        if heading.name == 'h2':
            toc.append({'id': heading['id'], 'text': text})
    for tag, attr in [('a', 'href'), ('img', 'src')]:
        for node in soup.find_all(tag):
            if not node.has_attr(attr):
                continue
            original_value = node[attr]
            node[attr] = rewrite_url(original_value, source, route, mapping, assets)
            if tag == 'a' and original_value.startswith(('http://', 'https://')):
                node['target'] = '_blank'; node['rel'] = 'noopener noreferrer'
            if tag == 'a' and urlsplit(node['href']).path.lower().endswith('.png'):
                node['data-lightbox'] = ''; node['data-caption'] = node.get_text(' ', strip=True)
            if tag == 'a' and urlsplit(node['href']).path.lower().endswith('.ps1'):
                node['download'] = ''
    for img in list(soup.find_all('img')):
        img['loading'] = 'lazy'; img['decoding'] = 'async'
        # PNG source dimensions allow layout to reserve image space.
        dest_path = posixpath.normpath(posixpath.join(posixpath.dirname(route), unquote(urlsplit(img['src']).path)))
        with Image.open(safe_source(root, dest_path)) as original:
            img['width'], img['height'] = original.size
        parent = img.parent
        if parent.name != 'p' or len(parent.find_all('img')) != 1:
            continue
        next_tag = parent.find_next_sibling()
        caption = None
        if next_tag and next_tag.name == 'p' and next_tag.find('em') and not next_tag.find('img'):
            caption = next_tag
        figure = soup.new_tag('figure')
        link = soup.new_tag('a', href=img['src'])
        link['data-lightbox'] = ''; link['data-caption'] = img.get('alt', 'Billedbevis')
        link['aria-label'] = 'Forstør: ' + img.get('alt', 'Billedbevis')
        link.append(img.extract())
        hint = soup.new_tag('span', attrs={'class': 'image-hint', 'aria-hidden': 'true'})
        hint.string = 'Forstør ↗'; link.append(hint)
        figure.append(link)
        if caption:
            figcaption = soup.new_tag('figcaption')
            for child in list(caption.contents):
                figcaption.append(child.extract())
            figure.append(figcaption); caption.decompose()
        parent.replace_with(figure)
    for table in list(soup.find_all('table')):
        wrapper = soup.new_tag('div', attrs={'class': 'table-wrap', 'tabindex': '0', 'role': 'region', 'aria-label': 'Tabel, rul vandret ved behov'})
        table.wrap(wrapper)
    for pre in list(soup.find_all('pre')):
        code = pre.find('code')
        raw = code.get_text() if code else pre.get_text()
        classes = code.get('class', []) if code else []
        language = next((c[9:] for c in classes if c.startswith('language-')), 'text')
        fragment = BeautifulSoup('<div class="code-block"><div class="code-toolbar"><span></span><button class="copy-code" type="button" hidden>Kopiér</button></div><pre class="highlight"><code></code></pre></div>', 'html.parser')
        fragment.span.string = 'PowerShell' if language == 'powershell' else language.upper()
        target = fragment.code
        colored = BeautifulSoup('<pre>' + highlighted(raw, language) + '</pre>', 'html.parser')
        for child in list(colored.pre.contents):
            target.append(child.extract())
        pre.replace_with(fragment.div)
    words = len(soup.get_text(' ', strip=True).split())
    return str(soup), toc, max(1, math.ceil(words / 210))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as handle:
        handle.write(text)


def build(root: Path, output: Path, config: dict, templates: Path = SITE / 'templates', static: Path = SITE / 'static') -> dict:
    root = root.resolve(); output = output.resolve()
    if output == root or root.is_relative_to(output) or any(output.is_relative_to(root / x) for x in ['docs', 'scripts', 'evidence', 'assets', '.git', 'site']):
        raise ValueError('Output cannot replace repository source folders.')
    if output.is_symlink():
        raise ValueError('Output cannot be a symlink.')
    if output.exists() and any(output.iterdir()) and not (output / '.securebase-site').is_file():
        raise ValueError(f'Output {output} is not a previous SecureBase build. Select an empty folder.')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    write_text(output / '.securebase-site', 'Generated website; safe to rebuild.\n')
    config = copy.deepcopy(config)
    config['site_url'] = config['site_url'].rstrip('/') + '/'
    if not config['site_url'].startswith('https://'):
        raise ValueError('site_url must be an HTTPS URL.')
    modules = config['modules']
    evidence = evidence_items(root, modules)
    all_assets = {e['path'] for e in evidence} | {config['architecture'], 'scripts/New-SecureBaseSupport.ps1'}
    for rel in sorted(all_assets):
        src = safe_source(root, rel)
        dst = output / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    for entry in evidence:
        dst = output / entry['thumb']; dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(root / entry['path']) as im:
            im = im.convert('RGB'); im.thumbnail((640, 400), Image.Resampling.LANCZOS)
            im.save(dst, format='WEBP', quality=84, method=4)
    shutil.copytree(static, output / 'site-assets', dirs_exist_ok=True)
    env = Environment(loader=FileSystemLoader(templates), autoescape=select_autoescape(['html', 'xml']), trim_blocks=True, lstrip_blocks=True)
    env.globals.update(config=config, modules=modules, evidence_count=len(evidence))
    routes = source_mapping(modules)
    pages = []
    def render(template: str, route: str, **data):
        prefix = root_prefix(route)
        if route == '404.html':
            prefix = urlsplit(config['site_url']).path
        canonical = config['site_url'] + ('' if route == 'index.html' else route)
        content = env.get_template(template).render(root=prefix, canonical=canonical, **data)
        write_text(output / route, content + '\n'); pages.append(route)
    featured = []
    for item in config['featured']:
        entry = next(e for e in evidence if e['module'] == item['module'] and Path(e['path']).name == item['file'])
        featured.append({**entry, **item})
    script = read_utf8(root / 'scripts/New-SecureBaseSupport.ps1')
    start = script.find('# Opret Support-OU')
    end = script.find('# Opret Support-gruppen', start)
    excerpt = script[start:end].strip() if 0 <= start < end else '\n'.join(script.splitlines()[:20])
    render('home.html', 'index.html', title=config['title'],
        description='Et isoleret Windows-lab med Active Directory, DNS, Group Policy, PowerShell, Registry og sikkerhedslogning. Seks moduler med konkrete billedbeviser.',
        page_class='home-page', architecture=config['architecture'], featured=featured,
        code_excerpt='<pre class="highlight"><code>' + highlighted(excerpt, 'powershell') + '</code></pre>')
    for index, module in enumerate(modules):
        source = f'docs/{module["key"]}.md'; route = routes[source]
        body, toc, minutes = render_markdown(root, source, route, routes, all_assets)
        render('article.html', route, title=module['title'], description=module['summary'], body=body, toc=toc,
            page_class='module-page', module=module, reading_minutes=minutes,
            source_url=config['repository'] + '/blob/main/' + source,
            previous=modules[index-1] if index else None, next=modules[index+1] if index+1 < len(modules) else None)
    body, toc, minutes = render_markdown(root, 'scripts/README.md', 'kode/index.html', routes, all_assets)
    render('article.html', 'kode/index.html', title='PowerShell-scriptet',
        description='Den afprøvede kode til Support-afdelingen. Forudsætninger, kørsel, resultatkontrol og den fulde kommenterede kildekode.',
        body=body, toc=toc, reading_minutes=minutes, module=None, previous=modules[3], next=None,
        page_class='code-page', source_url=config['repository'] + '/blob/main/scripts/New-SecureBaseSupport.ps1')
    render('gallery.html', 'beviser/index.html', title='Billedbeviser',
        description=f'{len(evidence)} originale screenshots fra SecureBase Windows, fordelt på seks moduler. Filtrér efter modul og søg i beskrivelserne.',
        page_class='gallery-page', evidence=evidence)
    render('404.html', '404.html', title='Siden blev ikke fundet', description='Tilbage til SecureBase Windows.', page_class='error-page')
    write_text(output / '.nojekyll', '')
    write_text(output / 'robots.txt', 'User-agent: *\nAllow: /\nSitemap: ' + config['site_url'] + 'sitemap.xml\n')
    urls = ''.join('<url><loc>' + html.escape(config['site_url'] + ('' if p == 'index.html' else p)) + '</loc></url>' for p in pages if p != '404.html')
    write_text(output / 'sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
    return {'pages': len(pages), 'evidence': len(evidence), 'original_files': len(all_assets), 'output': str(output)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    parser.add_argument('--site-url', help='Public HTTPS base URL (trailing slash is added).')
    args = parser.parse_args()
    config = json.loads(read_utf8(SITE / 'content.json'))
    if args.site_url:
        config['site_url'] = args.site_url
    try:
        result = build(ROOT, args.output, config)
    except (ValueError, OSError, StopIteration) as exc:
        print(f'[ERROR] {exc}', file=sys.stderr); return 1
    print(f'[OK] {result["pages"]} HTML pages, {result["evidence"]} original screenshots. Output: {result["output"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
