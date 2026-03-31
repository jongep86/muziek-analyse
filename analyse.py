#!/usr/bin/env python3
"""
Muzikale Improvisatiegids — Analyse Library
Pure analyse-functies voor audio: toonsoort, BPM, akkoorden, secties.
Geen I/O, geen HTML — alleen data in, data uit.
"""

import re
import numpy as np
from pychord import Chord

# librosa imported lazily in audio analysis functions to keep startup fast

# ──────────────────────────────────────────────
# 1. MUZIEKTHEORIE CONSTANTEN & HELPERS
# ──────────────────────────────────────────────

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ENHARMONIC = {
    'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B',
    'E#': 'F', 'B#': 'C',
}

# Krumhansl-Schmuckler key profiles
MAJOR_PROFILE_KS = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE_KS = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Temperley key profiles (better at distinguishing major/minor)
MAJOR_PROFILE_T = np.array([5.0, 2.0, 3.5, 2.0, 4.5, 4.0, 2.0, 4.5, 2.0, 3.5, 1.5, 4.0])
MINOR_PROFILE_T = np.array([5.0, 2.0, 3.5, 4.5, 2.0, 4.0, 2.0, 4.5, 3.5, 2.0, 1.5, 4.0])

# Combined profiles (average of KS and Temperley for robustness)
MAJOR_PROFILE = (MAJOR_PROFILE_KS + MAJOR_PROFILE_T) / 2
MINOR_PROFILE = (MINOR_PROFILE_KS + MINOR_PROFILE_T) / 2

# Scale definitions (semitone intervals from root)
SCALES = {
    'Ionisch (Majeur)':    [0, 2, 4, 5, 7, 9, 11],
    'Dorisch':             [0, 2, 3, 5, 7, 9, 10],
    'Frygisch':            [0, 1, 3, 5, 7, 8, 10],
    'Lydisch':             [0, 2, 4, 6, 7, 9, 11],
    'Mixolydisch':         [0, 2, 4, 5, 7, 9, 10],
    'Aeolisch (Mineur)':   [0, 2, 3, 5, 7, 8, 10],
    'Locrisch':            [0, 1, 3, 5, 6, 8, 10],
    'Altered':             [0, 1, 3, 4, 6, 8, 10],
    'Verminderd (HW)':     [0, 1, 3, 4, 6, 7, 9, 10],
    'Verminderd (WH)':     [0, 2, 3, 5, 6, 8, 9, 11],
    'Melodisch Mineur':    [0, 2, 3, 5, 7, 9, 11],
    'Blues':                [0, 3, 5, 6, 7, 10],
    'Pentatonisch Majeur': [0, 2, 4, 7, 9],
    'Pentatonisch Mineur': [0, 3, 5, 7, 10],
}

# Chord quality to scale mapping (from CLAUDE.md music theory rules)
CHORD_SCALE_MAP = {
    # Minor chords
    'm7':    {'primary': 'Dorisch',           'alt': 'Aeolisch (Mineur)'},
    'm9':    {'primary': 'Dorisch',           'alt': 'Aeolisch (Mineur)'},
    'm':     {'primary': 'Dorisch',           'alt': 'Aeolisch (Mineur)'},
    'min7':  {'primary': 'Dorisch',           'alt': 'Aeolisch (Mineur)'},
    'min':   {'primary': 'Dorisch',           'alt': 'Aeolisch (Mineur)'},
    'm6':    {'primary': 'Dorisch',           'alt': None},
    'm11':   {'primary': 'Dorisch',           'alt': 'Aeolisch (Mineur)'},
    # Major chords
    'maj7':  {'primary': 'Lydisch',           'alt': 'Ionisch (Majeur)'},
    'maj9':  {'primary': 'Lydisch',           'alt': 'Ionisch (Majeur)'},
    'M7':    {'primary': 'Lydisch',           'alt': 'Ionisch (Majeur)'},
    '':      {'primary': 'Ionisch (Majeur)',  'alt': 'Mixolydisch'},
    'maj':   {'primary': 'Ionisch (Majeur)',  'alt': 'Lydisch'},
    '6':     {'primary': 'Ionisch (Majeur)',  'alt': 'Lydisch'},
    # Dominant chords
    '7':     {'primary': 'Mixolydisch',       'alt': 'Altered'},
    '9':     {'primary': 'Mixolydisch',       'alt': 'Lydisch'},
    '7#9':   {'primary': 'Altered',           'alt': 'Verminderd (HW)'},
    '7b9':   {'primary': 'Altered',           'alt': 'Verminderd (HW)'},
    '7alt':  {'primary': 'Altered',           'alt': 'Verminderd (HW)'},
    '7#11':  {'primary': 'Lydisch',           'alt': 'Mixolydisch'},
    '13':    {'primary': 'Mixolydisch',       'alt': None},
    '7b13':  {'primary': 'Altered',           'alt': 'Mixolydisch'},
    # Half-diminished
    'm7b5':  {'primary': 'Locrisch',          'alt': None},
    'ø':     {'primary': 'Locrisch',          'alt': None},
    'ø7':    {'primary': 'Locrisch',          'alt': None},
    # Diminished
    'dim':   {'primary': 'Verminderd (WH)',   'alt': None},
    'dim7':  {'primary': 'Verminderd (WH)',   'alt': None},
    'o':     {'primary': 'Verminderd (WH)',   'alt': None},
    'o7':    {'primary': 'Verminderd (WH)',   'alt': None},
    # Augmented
    'aug':   {'primary': 'Melodisch Mineur',  'alt': None},
    '+':     {'primary': 'Melodisch Mineur',  'alt': None},
    # Sus chords
    'sus4':  {'primary': 'Mixolydisch',       'alt': 'Dorisch'},
    'sus2':  {'primary': 'Mixolydisch',       'alt': None},
    '7sus4': {'primary': 'Mixolydisch',       'alt': 'Dorisch'},
}

# Note role colors for the chromatic map
NOTE_ROLES = {
    'chord_tone':   {'label': 'Chord tone',   'color': '#2ecc71', 'priority': 1},
    'tension':      {'label': 'Spanning',      'color': '#3498db', 'priority': 2},
    'approach':     {'label': 'Approach',       'color': '#f39c12', 'priority': 3},
    'avoid':        {'label': 'Avoid',          'color': '#e74c3c', 'priority': 4},
    'passing':      {'label': 'Doorgangstoon', 'color': '#9b59b6', 'priority': 5},
}


def note_to_index(note_name):
    """Convert note name to chromatic index (0-11)."""
    clean = note_name.strip()
    if clean in ENHARMONIC:
        clean = ENHARMONIC[clean]
    try:
        return NOTE_NAMES.index(clean)
    except ValueError:
        return 0


def index_to_note(idx):
    """Convert chromatic index to note name."""
    return NOTE_NAMES[idx % 12]


def transpose_for_bb(note_idx):
    """Transpose concert pitch to Bb trumpet (up a major 2nd = +2 semitones)."""
    return (note_idx + 2) % 12


