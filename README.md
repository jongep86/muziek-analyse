# Muziek-Analyse

Analyseer audiobestanden en genereer interactieve improvisatiegidsen voor trompet in Bb.

## Wat doet het?

De app analyseert muzieknummers en genereert per track een uitgebreide gids met:

- **Toonsoort-detectie** — Krumhansl-Schmuckler algoritme via chroma features
- **Akkoord-extractie** — Chordino/NNLS via chord-extractor
- **BPM & structuur** — beat tracking, maten, secties
- **Melodie-detectie** — pitch tracking met motief-herkenning en contour-analyse
- **Toonschaal-mapping** — per akkoord de juiste schaal (Dorisch, Lydisch, Altered, etc.)
- **Fraseersuggesties** — chord tones, tensions, approach notes per akkoord
- **Nootkaart** — kleurgecodeerd: chord tone / spanning / approach / avoid / doorgangstoon

## Screenshots

De web-interface toont per track:
- Globale nootkaart met rollen per noot
- Tijdlijn met akkoorden en schalen
- Herkende melodische motieven met nootnamen
- Melodie-contour visualisatie
- Bb-trompet transpositie toggle

## Installatie

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Chord-extractor (Chordino)

De chord-extractor library vereist het Vamp plugin framework:

```bash
# macOS
brew install vamp-plugin-sdk

# Ubuntu/Debian
sudo apt-get install vamp-plugin-sdk

pip install chord-extractor
```

## Configuratie

Pas `config.py` aan voor je eigen setup:

```python
DEFAULT_AUDIO_DIR = '/pad/naar/je/muziek'
```

## Gebruik

```bash
source .venv/bin/activate
python app.py
```

Open `http://localhost:5050` in je browser.

### Tracks analyseren

1. Ga naar **Nieuwe Analyse**
2. Blader naar een map met audiobestanden
3. Selecteer tracks om te analyseren
4. Wacht tot de analyse klaar is (1-3 min per track)

### Export

Per track kun je exporteren naar:
- **Standalone HTML** — één bestand, geen externe dependencies
- **Markdown** — platte tekst met alle analyse-data

### Online toegang (optioneel)

Met Cloudflare Tunnel kun je de app bereikbaar maken via internet:

```bash
brew install cloudflared
./start-online.sh
```

## Muziektheorie-regels

De app volgt deze mapping voor schalen per akkoordfunctie:

| Akkoord | Primaire schaal | Alternatief |
|---------|----------------|-------------|
| im7/im9 | Dorisch | Aeolisch |
| IVm7 | Dorisch (subdominant) | — |
| Vmaj7/IIImaj7 | Lydisch | — |
| ii°m7b5 | Locrisch | — |
| V7alt | Altered | Diminished |

Chord tones zijn altijd veilig op sterke maatdelen. b9/b5 worden vermeden tenzij ze in het akkoord zitten.

## Tech stack

- **Python 3** met Flask
- **librosa** voor audio-analyse
- **chord-extractor** (Chordino) voor akkoorden
- **pychord** voor akkoord-parsing
- **scipy/numpy** voor signaalverwerking
- **SQLite** voor track-opslag

## Licentie

Persoonlijk project — niet bedoeld voor distributie.
