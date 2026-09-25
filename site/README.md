# Website

Portfolio-forsiden og læsevisningerne bygges fra projektets eksisterende dokumentation. `docs/`, `evidence/` og `scripts/` er fortsat kilderne til modulernes indhold. Websitet udfører ikke labkommandoerne.

## Opdatering

Redigér modulteksterne i `docs/`. Tilføj nye screenshots i den relevante `evidence/`-mappe og dens README. `site/content.json` indeholder de korte forsidetekster; layoutet ligger i `templates/` og `static/`.

GitHub Actions bygger, kontrollerer og publicerer `_site/` ved push til `main`. Pull requests bliver bygget og kontrolleret, men ikke publiceret. Vælg **Settings → Pages → Source: GitHub Actions** én gang i repoet.

## Lokal kontrol

Python 3.13 anbefales. Kør fra repo-roden; brug gerne et virtuelt miljø:

```text
python -m venv .venv-site
```

På Windows:

```powershell
.\.venv-site\Scripts\python.exe -m pip install -r site/requirements.txt
.\.venv-site\Scripts\python.exe -m unittest discover -s site -p 'test_*.py' -v
.\.venv-site\Scripts\python.exe site/build.py
.\.venv-site\Scripts\python.exe site/check.py
```

Åbn `_site/index.html` i browseren. Indhold, links, billedvisning og galleri fungerer uden en lokal webserver. Alternativt kan `_site/` serveres med `python -m http.server 8000 --directory _site`.

## Publicering

Kun de genererede HTML-sider, billedbeviser, arkitekturdiagrammet, AD-scriptet og webassets bliver kopieret til `_site/`. `.git`, `.obsidian`, lokale eksporter og installationsfiler bliver ikke publiceret af builderen. Preview og eksport er statiske; der bruges ingen analyseværktøjer, cookies eller eksterne scripts.

[GitHub: Custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