def transpose_for_eb(note_idx):
    """Transpose concert pitch to Eb alto sax (up a major 6th = +9 semitones)."""
    return (note_idx + 9) % 12


def get_chord_tones(chord_str):
    """Extract chord tones from a chord string using pychord."""
    try:
        c = Chord(chord_str)
        notes = c.components()
        return [note_to_index(n) for n in notes]
    except Exception:
        root = chord_str[0]
        if len(chord_str) > 1 and chord_str[1] in '#b':
            root = chord_str[:2]
        return [note_to_index(root)]


def get_chord_quality(chord_str):
    """Extract the quality suffix from a chord string."""
    root = chord_str[0]
    if len(chord_str) > 1 and chord_str[1] in '#b':
        root = chord_str[:2]
    quality = chord_str[len(root):]
    return quality


def get_scale_for_chord(chord_str):
    """Determine the best scale for a chord based on music theory rules."""
    quality = get_chord_quality(chord_str)
    mapping = CHORD_SCALE_MAP.get(quality, CHORD_SCALE_MAP.get('', None))
    if mapping is None:
        mapping = {'primary': 'Ionisch (Majeur)', 'alt': None}
    return mapping


def classify_notes_for_key(key, mode):
    """
    Classify all 12 chromatic notes for the global key of the track.
    Returns dict {note_index: role} with scale_tone / approach / outside.
    """
    root_idx = note_to_index(key)
    if mode == 'minor':
        # Use Dorian as primary (common in jazz/soul/deep house)
        scale_intervals = SCALES['Dorisch']
        alt_intervals = SCALES['Aeolisch (Mineur)']
    else:
        scale_intervals = SCALES['Ionisch (Majeur)']
        alt_intervals = SCALES['Lydisch']

    scale_notes = set((root_idx + iv) % 12 for iv in scale_intervals)
    alt_notes = set((root_idx + iv) % 12 for iv in alt_intervals)

    # Chord tones of the tonic chord (1, b3/3, 5, b7/7)
    if mode == 'minor':
        tonic_intervals = [0, 3, 7, 10]  # m7
    else:
        tonic_intervals = [0, 4, 7, 11]  # maj7
    tonic_tones = set((root_idx + iv) % 12 for iv in tonic_intervals)

    result = {}
    for i in range(12):
        if i in tonic_tones:
            result[i] = 'chord_tone'
        elif i in scale_notes:
            result[i] = 'tension'
        elif i in alt_notes:
            result[i] = 'approach'
        else:
            # Check if chromatic neighbor to a scale tone
            is_neighbor = any((i + d) % 12 in scale_notes for d in [1, -1])
            result[i] = 'passing' if is_neighbor else 'avoid'

    return result


def classify_notes_for_chord(chord_str):
    """
    Classify all 12 chromatic notes for a given chord.
    Returns dict {note_index: role}
    """
    chord_tones = get_chord_tones(chord_str)
    root = chord_str[0]
    if len(chord_str) > 1 and chord_str[1] in '#b':
        root = chord_str[:2]
    root_idx = note_to_index(root)

    scale_info = get_scale_for_chord(chord_str)
    scale_name = scale_info['primary']
    scale_intervals = SCALES.get(scale_name, SCALES['Ionisch (Majeur)'])
    scale_notes = set((root_idx + interval) % 12 for interval in scale_intervals)

    quality = get_chord_quality(chord_str)

    # Determine avoid notes based on chord quality
    avoid_intervals = set()
    if quality in ('', 'maj', 'maj7', 'M7', '6'):
        # Avoid b9 from chord tones (natural 4 over major)
        avoid_intervals.add(5)  # perfect 4th from root for major
    elif quality in ('m7', 'm9', 'min7', 'min', 'm', 'm11'):
        # Avoid b13 (b6) for minor if not in chord
        avoid_intervals.add(8)  # minor 6th
    elif quality in ('7', '9', '13'):
        # Avoid b9 for dominant
        avoid_intervals.add(1)  # b9 interval

    avoid_notes = set()
    for interval in avoid_intervals:
        note = (root_idx + interval) % 12
        if note not in chord_tones:
            avoid_notes.add(note)

    # Classify each note
    result = {}
    for i in range(12):
        if i in chord_tones:
            result[i] = 'chord_tone'
        elif i in avoid_notes:
            result[i] = 'avoid'
        elif i in scale_notes:
            # Scale tones that aren't chord tones = tensions
            result[i] = 'tension'
        else:
            # Check if chromatic approach to a chord tone
            is_approach = False
            for ct in chord_tones:
                if (i + 1) % 12 == ct or (i - 1) % 12 == ct:
                    is_approach = True
                    break
            if is_approach:
                result[i] = 'approach'
            else:
                result[i] = 'passing'

    return result


def generate_phrase_suggestions(chord_str, scale_name, root_idx):
    """Generate phrasing suggestions based on chord tones and scale."""
    chord_tones = get_chord_tones(chord_str)
    scale_intervals = SCALES.get(scale_name, SCALES['Ionisch (Majeur)'])
    scale_notes = [(root_idx + i) % 12 for i in scale_intervals]

    suggestions = []

    # 1. Arpeggio suggestion
    arp_notes = [index_to_note(n) for n in chord_tones]
    suggestions.append({
        'name': 'Arpeggio',
        'notes': chord_tones,
        'description': f'Speel de chord tones: {" → ".join(arp_notes)}',
        'tip': 'Begin op een sterke maatdeel met de grondtoon of terts.'
    })

    # 2. Scale run
    suggestions.append({
        'name': f'{scale_name} run',
        'notes': scale_notes,
        'description': f'Toonladder: {" → ".join(index_to_note(n) for n in scale_notes)}',
        'tip': 'Land op een chord tone op het volgende sterke maatdeel.'
    })

    # 3. Enclosure pattern (chromatic approach)
    if len(chord_tones) >= 2:
        target = chord_tones[2 % len(chord_tones)]  # target the 3rd or root
        above = (target + 1) % 12
        below = (target - 1) % 12
        suggestions.append({
            'name': 'Enclosure',
            'notes': [above, below, target],
            'description': f'Omsluit de {index_to_note(target)}: {index_to_note(above)} → {index_to_note(below)} → {index_to_note(target)}',
            'tip': 'Chromatische benadering van boven en onder naar een chord tone.'
        })

    # 4. 1-2-3-5 pattern
    if len(scale_notes) >= 5:
        pattern_notes = [scale_notes[0], scale_notes[1], scale_notes[2], scale_notes[4]]
        suggestions.append({
            'name': '1-2-3-5 Patroon',
            'notes': pattern_notes,
            'description': f'{" → ".join(index_to_note(n) for n in pattern_notes)}',
            'tip': 'Klassiek jazzpatroon, werkt goed als opening van een frase.'
        })

    return suggestions


