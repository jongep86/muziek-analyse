# Muzikale improvisatiegids

## Doel
Analyseer audiobestanden in /tracks en genereer per nummer
een interactieve HTML-improvisatiegids voor trompet in Bb.

## Quickstart
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Flask dev server draait op http://localhost:5050

## Tech stack
- **Backend**: Flask (app.py), Python 3.13
- **Analyse**: librosa, pychord, numba, scipy, scikit-learn
- **YouTube import**: yt-dlp
- **Frontend**: Jinja2 templates, standalone HTML output

## Pipeline
1. Laad audiobestand via librosa
2. Detecteer toonsoort (Krumhansl-Schmuckler via chroma_cqt)
3. Extraheer akkoorden met chord-extractor (Chordino)
4. Analyseer structuur: BPM, maten, akkoordwisselingstijdstempels
5. Map akkoorden naar toonschalen via muziektheorie-regels
6. Genereer fraseersuggesties per akkoord op basis van chord tones
7. Exporteer interactieve HTML naar /output/[tracknaam].html

## Container
- Multi-stage `Dockerfile`: uv on Debian 13 builds `/app/.venv`, runtime is `python:3.13-slim-trixie`. Every `FROM` is digest-pinned; Renovate bumps them.
- Runs as uid/gid 1000. Everything it writes goes to `DATA_DIR` (`/app/data`, the volume) or `/tmp` (numba, yt-dlp and deno caches), so the root filesystem can be read-only with a tmpfs or emptyDir on `/tmp`.
- An existing volume written by the old root image needs `fsGroup: 1000` (or a one-time chown) before this image can write to it.
- `/healthz` answers 200 when the app runs and the SQLite database opens.
- Local check: `docker build -t muziek-analyse . && docker run --rm --read-only --tmpfs /tmp:exec -v ma-data:/app/data -p 5050:5050 muziek-analyse`

## Dependencies
Zie requirements.txt. Installeer met `pip3 install -r requirements.txt`.

## Output-eisen
- Chromatische nootkaart per akkoord (kleurgecodeerd: 
  chord tone / spanning / approach / avoid / doorgangstoon)
- Tijdlijn synchroon met BPM
- Instrumenttranspositie dropdown (Bb trompet / Eb alt sax / concert pitch)
- Fraseersuggesties als kleurgecodeerde nootrijen
- Trompetspecifieke tips per akkoord (register, kleur)
- Eén zelfstandig HTML-bestand zonder externe dependencies

## Muziektheorie-regels
- im7/im9: Dorisch primair, Aeolisch alt
- ivm7: Dorisch van subdominant
- vmaj7/IIImaj7: Lydisch primair
- ii°m7b5: Locrisch
- V7alt: Altered scale primair, Diminished alt
- Chord tones altijd veilig op sterke maatdelen
- b9/b5 vermijden als niet in het akkoord