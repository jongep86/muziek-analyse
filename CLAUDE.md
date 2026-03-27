# Muzikale improvisatiegids

## Doel
Analyseer audiobestanden in /tracks en genereer per nummer 
een interactieve HTML-improvisatiegids voor trompet in Bb.

## Pipeline
1. Laad audiobestand via librosa
2. Detecteer toonsoort (Krumhansl-Schmuckler via chroma_cqt)
3. Extraheer akkoorden met chord-extractor (Chordino)
4. Analyseer structuur: BPM, maten, akkoordwisselingstijdstempels
5. Map akkoorden naar toonschalen via muziektheorie-regels
6. Genereer fraseersuggesties per akkoord op basis van chord tones
7. Exporteer interactieve HTML naar /output/[tracknaam].html

## Dependencies
librosa, chord-extractor, pychord, basic-pitch, numpy, scipy

## Output-eisen
- Chromatische nootkaart per akkoord (kleurgecodeerd: 
  chord tone / spanning / approach / avoid / doorgangstoon)
- Tijdlijn synchroon met BPM
- Bb-trompet transpositie toggle
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