def get_trumpet_tips(chord_str, quality):
    """Generate trumpet-specific tips for a chord."""
    tips = []
    if quality in ('7', '7alt', '7#9', '7b9', '9', '13'):
        tips.append('Dominant akkoord: gebruik spanning en release. Altered tonen geven extra kleur.')
        tips.append('Probeer bends en half-valve effecten op de 7e en altered tensions.')
    elif quality in ('m7', 'm9', 'm', 'min7', 'min', 'm11'):
        tips.append('Mineur akkoord: Dorisch geeft een warme, soulvolle klank.')
        tips.append('De 6e graad (Dorisch) geeft extra kleur t.o.v. natuurlijk mineur.')
    elif quality in ('maj7', 'M7', 'maj9'):
        tips.append('Majeur 7: Lydisch geeft een dromerige, open klank.')
        tips.append('Vermijd de kwart (#11 is wel veilig in Lydisch).')
    elif quality in ('m7b5', 'ø', 'ø7'):
        tips.append('Half-verminderd: Locrisch past, maar gebruik chord tones als anker.')
        tips.append('De b5 is een kenmerkende kleur — benadruk deze bewust.')
    elif quality in ('dim', 'dim7', 'o', 'o7'):
        tips.append('Verminderd: symmetrische toonladder, elk interval van 1,5 toon is een rustpunt.')
    else:
        tips.append('Gebruik chord tones op sterke maatdelen als veilige keuze.')

    tips.append('Midden register (G4-C6 concert) geeft de warmste toon voor deze stijl.')
    tips.append('Denk aan ademhaling: plan je frases in eenheden van 2-4 maten.')
    return tips


# ──────────────────────────────────────────────
# 1b. DEEP HOUSE PATROONBIBLIOTHEEK
# ──────────────────────────────────────────────

# Character categories with colors and icons
PATTERN_CHARACTERS = {
    'laid-back':   {'label': 'Laid-back',    'icon': '🌊', 'color': '#1abc9c', 'description': 'Ontspannen, zwevend, geen haast'},
    'cool':        {'label': 'Cool',         'icon': '😎', 'color': '#3498db', 'description': 'Strak, sophisticated, beheerst'},
    'jazzy':       {'label': 'Jazzy',        'icon': '🎷', 'color': '#9b59b6', 'description': 'Chromatisch, verrassend, harmonisch rijk'},
    'soulful':     {'label': 'Soulful',      'icon': '❤️', 'color': '#e74c3c', 'description': 'Warm, emotioneel, expressief'},
    'dreamy':      {'label': 'Dreamy',       'icon': '✨', 'color': '#2ecc71', 'description': 'Ruimtelijk, open, ambigu'},
    'groovy':      {'label': 'Groovy',       'icon': '🔥', 'color': '#f39c12', 'description': 'Ritmisch, dansbaar, herhalend'},
}

# Pattern definitions: each pattern is an interval recipe relative to root
# intervals: semitones from root (can go negative for downward movement)
# Patterns are grouped by character and tagged with compatible modes
DEEP_HOUSE_PATTERNS = [
    # ── LAID-BACK ──
    {
        'id': 'pent-descent',
        'name': 'Pentatonische daling',
        'character': 'laid-back',
        'intervals': [12, 10, 7, 5, 3, 0],
        'direction': 'down',
        'modes': ['minor'],
        'description': 'Dalende mineur pentatoniek vanuit het octaaf. Laat de noten vallen als druppels.',
        'tip': 'Speel achter de tel. Laat elke noot even klinken voor je verder gaat.',
    },
    {
        'id': 'dorian-glide',
        'name': 'Dorische glijbaan',
        'character': 'laid-back',
        'intervals': [7, 5, 3, 2, 0],
        'direction': 'down',
        'modes': ['minor'],
        'description': 'Van de kwint naar de grondtoon via de Dorische kleuren.',
        'tip': 'Gebruik een zachte tongslag. Denk aan een zucht.',
    },
    {
        'id': 'major-drift',
        'name': 'Majeur afdaling',
        'character': 'laid-back',
        'intervals': [12, 11, 9, 7, 4, 2, 0],
        'direction': 'down',
        'modes': ['major'],
        'description': 'Stapsgewijs dalen door de majeurtoonladder vanaf het octaaf.',
        'tip': 'Adem goed door en laat de frase organisch vallen.',
    },
    {
        'id': 'root-seven-five',
        'name': 'Root-7-5 drop',
        'character': 'laid-back',
        'intervals': [12, 10, 7],
        'direction': 'down',
        'modes': ['minor'],
        'description': 'Kort motief: octaaf → septiem → kwint. Minimalistische statement.',
        'tip': 'Perfect als openingsfrase. Laat de kwint hangen.',
    },

    # ── COOL ──
    {
        'id': 'nine-arp',
        'name': '9-arpeggio',
        'character': 'cool',
        'intervals': [0, 3, 7, 10, 14],
        'direction': 'up',
        'modes': ['minor'],
        'description': 'Mineur 9 arpeggio: 1 → b3 → 5 → b7 → 9. Moderne jazzklank.',
        'tip': 'Speel legato. De 9e graad geeft de "deep house-kleur".',
    },
    {
        'id': 'neighbor-tone',
        'name': 'Buurtoonfrase',
        'character': 'cool',
        'intervals': [7, 8, 7, 5, 7],
        'direction': 'mixed',
        'modes': ['both'],
        'description': 'Buurtoon boven de kwint en terug. Subtiele spanning en release.',
        'tip': 'Houd het licht. De buurtoon creëert spanning zonder dramatiek.',
    },
    {
        'id': 'chromatic-slide',
        'name': 'Chromatische slide',
        'character': 'cool',
        'intervals': [6, 5, 4, 3],
        'direction': 'down',
        'modes': ['minor'],
        'description': 'Chromatisch glijden van #4 naar b3. Half-valve of lip-bend effect.',
        'tip': 'Gebruik een halve klep of lip-bend voor een fluïde overgang.',
    },
    {
        'id': 'major-lydian-color',
        'name': 'Lydische kleur',
        'character': 'cool',
        'intervals': [0, 4, 6, 7, 11],
        'direction': 'up',
        'modes': ['major'],
        'description': 'Grondtoon → 3 → #4 → 5 → 7. Lydische openheid en glans.',
        'tip': 'De #4 geeft dat dromerige, zwevende gevoel. Laat die even klinken.',
    },

    # ── JAZZY ──
    {
        'id': 'enclosure-third',
        'name': 'Enclosure naar terts',
        'character': 'jazzy',
        'intervals': [4, 2, 3],
        'direction': 'mixed',
        'modes': ['minor'],
        'description': 'Boven (3) → onder (2) → doel (b3). Klassieke jazz-enclosure.',
        'tip': 'Speel de eerste twee noten snel, land op de b3 op het sterke maatdeel.',
    },
    {
        'id': 'bebop-fragment',
        'name': 'Bebop-fragment',
        'character': 'jazzy',
        'intervals': [0, 2, 3, 4, 5, 7],
        'direction': 'up',
        'modes': ['minor'],
        'description': 'Dorisch met chromatische doorgangstoon (3→4). Bebop-smaak in deep house.',
        'tip': 'Gebruik dit op dubbele snelheid (achtsten) voor een jazzy contrast.',
    },
    {
        'id': 'dom-altered',
        'name': 'Altered dominant lick',
        'character': 'jazzy',
        'intervals': [0, 1, 3, 4, 6, 7],
        'direction': 'up',
        'modes': ['both'],
        'description': 'Altered-tonen over een dominant akkoord. Spanning die oplost.',
        'tip': 'Gebruik dit als een V7 klinkt in de progressie. Los op naar de tonica.',
    },
    {
        'id': 'minor-cliche',
        'name': 'Mineur cliché-lijn',
        'character': 'jazzy',
        'intervals': [0, 11, 10, 9],
        'direction': 'down',
        'modes': ['minor'],
        'description': 'Dalende chromatische lijn: 1 → 7 → b7 → 6. Klassieke "line cliché".',
        'tip': 'Speel langzaam en laat elke halve toon duidelijk klinken.',
    },

    # ── SOULFUL ──
    {
        'id': 'blues-cry',
        'name': 'Blues cry',
        'character': 'soulful',
        'intervals': [3, 4, 3, 0],
        'direction': 'mixed',
        'modes': ['minor'],
        'description': 'b3 → 3 → b3 → 1. De klassieke blue note bending.',
        'tip': 'Bend van b3 naar 3 met de lip. Dit is de emotionele kern van blues.',
    },
    {
        'id': 'gospel-turn',
        'name': 'Gospel turn',
        'character': 'soulful',
        'intervals': [3, 5, 6, 7],
        'direction': 'up',
        'modes': ['minor'],
        'description': 'b3 → 4 → #4 → 5. Chromatische stijging naar de kwint. Gospel/soul.',
        'tip': 'Bouw op in dynamiek. Begin zacht, eindig vol op de kwint.',
    },
    {
        'id': 'dorian-sixth',
        'name': 'Dorische zesde',
        'character': 'soulful',
        'intervals': [0, 3, 5, 7, 9, 7],
        'direction': 'mixed',
        'modes': ['minor'],
        'description': 'Arpeggio met Dorische 6e. DÉ kenmerkende kleur van deep house.',
        'tip': 'De 6e graad is het verschil tussen somber en warm. Benadruk deze noot.',
    },
    {
        'id': 'major-soul',
        'name': 'Soulvolle majeur',
        'character': 'soulful',
        'intervals': [0, 4, 7, 9, 12, 9, 7],
        'direction': 'mixed',
        'modes': ['major'],
        'description': 'Stijgend arpeggio met 6e, terug via kwint. Warme, open majeur-frase.',
        'tip': 'Denk aan een vocale frase. Zing het eerst, speel het dan.',
    },

    # ── DREAMY ──
    {
        'id': 'quartal-stack',
        'name': 'Kwarten-stapeling',
        'character': 'dreamy',
        'intervals': [0, 5, 10, 15],
        'direction': 'up',
        'modes': ['both'],
        'description': 'Gestapelde kwarten. Ambigu, open, modern. Geen duidelijke tonaliteit.',
        'tip': 'Laat ruimte tussen de noten. Dit patroon leeft van de stilte ertussen.',
    },
    {
        'id': 'octave-float',
        'name': 'Octaaf-zweefvlucht',
        'character': 'dreamy',
        'intervals': [0, 12, 7, 12, 5, 12],
        'direction': 'mixed',
        'modes': ['both'],
        'description': 'Springen tussen octaaf en toonladdernoten. Creëert ruimte en diepte.',
        'tip': 'Gebruik zachte dynamiek. Dit patroon werkt als achtergrondkleur.',
    },
    {
        'id': 'sus-resolve',
        'name': 'Sus → Resolve',
        'character': 'dreamy',
        'intervals': [0, 5, 7, 5, 4, 0],
        'direction': 'mixed',
        'modes': ['major'],
        'description': 'Kwart → kwint → kwart → terts → grondtoon. Vertraagde resolutie.',
        'tip': 'Houd de kwart lang aan voor de resolutie naar de terts.',
    },
    {
        'id': 'minor-float',
        'name': 'Mineur zweeftoon',
        'character': 'dreamy',
        'intervals': [0, 7, 3, 10, 5, 12],
        'direction': 'mixed',
        'modes': ['minor'],
        'description': 'Springen door het mineur-akkoord met wijde intervallen.',
        'tip': 'Elk interval is een sprong. Denk in ruimte, niet in lijn.',
    },

    # ── GROOVY ──
    {
        'id': 'riff-hook',
        'name': 'Riff-hook',
        'character': 'groovy',
        'intervals': [0, 3, 5, 3, 0, 10],
        'direction': 'mixed',
        'modes': ['minor'],
        'description': 'Kort, herhalend riff. 1→b3→4→b3→1→b7(laag). Hoofd-motief materiaal.',
        'tip': 'Herhaal dit patroon met kleine variaties. Herhaling = groove.',
    },
    {
        'id': 'call-response',
        'name': 'Call & Response',
        'character': 'groovy',
        'intervals': [0, 3, 5, 7],
        'direction': 'up',
        'modes': ['minor'],
        'description': 'Stijgend motief (de "call"). Antwoord met een variatie.',
        'tip': 'Speel dit, wacht 2 tellen, speel dan het omgekeerde of een variatie.',
    },
    {
        'id': 'syncopated-fifth',
        'name': 'Syncopated kwint',
        'character': 'groovy',
        'intervals': [7, 5, 7, 3, 7, 0],
        'direction': 'mixed',
        'modes': ['both'],
        'description': 'De kwint als ankerpunt met toonladdernoten ertussen.',
        'tip': 'Accenten op de kwint, zachter op de tussennoten. Ritmisch spel!',
    },
    {
        'id': 'pent-riff-major',
        'name': 'Pentatonisch riff',
        'character': 'groovy',
        'intervals': [0, 2, 4, 7, 4, 2],
        'direction': 'mixed',
        'modes': ['major'],
        'description': 'Majeur pentatonisch riff: 1→2→3→5→3→2. Dansbaar en catchy.',
        'tip': 'Accent op de 5e noot. Maak het ritmisch interessant.',
    },
]


def generate_patterns_for_key(key, mode):
    """
    Generate all compatible patterns for a given key and mode.
    Returns patterns with actual note indices mapped to the key.
    """
    root_idx = note_to_index(key)
    result = []

    for pattern in DEEP_HOUSE_PATTERNS:
        # Check mode compatibility
        if pattern['modes'] != ['both'] and mode not in pattern['modes']:
            continue

        # Map intervals to actual chromatic note indices
        notes = [(root_idx + iv) % 12 for iv in pattern['intervals']]

        # Get note classifications for the key
        key_roles = classify_notes_for_key(key, mode)

        # Build note data with roles
        note_data = []
        for iv, note_idx in zip(pattern['intervals'], notes):
            role = key_roles.get(note_idx, 'passing')
            note_data.append({
                'index': note_idx,
                'name': index_to_note(note_idx),
                'role': role,
                'interval': iv,
            })

        character_info = PATTERN_CHARACTERS.get(pattern['character'], {})

        result.append({
            'id': pattern['id'],
            'name': pattern['name'],
            'character': pattern['character'],
            'character_label': character_info.get('label', pattern['character']),
            'character_icon': character_info.get('icon', ''),
            'character_color': character_info.get('color', '#888'),
            'direction': pattern['direction'],
            'notes': note_data,
            'description': pattern['description'],
            'tip': pattern['tip'],
        })

    return result


# ──────────────────────────────────────────────
# 1c. MELODIE-DETECTIE & PATROONHERKENNING
# ──────────────────────────────────────────────

def detect_melody(y_harm, sr, beat_times, key, mode, chords, duration):
    """
    Detect the dominant melody line using piptrack on the harmonic signal.
    Returns dict with notes, phrases, motifs, contour, and stats.
    """
    import librosa
    from scipy.ndimage import median_filter

    # Pitch tracking on harmonic signal, melody range only
    pitches, magnitudes = librosa.piptrack(
        y=y_harm, sr=sr, fmin=200, fmax=4000, threshold=0.1
    )

    # Extract dominant pitch per frame (highest magnitude)
    n_frames = pitches.shape[1]
    times = librosa.frames_to_time(np.arange(n_frames), sr=sr)
    dominant_pitches = np.zeros(n_frames)
    dominant_mags = np.zeros(n_frames)

    for t in range(n_frames):
        mag_col = magnitudes[:, t]
        if mag_col.max() > 0:
            idx = mag_col.argmax()
            dominant_pitches[t] = pitches[idx, t]
            dominant_mags[t] = mag_col[idx]

    # Convert Hz to MIDI, filter silence (0 Hz)
    valid = dominant_pitches > 0
    midi_raw = np.zeros(n_frames)
    midi_raw[valid] = np.round(12 * np.log2(dominant_pitches[valid] / 440.0) + 69).astype(int)
    midi_raw[~valid] = 0

    # Median filter to smooth jumps (5-frame window)
    midi_smoothed = np.copy(midi_raw)
    valid_mask = midi_raw > 0
    if np.sum(valid_mask) > 5:
        midi_vals = midi_raw[valid_mask]
        midi_vals = median_filter(midi_vals, size=5)
        midi_smoothed[valid_mask] = midi_vals

    # Magnitude threshold: keep only notes with sufficient energy
    mag_threshold = np.percentile(dominant_mags[dominant_mags > 0], 40) if np.any(dominant_mags > 0) else 0
    midi_smoothed[dominant_mags < mag_threshold] = 0

    # Key validation: prefer notes in the key's scale
    root_idx = note_to_index(key)
    if mode == 'minor':
        scale_intervals = SCALES['Dorisch']
    else:
        scale_intervals = SCALES['Ionisch (Majeur)']
    scale_pcs = set((root_idx + iv) % 12 for iv in scale_intervals)

    # Don't discard out-of-key notes entirely, but lower their confidence
    # (they might be chromatic approach or tension notes)

    # Group consecutive frames with same MIDI note into note events
    notes = _frames_to_notes(midi_smoothed, times, dominant_mags, scale_pcs)

    if not notes:
        return _empty_melody()

    # Segment into phrases
    phrases = _segment_phrases(notes, chords, duration)

    # Find motifs
    motifs = _find_motifs(phrases, notes)

    # Build contour
    contour = _build_contour(notes)

    # Stats
    midi_vals = [n['midi'] for n in notes]
    note_counts = {}
    for n in notes:
        note_counts[n['name']] = note_counts.get(n['name'], 0) + 1
    most_common = max(note_counts, key=note_counts.get) if note_counts else ''

    stats = {
        'total_notes': len(notes),
        'total_phrases': len(phrases),
        'total_motifs': len(motifs),
        'pitch_range': {
            'low': min(midi_vals), 'high': max(midi_vals),
            'low_name': f"{index_to_note(min(midi_vals) % 12)}{min(midi_vals) // 12 - 1}",
            'high_name': f"{index_to_note(max(midi_vals) % 12)}{max(midi_vals) // 12 - 1}",
        },
        'most_common_note': most_common,
    }

    return {
        'notes': notes,
        'phrases': phrases,
        'motifs': motifs,
        'contour': contour,
        'stats': stats,
    }


def _frames_to_notes(midi_smoothed, times, magnitudes, scale_pcs):
    """Group consecutive frames with same MIDI note into note events."""
    notes = []
    n_frames = len(midi_smoothed)
    i = 0
    while i < n_frames:
        if midi_smoothed[i] == 0:
            i += 1
            continue
        midi_val = int(midi_smoothed[i])
        start_frame = i
        mag_sum = 0
        count = 0
        while i < n_frames and midi_smoothed[i] == midi_val:
            mag_sum += magnitudes[i]
            count += 1
            i += 1
        end_frame = i - 1

        start_time = float(times[start_frame])
        end_time = float(times[end_frame])
        duration = end_time - start_time

        # Filter very short notes (< 80ms = noise)
        if duration < 0.08:
            continue

        pc = midi_val % 12
        in_key = pc in scale_pcs
        confidence = float(mag_sum / count) if count > 0 else 0

        notes.append({
            'start': round(start_time, 3),
            'end': round(end_time, 3),
            'midi': midi_val,
            'name': index_to_note(pc),
            'octave': midi_val // 12 - 1,
            'confidence': round(confidence, 3),
            'in_key': in_key,
        })

    return notes


def _segment_phrases(notes, chords, duration):
    """Split notes into phrases based on silence gaps or chord boundaries."""
    if not notes:
        return []

    phrases = []
    current_phrase_notes = [0]  # start with first note index

    for i in range(1, len(notes)):
        gap = notes[i]['start'] - notes[i - 1]['end']
        # New phrase on silence gap > 0.4s
        if gap > 0.4:
            phrases.append(_build_phrase(current_phrase_notes, notes))
            current_phrase_notes = [i]
        else:
            current_phrase_notes.append(i)

    # Last phrase
    if current_phrase_notes:
        phrases.append(_build_phrase(current_phrase_notes, notes))

    # Filter out very short phrases (< 3 notes)
    phrases = [p for p in phrases if len(p['note_indices']) >= 3]

    return phrases


def _build_phrase(note_indices, notes):
    """Build a phrase dict from note indices."""
    phrase_notes = [notes[i] for i in note_indices]
    intervals = []
    contour = []
    for j in range(1, len(phrase_notes)):
        iv = phrase_notes[j]['midi'] - phrase_notes[j - 1]['midi']
        intervals.append(iv)
        if iv > 0:
            contour.append('up')
        elif iv < 0:
            contour.append('down')
        else:
            contour.append('hold')

    return {
        'start': phrase_notes[0]['start'],
        'end': phrase_notes[-1]['end'],
        'note_indices': note_indices,
        'intervals': intervals,
        'contour': contour,
        'motif_id': None,
        'is_variation': False,
    }


def _find_motifs(phrases, notes):
    """Find recurring interval patterns across phrases using edit distance."""
    if len(phrases) < 2:
        return []

    # Extract all subsequences of length 3-8 from each phrase
    candidates = []
    for pi, phrase in enumerate(phrases):
        ivs = phrase['intervals']
        for length in range(3, min(9, len(ivs) + 1)):
            for start in range(len(ivs) - length + 1):
                sub = tuple(ivs[start:start + length])
                candidates.append((sub, pi, start))

    if not candidates:
        return []

    # Group similar candidates by edit distance
    clusters = []
    used = set()

    for i, (pat_i, pi_i, si_i) in enumerate(candidates):
        if i in used:
            continue
        cluster = [(pat_i, pi_i, si_i)]
        used.add(i)
        for j, (pat_j, pi_j, si_j) in enumerate(candidates):
            if j in used or pi_j == pi_i:
                continue
            if _interval_similarity(pat_i, pat_j) >= 0.7:
                cluster.append((pat_j, pi_j, si_j))
                used.add(j)
        # Only keep clusters that appear in 2+ different phrases
        phrase_ids = set(c[1] for c in cluster)
        if len(phrase_ids) >= 2:
            clusters.append(cluster)

    if not clusters:
        return []

    # Sort clusters by size (most recurring first), take top 5
    clusters.sort(key=lambda c: len(c), reverse=True)
    clusters = clusters[:5]

    # Deduplicate overlapping clusters
    motifs = []
    assigned_phrases = {}  # phrase_idx -> motif_id

    labels = ['A', 'B', 'C', 'D', 'E']
    for ci, cluster in enumerate(clusters):
        if ci >= len(labels):
            break
        canonical = cluster[0][0]  # use first pattern as canonical

        # Resolve example note names from first occurrence
        first_pat, first_pi, first_si = cluster[0]
        first_phrase = phrases[first_pi]
        example_midis = []
        for ni in range(first_si, min(first_si + len(canonical) + 1, len(first_phrase['note_indices']))):
            note_idx = first_phrase['note_indices'][ni]
            example_midis.append(notes[note_idx]['midi'])
        example_notes = [NOTE_NAMES[m % 12] for m in example_midis]

        # Build occurrences
        occurrences = []
        phrase_idxs = set()
        for pat, pi, si in cluster:
            if pi not in phrase_idxs:
                phrase_idxs.add(pi)
                phrase = phrases[pi]
                occurrences.append({
                    'phrase_idx': pi,
                    'start': phrase['start'],
                    'end': phrase['end'],
                })

        # Build contour summary
        contour_parts = []
        for iv in canonical:
            if iv > 0:
                contour_parts.append('up')
            elif iv < 0:
                contour_parts.append('down')
            else:
                contour_parts.append('hold')
        contour_summary = '-'.join(contour_parts)

        motif_id = labels[ci]
        motifs.append({
            'id': motif_id,
            'name': f'Motief {motif_id}',
            'intervals': list(canonical),
            'example_notes': example_notes,
            'occurrence_count': len(occurrences),
            'occurrences': occurrences,
            'contour_summary': contour_summary,
        })

        # Tag phrases
        for pi in phrase_idxs:
            if pi not in assigned_phrases:
                assigned_phrases[pi] = motif_id
                phrases[pi]['motif_id'] = motif_id
            elif assigned_phrases[pi] != motif_id:
                phrases[pi]['is_variation'] = True

    return motifs


def _interval_similarity(a, b):
    """Compare two interval tuples using normalized edit distance. Returns 0-1."""
    if not a or not b:
        return 0.0
    # Use simple edit distance on intervals
    la, lb = len(a), len(b)
    if abs(la - lb) > max(la, lb) * 0.3:
        return 0.0  # too different in length

    # Levenshtein on intervals (with tolerance of ±1 semitone)
    dp = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        dp[i][0] = i
    for j in range(lb + 1):
        dp[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if abs(a[i - 1] - b[j - 1]) <= 1 else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    max_len = max(la, lb)
    return 1.0 - dp[la][lb] / max_len


def _build_contour(notes):
    """Build a simplified contour from note events."""
    contour = []
    for i, note in enumerate(notes):
        if i == 0:
            direction = 'start'
        else:
            diff = note['midi'] - notes[i - 1]['midi']
            if diff > 0:
                direction = 'up'
            elif diff < 0:
                direction = 'down'
            else:
                direction = 'hold'
        contour.append({
            'time': note['start'],
            'midi': note['midi'],
            'direction': direction,
        })
    return contour


def _empty_melody():
    """Return empty melody data structure."""
    return {
        'notes': [],
        'phrases': [],
        'motifs': [],
        'contour': [],
        'stats': {
            'total_notes': 0, 'total_phrases': 0, 'total_motifs': 0,
            'pitch_range': None,
            'most_common_note': '',
        },
    }


def parse_filename_metadata(filename):
    """
    Extract key and BPM hints from filename patterns like:
    '01 Artist - Title - Cm - 125.mp3'
    Returns dict with optional 'key', 'mode', 'bpm' fields.
    """
    stem = filename.rsplit('.', 1)[0] if '.' in filename else filename
    result = {}

    # Match key pattern: single note letter + optional #/b + optional m (minor)
    # Look for patterns like "- Cm -", "- F# -", "- Bbm -"
    key_match = re.search(r'[-–]\s*([A-G][#b]?)(m)?\s*[-–]', stem)
    if key_match:
        note = key_match.group(1)
        is_minor = key_match.group(2) == 'm'
        result['key'] = note
        result['mode'] = 'minor' if is_minor else 'major'

    # Match BPM: a number between 60-200 near the end or between dashes
    bpm_match = re.search(r'[-–]\s*(\d{2,3})\s*(?:[-–]|$)', stem)
    if bpm_match:
        bpm = int(bpm_match.group(1))
        if 60 <= bpm <= 200:
            result['bpm'] = bpm

    return result


# ──────────────────────────────────────────────
# 2. AUDIO-ANALYSE
# ──────────────────────────────────────────────

def _key_profile_scores(chroma_mean, major_profile, minor_profile):
    """Compute correlation scores for all 24 keys against given profiles."""
    scores = []
    for i in range(12):
        rotated = np.roll(chroma_mean, -i)
        corr_major = np.corrcoef(rotated, major_profile)[0, 1]
        corr_minor = np.corrcoef(rotated, minor_profile)[0, 1]
        scores.append((corr_major, NOTE_NAMES[i], 'major'))
        scores.append((corr_minor, NOTE_NAMES[i], 'minor'))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores


def detect_key(y, sr, y_harm=None):
    """
    Detect key using multiple profile sets and segment voting.
    Combines Krumhansl-Schmuckler and Temperley profiles with
    segment-based voting for more robust major/minor distinction.
    """
    import librosa
    if y_harm is None:
        y_harm = librosa.effects.harmonic(y, margin=4)
    chroma = librosa.feature.chroma_cqt(y=y_harm, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    # Score with combined profiles
    scores_combined = _key_profile_scores(chroma_mean, MAJOR_PROFILE, MINOR_PROFILE)
    # Score with Temperley profiles (better major/minor distinction)
    scores_temperley = _key_profile_scores(chroma_mean, MAJOR_PROFILE_T, MINOR_PROFILE_T)
    # Score with KS profiles
    scores_ks = _key_profile_scores(chroma_mean, MAJOR_PROFILE_KS, MINOR_PROFILE_KS)

    # Get top candidates from each method
    top_combined = scores_combined[0]
    top_temperley = scores_temperley[0]
    top_ks = scores_ks[0]

    # Segment-based voting: split audio into ~30s segments and vote
    segment_frames = sr * 30
    n_segments = max(1, len(y_harm) // segment_frames)
    key_votes = {}
    for seg_i in range(n_segments):
        start = seg_i * segment_frames
        end = min((seg_i + 1) * segment_frames, len(y_harm))
        seg_chroma = librosa.feature.chroma_cqt(y=y_harm[start:end], sr=sr)
        seg_mean = np.mean(seg_chroma, axis=1)
        seg_scores = _key_profile_scores(seg_mean, MAJOR_PROFILE, MINOR_PROFILE)
        top = seg_scores[0]
        vote_key = (top[1], top[2])
        key_votes[vote_key] = key_votes.get(vote_key, 0) + 1

    # Determine winner: prefer consensus of methods
    candidates = {}
    for corr, key, mode in [top_combined, top_temperley, top_ks]:
        k = (key, mode)
        candidates[k] = candidates.get(k, 0) + corr

    # Add segment votes as bonus (weighted)
    for (key, mode), count in key_votes.items():
        k = (key, mode)
        candidates[k] = candidates.get(k, 0) + count * 0.3

    # Pick the candidate with highest combined score
    best = max(candidates.items(), key=lambda x: x[1])
    best_key, best_mode = best[0]
    best_corr = float(top_combined[0])

    # If the relative major/minor of the winner is very close, check b3 energy
    # to break ties (minor keys have strong b3 = 3 semitones above root)
    root_idx = NOTE_NAMES.index(best_key)
    relative_key = NOTE_NAMES[(root_idx + (3 if best_mode == 'minor' else 9)) % 12]
    relative_mode = 'major' if best_mode == 'minor' else 'minor'
    rel_k = (relative_key, relative_mode)
    if rel_k in candidates and candidates[rel_k] > candidates[best[0]] * 0.85:
        # Very close — use b3/3 energy ratio to decide
        b3_energy = chroma_mean[(root_idx + 3) % 12]
        m3_energy = chroma_mean[(root_idx + 4) % 12]
        if best_mode == 'major' and b3_energy > m3_energy * 1.15:
            # Strong minor third relative to major third → likely minor
            best_mode = 'minor'
        elif best_mode == 'minor' and m3_energy > b3_energy * 1.15:
            best_mode = 'major'

    return best_key, best_mode, best_corr


def detect_bpm(y, sr):
    """Detect BPM using multiple methods and selecting the best estimate."""
    import librosa
    # Method 1: standard beat tracking
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo1, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    if hasattr(tempo1, '__len__'):
        tempo1 = float(tempo1[0])

    # Method 2: tempo estimation with prior around 120 (common for dance/pop)
    tempi = librosa.feature.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)
    # Get the most common tempo candidates
    candidates = set()
    for t in (tempi.flatten() if hasattr(tempi, 'flatten') else [tempi]):
        t = float(t)
        candidates.add(t)
        candidates.add(t / 2)
        candidates.add(t * 2)
    candidates.add(tempo1)
    candidates.add(tempo1 / 2)
    candidates.add(tempo1 * 2)

    # Pick the candidate closest to typical music range (100-135 preferred, then 85-150)
    best = tempo1
    best_score = 999
    for c in candidates:
        if c < 60 or c > 200:
            continue
        # Prefer tempos in the 100-135 range (most pop/dance music)
        if 100 <= c <= 135:
            score = abs(c - 120)  # prefer near 120
        elif 85 <= c <= 150:
            score = 50 + abs(c - 120)
        else:
            score = 100 + abs(c - 120)
        if score < best_score:
            best_score = score
            best = c

    corrected = round(best)

    # Re-track beats at the corrected tempo
    _, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, bpm=corrected, units='frames'
    )
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    return corrected, beat_times.tolist()


def extract_chords_chroma(y, sr, bpm):
    """
    Extract chords using chroma features analysis.
    Uses 2-bar segments for stability, filters low-confidence results,
    and stabilizes short outlier chords.
    """
    import librosa
    # Use harmonic component for cleaner chroma
    y_harm = librosa.effects.harmonic(y, margin=4)

    # Beat tracking
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    _, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, bpm=bpm, units='frames'
    )
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y_harm, sr=sr)
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.median)

    # Chord templates: only major, minor, dom7, min7 (fewer = less noise)
    chord_templates = {}
    for root in range(12):
        root_name = NOTE_NAMES[root]
        # Major triad
        t = np.zeros(12)
        for iv in [0, 4, 7]: t[(root + iv) % 12] = 1.0
        chord_templates[root_name] = t
        # Minor triad
        t = np.zeros(12)
        for iv in [0, 3, 7]: t[(root + iv) % 12] = 1.0
        chord_templates[root_name + 'm'] = t
        # Dominant 7
        t = np.zeros(12)
        for iv in [0, 4, 7, 10]: t[(root + iv) % 12] = 1.0
        chord_templates[root_name + '7'] = t
        # Minor 7
        t = np.zeros(12)
        for iv in [0, 3, 7, 10]: t[(root + iv) % 12] = 1.0
        chord_templates[root_name + 'm7'] = t

    # Normalize templates once
    for name in chord_templates:
        chord_templates[name] = chord_templates[name] / (np.linalg.norm(chord_templates[name]) + 1e-6)

    # Classify per 4-bar segment (16 beats in 4/4) for cleaner results
    beats_per_segment = 16
    raw_chords = []

    i = 0
    while i < beat_chroma.shape[1]:
        end = min(i + beats_per_segment, beat_chroma.shape[1])
        segment = np.mean(beat_chroma[:, i:end], axis=1)
        segment = segment / (np.linalg.norm(segment) + 1e-6)

        best_chord = 'C'
        best_score = -1
        for chord_name, template in chord_templates.items():
            score = np.dot(segment, template)
            if score > best_score:
                best_score = score
                best_chord = chord_name

        start_time = beat_times[i] if i < len(beat_times) else 0
        end_time = beat_times[end] if end < len(beat_times) else (
            beat_times[-1] + 60.0 / bpm if len(beat_times) > 0 else 0)

        raw_chords.append({
            'chord': best_chord,
            'start': round(float(start_time), 2),
            'end': round(float(end_time), 2),
            'confidence': round(float(best_score), 3)
        })
        i = end

    # Stabilize pass 1: replace outlier surrounded by same chord
    stabilized = list(raw_chords)
    for i in range(1, len(stabilized) - 1):
        prev_ch = stabilized[i - 1]['chord']
        next_ch = stabilized[i + 1]['chord']
        curr_ch = stabilized[i]['chord']
        curr_conf = stabilized[i]['confidence']
        if prev_ch == next_ch and curr_ch != prev_ch and curr_conf < 0.9:
            stabilized[i]['chord'] = prev_ch

    # Stabilize pass 2: absorb low-confidence segments into stronger neighbor
    for i in range(1, len(stabilized)):
        if stabilized[i]['confidence'] < 0.75:
            stabilized[i]['chord'] = stabilized[i - 1]['chord']

    # Merge consecutive identical chords
    merged = []
    for chord_info in stabilized:
        if merged and merged[-1]['chord'] == chord_info['chord']:
            merged[-1]['end'] = chord_info['end']
            merged[-1]['confidence'] = max(merged[-1]['confidence'], chord_info['confidence'])
        else:
            merged.append(dict(chord_info))

    return merged


def detect_sections(chords, duration, bpm):
    """
    Detect song sections by grouping chords into time-based segments
    (~16 bars each) and labelling recurring chord progressions.
    """
    if len(chords) <= 4:
        return [{'name': 'Hele nummer', 'chords': chords, 'start': chords[0]['start'], 'end': chords[-1]['end']}]

    # Group chords into ~16-bar sections by time
    bar_duration = 4 * 60.0 / bpm
    section_duration = 16 * bar_duration
    raw_sections = []
    current_chords = []
    section_start = chords[0]['start']

    for ch in chords:
        if ch['start'] - section_start >= section_duration and current_chords:
            raw_sections.append(current_chords)
            current_chords = []
            section_start = ch['start']
        current_chords.append(ch)
    if current_chords:
        raw_sections.append(current_chords)

    # Create a fingerprint for each section (sequence of chord names)
    fingerprints = []
    for sec_chords in raw_sections:
        fp = tuple(ch['chord'] for ch in sec_chords)
        fingerprints.append(fp)

    # Assign labels: same/similar progressions get same letter
    labels = {}
    section_labels = []
    LABEL_NAMES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    label_idx = 0

    for fp in fingerprints:
        # Check if this fingerprint is similar enough to an existing one
        matched_label = None
        for known_fp, label in labels.items():
            if _progression_similarity(fp, known_fp) >= 0.6:
                matched_label = label
                break
        if matched_label is None:
            matched_label = LABEL_NAMES[label_idx % len(LABEL_NAMES)]
            label_idx += 1
            labels[fp] = matched_label
        section_labels.append(matched_label)

    # Build section objects
    sections = []
    for i, sec_chords in enumerate(raw_sections):
        label = section_labels[i]
        sections.append({
            'name': label,
            'chords': sec_chords,
            'start': sec_chords[0]['start'],
            'end': sec_chords[-1]['end'],
        })

    # Rename first/last if appropriate
    if sections:
        if sections[0]['start'] < 20:
            sections[0]['name'] = 'Intro'
        if duration - sections[-1]['end'] < 15 or sections[-1] is sections[-1]:
            if len(sections) > 1:
                sections[-1]['name'] = 'Outro'

    # Merge consecutive sections with same label
    merged = []
    for sec in sections:
        if merged and merged[-1]['name'] == sec['name']:
            merged[-1]['chords'].extend(sec['chords'])
            merged[-1]['end'] = sec['end']
        else:
            merged.append(dict(sec))

    return merged


def _progression_similarity(fp1, fp2):
    """Compare two chord progressions. Returns 0.0-1.0 similarity."""
    if not fp1 or not fp2:
        return 0.0
    # Compare chord-by-chord up to shortest length
    min_len = min(len(fp1), len(fp2))
    max_len = max(len(fp1), len(fp2))
    if max_len == 0:
        return 1.0
    matches = sum(1 for a, b in zip(fp1[:min_len], fp2[:min_len]) if a == b)
    # Penalize length differences
    return matches / max_len


def compute_bars(beat_times, bpm, total_duration):
    """Compute bar numbers and positions (assuming 4/4 time)."""
    bars = []
    beats_per_bar = 4
    for i in range(0, len(beat_times), beats_per_bar):
        bar_num = i // beats_per_bar + 1
        start = beat_times[i]
        end = beat_times[min(i + beats_per_bar, len(beat_times)) - 1]
        bars.append({'bar': bar_num, 'start': round(float(start), 2), 'end': round(float(end), 2)})
    return bars


# ──────────────────────────────────────────────
# 3. ANALYSE PIPELINE
# ──────────────────────────────────────────────

def analyse_track(audio_path, progress_callback=None):
    """
    Full analysis pipeline for a single audio file.
    Returns analysis_data dict. No file I/O, no HTML.

    progress_callback: optional callable(step_description) for status updates.
    """
    def _progress(msg):
        if progress_callback:
            progress_callback(msg)

    import librosa
    import soundfile as sf
    import soxr
    _progress("Audio laden...")
    # Use soundfile + soxr instead of librosa.load to avoid numba JIT hang
    data, orig_sr = sf.read(audio_path, dtype='float32')
    if len(data.shape) > 1:
        y = np.mean(data, axis=1)  # stereo to mono
    else:
        y = data
    if orig_sr != 22050:
        y = soxr.resample(y, orig_sr, 22050).astype(np.float32)
    sr = 22050
    duration = len(y) / sr

    _progress("Harmonisch signaal extraheren...")
    y_harm = librosa.effects.harmonic(y, margin=4)

    _progress("Toonsoort detecteren...")
    key, mode, key_confidence = detect_key(y, sr, y_harm=y_harm)

    _progress("BPM detecteren...")
    bpm, beat_times = detect_bpm(y, sr)

    _progress("Akkoorden extraheren...")
    chords = extract_chords_chroma(y, sr, bpm)

    _progress("Secties detecteren...")
    sections = detect_sections(chords, duration, bpm)

    _progress("Maten berekenen...")
    bars = compute_bars(beat_times, bpm, duration)

    _progress("Melodie detecteren...")
    melody = detect_melody(y_harm, sr, beat_times, key, mode, chords, duration)

    return {
        'key': key,
        'mode': mode,
        'key_confidence': key_confidence,
        'bpm': bpm,
        'duration': duration,
        'chords': chords,
        'sections': sections,
        'bars': bars,
        'melody': melody,
    }

