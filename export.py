"""Export functies: genereer standalone HTML en Markdown uit analyse data."""

import json
from datetime import datetime
from analyse import (
    NOTE_NAMES, NOTE_ROLES, SCALES, PATTERN_CHARACTERS,
    note_to_index, index_to_note, transpose_for_bb, transpose_for_eb,
    get_chord_quality, get_chord_tones, get_scale_for_chord,
    classify_notes_for_key, classify_notes_for_chord,
    generate_phrase_suggestions, get_trumpet_tips,
    generate_patterns_for_key,
)


def _prepare_template_data(track_name, analysis_data):
    """Prepare all derived data needed for rendering (shared by HTML and Markdown)."""
    key = analysis_data['key']
    mode = analysis_data['mode']
    bpm = analysis_data['bpm']
    chords = analysis_data['chords']
    sections = analysis_data['sections']
    duration = analysis_data['duration']
    bars = analysis_data['bars']
    key_confidence = analysis_data['key_confidence']

    # Global chromatic note map
    global_note_roles = classify_notes_for_key(key, mode)

    # Global phrase suggestions based on tonic chord
    tonic_chord = f"{key}m7" if mode == 'minor' else f"{key}maj7"
    tonic_scale_info = get_scale_for_chord(tonic_chord)
    tonic_root_idx = note_to_index(key)
    global_phrases = generate_phrase_suggestions(tonic_chord, tonic_scale_info['primary'], tonic_root_idx)

    # Build unique chord data
    unique_chords = {}
    for ch in chords:
        chord_str = ch['chord']
        if chord_str not in unique_chords:
            quality = get_chord_quality(chord_str)
            scale_info = get_scale_for_chord(chord_str)
            root = chord_str[0]
            if len(chord_str) > 1 and chord_str[1] in '#b':
                root = chord_str[:2]
            root_idx = note_to_index(root)
            note_roles = classify_notes_for_chord(chord_str)
            phrases = generate_phrase_suggestions(chord_str, scale_info['primary'], root_idx)
            tips = get_trumpet_tips(chord_str, quality)
            unique_chords[chord_str] = {
                'chord': chord_str,
                'quality': quality,
                'scale_primary': scale_info['primary'],
                'scale_alt': scale_info['alt'],
                'root_idx': root_idx,
                'note_roles': {str(k): v for k, v in note_roles.items()},
                'phrases': phrases,
                'tips': tips,
            }

    # Section data
    sections_data = []
    for sec in sections:
        sec_chords = [{'chord': ch['chord'], 'start': ch['start'], 'end': ch['end'],
                        'confidence': ch.get('confidence', 0)} for ch in sec['chords']]
        sections_data.append({'name': sec['name'], 'start': sec['start'], 'end': sec['end'], 'chords': sec_chords})

    # All chords flat (for timeline)
    all_chords = [{'chord': ch['chord'], 'start': ch['start'], 'end': ch['end'],
                    'quality': get_chord_quality(ch['chord'])} for ch in chords]

    bb_key_idx = transpose_for_bb(note_to_index(key))
    bb_key = index_to_note(bb_key_idx)
    eb_key_idx = transpose_for_eb(note_to_index(key))
    eb_key = index_to_note(eb_key_idx)
    mode_nl = 'majeur' if mode == 'major' else 'mineur'

    # Deep house patterns for this key/mode
    patterns = generate_patterns_for_key(key, mode)

    # Melody data (graceful if not present — older analyses)
    melody = analysis_data.get('melody')
    melody_data = None
    if melody and melody.get('notes'):
        # Classify each melody note's role relative to the concurrent chord
        melody_notes_with_roles = []
        for note in melody['notes']:
            # Find the chord active at this note's start time
            active_chord = None
            for ch in chords:
                if ch['start'] <= note['start'] <= ch['end']:
                    active_chord = ch['chord']
                    break
            if active_chord:
                chord_roles = classify_notes_for_chord(active_chord)
                role = chord_roles.get(note['midi'] % 12, 'passing')
            else:
                role = global_note_roles.get(note['midi'] % 12, 'passing')
            melody_notes_with_roles.append({**note, 'role': role})

        motifs = melody.get('motifs', [])

        # Backfill example_notes for motifs from older analyses
        for motif in motifs:
            if 'example_notes' not in motif and motif.get('occurrences'):
                occ = motif['occurrences'][0]
                # Find phrase notes that match this occurrence's time range
                occ_notes = [n for n in melody_notes_with_roles
                             if occ['start'] <= n['start'] <= occ['end']]
                if occ_notes:
                    # Take first len(intervals)+1 notes
                    count = len(motif.get('intervals', [])) + 1
                    motif['example_notes'] = [NOTE_NAMES[n['midi'] % 12] for n in occ_notes[:count]]

        melody_data = {
            'notes': melody_notes_with_roles,
            'phrases': melody.get('phrases', []),
            'motifs': motifs,
            'contour': melody.get('contour', []),
            'stats': melody.get('stats', {}),
        }

    return {
        'track_name': track_name,
        'key': key, 'mode': mode, 'mode_nl': mode_nl,
        'bb_key': bb_key, 'eb_key': eb_key, 'bpm': bpm, 'duration': duration,
        'key_confidence': key_confidence,
        'bars': bars,
        'global_note_roles': global_note_roles,
        'global_phrases': global_phrases,
        'unique_chords': unique_chords,
        'sections_data': sections_data,
        'all_chords': all_chords,
        'patterns': patterns,
        'pattern_characters': PATTERN_CHARACTERS,
        'melody': melody_data,
    }


def generate_html(track_name, analysis_data):
    """Generate a self-contained HTML improvisation guide."""
    d = _prepare_template_data(track_name, analysis_data)

    # Serialize for JS
    global_roles_json = json.dumps({str(k): v for k, v in d['global_note_roles'].items()})
    global_phrases_json = json.dumps(d['global_phrases'], ensure_ascii=False)
    unique_chords_json = json.dumps(d['unique_chords'], ensure_ascii=False)
    sections_json = json.dumps(d['sections_data'], ensure_ascii=False)
    bars_json = json.dumps(d['bars'])
    all_chords_json = json.dumps(d['all_chords'], ensure_ascii=False)
    patterns_json = json.dumps(d['patterns'], ensure_ascii=False)
    pattern_chars_json = json.dumps(d['pattern_characters'], ensure_ascii=False)
    melody_json = json.dumps(d.get('melody'), ensure_ascii=False)

    key = d['key']
    mode_nl = d['mode_nl']
    bb_key = d['bb_key']
    eb_key = d['eb_key']
    bpm = d['bpm']
    duration = d['duration']
    key_confidence = d['key_confidence']
    unique_count = len(d['unique_chords'])
    sections = d['sections_data']
    chords = analysis_data['chords']

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Improvisatiegids: {track_name}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: #0a0a0f;
    color: #e0e0e0;
    line-height: 1.6;
}}
.container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}

header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 28px; border-radius: 16px; margin-bottom: 20px; border: 1px solid #2a2a4a;
}}
header h1 {{ font-size: 1.6em; color: #e94560; margin-bottom: 8px; word-break: break-word; }}
.meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-top: 14px; }}
.meta-card {{ background: rgba(255,255,255,0.05); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }}
.meta-card .label {{ font-size: 0.7em; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
.meta-card .value {{ font-size: 1.3em; font-weight: 700; color: #fff; }}
.meta-card .sub {{ font-size: 0.75em; color: #aaa; }}

.toggle-container {{ display: flex; align-items: center; gap: 10px; margin: 14px 0 0; padding: 10px 14px; background: rgba(233, 69, 96, 0.1); border-radius: 8px; border: 1px solid rgba(233, 69, 96, 0.3); }}
.toggle-switch {{ position: relative; width: 48px; height: 24px; cursor: pointer; }}
.toggle-switch input {{ opacity: 0; width: 0; height: 0; }}
.toggle-slider {{ position: absolute; inset: 0; background: #333; border-radius: 24px; transition: 0.3s; }}
.toggle-slider:before {{ content: ""; position: absolute; height: 18px; width: 18px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s; }}
.toggle-switch input:checked + .toggle-slider {{ background: #e94560; }}
.toggle-switch input:checked + .toggle-slider:before {{ transform: translateX(24px); }}

.legend {{ display: flex; gap: 14px; flex-wrap: wrap; margin: 14px 0; padding: 10px 12px; background: rgba(255,255,255,0.03); border-radius: 8px; font-size: 0.8em; }}
.legend-item {{ display: flex; align-items: center; gap: 5px; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}

.timeline-container {{ background: #111; border-radius: 12px; padding: 16px; margin-bottom: 20px; border: 1px solid #2a2a4a; overflow-x: auto; }}
.timeline-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
.timeline-header h2 {{ color: #e94560; font-size: 1.1em; }}
.timeline {{ position: relative; height: 60px; background: #1a1a2e; border-radius: 8px; overflow: hidden; cursor: pointer; }}
.chord-block {{ position: absolute; top: 0; height: 100%; display: flex; align-items: center; justify-content: center; border-right: 1px solid rgba(0,0,0,0.3); font-weight: 600; font-size: 0.8em; cursor: pointer; transition: filter 0.15s; overflow: hidden; white-space: nowrap; padding: 0 3px; }}
.chord-block:hover {{ filter: brightness(1.3); z-index: 2; }}
.section-markers {{ position: relative; height: 22px; margin-top: 4px; }}
.section-marker {{ position: absolute; font-size: 0.7em; font-weight: 700; color: #e94560; background: rgba(233,69,96,0.15); padding: 1px 6px; border-radius: 4px; }}

.section-card {{ background: #111; border-radius: 12px; padding: 20px; margin-bottom: 16px; border: 1px solid #2a2a4a; }}
.section-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }}
.section-label {{ font-size: 1.1em; font-weight: 800; color: #e94560; background: rgba(233,69,96,0.15); padding: 4px 14px; border-radius: 6px; min-width: 36px; text-align: center; }}
.section-time {{ font-size: 0.85em; color: #888; }}
.section-chords {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }}
.section-chord {{ padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 1.05em; cursor: pointer; transition: all 0.15s; border: 2px solid transparent; }}
.section-chord:hover {{ transform: scale(1.05); }}
.section-chord.active {{ border-color: #fff; }}
.section-chord .chord-dur {{ display: block; font-size: 0.6em; font-weight: 400; color: rgba(255,255,255,0.6); margin-top: 2px; }}

.chord-color-major {{ background: rgba(46, 204, 113, 0.4); color: #fff; }}
.chord-color-minor {{ background: rgba(52, 152, 219, 0.4); color: #fff; }}
.chord-color-dom {{ background: rgba(243, 156, 18, 0.4); color: #fff; }}
.chord-color-dim {{ background: rgba(231, 76, 60, 0.4); color: #fff; }}

.chord-detail {{ background: #0d0d18; border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a; margin-top: -4px; margin-bottom: 16px; display: none; }}
.chord-detail.visible {{ display: block; }}
.chord-detail h2 {{ color: #e94560; font-size: 1.3em; margin-bottom: 14px; }}
.detail-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }}
@media (max-width: 600px) {{ .detail-grid {{ grid-template-columns: 1fr; }} }}

.chromatic-map {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 3px; margin-bottom: 16px; }}
.note-cell {{ text-align: center; padding: 8px 2px; border-radius: 6px; font-weight: 600; font-size: 0.8em; transition: transform 0.15s; }}
.note-cell:hover {{ transform: scale(1.1); z-index: 2; }}
.note-cell .note-name {{ display: block; }}
.note-cell .note-role {{ display: block; font-size: 0.6em; font-weight: 400; opacity: 0.8; margin-top: 1px; }}
.note-cell.chord_tone {{ background: rgba(46,204,113,0.3); border: 2px solid #2ecc71; color: #2ecc71; }}
.note-cell.tension {{ background: rgba(52,152,219,0.3); border: 2px solid #3498db; color: #3498db; }}
.note-cell.approach {{ background: rgba(243,156,18,0.2); border: 2px solid #f39c12; color: #f39c12; }}
.note-cell.avoid {{ background: rgba(231,76,60,0.2); border: 2px solid #e74c3c; color: #e74c3c; }}
.note-cell.passing {{ background: rgba(155,89,182,0.15); border: 1px solid rgba(155,89,182,0.4); color: #9b59b6; }}

.phrase-card {{ background: rgba(255,255,255,0.03); border: 1px solid #2a2a4a; border-radius: 8px; padding: 14px; margin-bottom: 10px; }}
.phrase-card h4 {{ color: #3498db; margin-bottom: 6px; font-size: 0.95em; }}
.phrase-notes {{ display: flex; gap: 5px; flex-wrap: wrap; margin: 6px 0; }}
.phrase-note {{ width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 700; font-size: 0.75em; }}
.phrase-note.chord_tone {{ background: #2ecc71; color: #000; }}
.phrase-note.tension {{ background: #3498db; color: #fff; }}
.phrase-note.approach {{ background: #f39c12; color: #000; }}
.phrase-note.avoid {{ background: #e74c3c; color: #fff; }}
.phrase-note.passing {{ background: #9b59b6; color: #fff; }}
.phrase-arrow {{ display: flex; align-items: center; color: #555; }}
.phrase-tip {{ font-size: 0.8em; color: #aaa; font-style: italic; }}

.tips-section {{ background: rgba(243,156,18,0.05); border: 1px solid rgba(243,156,18,0.2); border-radius: 8px; padding: 14px; }}
.tips-section h3 {{ color: #f39c12; margin-bottom: 8px; font-size: 0.95em; }}
.tips-section ul {{ list-style: none; }}
.tips-section li {{ padding: 4px 0 4px 18px; position: relative; font-size: 0.85em; color: #ccc; }}
.tips-section li:before {{ content: "♪"; position: absolute; left: 0; color: #f39c12; }}

.patterns-section {{ margin-bottom: 24px; }}
.patterns-section > h2 {{ color: #e94560; font-size: 1.2em; margin-bottom: 6px; }}
.patterns-section > p {{ color: #888; font-size: 0.85em; margin-bottom: 16px; }}
.pattern-filters {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
.pattern-filter-btn {{ padding: 6px 14px; border-radius: 20px; border: 2px solid transparent; font-size: 0.8em; font-weight: 600; cursor: pointer; transition: all 0.2s; background: rgba(255,255,255,0.05); color: #aaa; }}
.pattern-filter-btn:hover {{ background: rgba(255,255,255,0.1); color: #fff; }}
.pattern-filter-btn.active {{ color: #fff; }}
.pattern-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }}
.pattern-card {{ background: rgba(255,255,255,0.03); border: 1px solid #2a2a4a; border-radius: 12px; padding: 16px; transition: all 0.2s; position: relative; overflow: hidden; }}
.pattern-card:hover {{ border-color: rgba(255,255,255,0.15); }}
.pattern-card .pattern-accent {{ position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 12px 12px 0 0; }}
.pattern-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; margin-top: 4px; }}
.pattern-icon {{ font-size: 1.2em; }}
.pattern-name {{ font-weight: 700; color: #fff; font-size: 0.95em; flex: 1; }}
.pattern-direction {{ font-size: 0.65em; text-transform: uppercase; letter-spacing: 1px; padding: 2px 8px; border-radius: 10px; background: rgba(255,255,255,0.08); color: #888; }}
.pattern-character-badge {{ display: inline-flex; align-items: center; gap: 4px; font-size: 0.7em; font-weight: 600; padding: 2px 10px; border-radius: 12px; margin-bottom: 8px; }}
.pattern-desc {{ font-size: 0.82em; color: #ccc; margin-bottom: 10px; line-height: 1.5; }}
.pattern-notes-row {{ display: flex; align-items: center; gap: 4px; flex-wrap: wrap; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; margin-bottom: 8px; }}
.pattern-note {{ width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 700; font-size: 0.75em; }}
.pattern-note.chord_tone {{ background: #2ecc71; color: #000; }}
.pattern-note.tension {{ background: #3498db; color: #fff; }}
.pattern-note.approach {{ background: #f39c12; color: #000; }}
.pattern-note.avoid {{ background: #e74c3c; color: #fff; }}
.pattern-note.passing {{ background: #9b59b6; color: #fff; }}
.pattern-arrow-up {{ color: #2ecc71; font-size: 0.8em; }}
.pattern-arrow-down {{ color: #e94560; font-size: 0.8em; }}
.pattern-arrow-same {{ color: #888; font-size: 0.8em; }}
.pattern-tip {{ font-size: 0.78em; color: #aaa; font-style: italic; padding-left: 16px; position: relative; }}
.motifs-section {{ margin-bottom: 24px; }}

footer {{ text-align: center; padding: 16px; color: #444; font-size: 0.75em; }}
</style>
</head>
<body>
<div class="container">

<header>
    <h1>{track_name}</h1>
    <div class="meta-grid">
        <div class="meta-card"><div class="label">Toonsoort (Concert)</div><div class="value">{key} {mode_nl}</div><div class="sub">Betrouwbaarheid: {round(key_confidence * 100)}%</div></div>
        <div class="meta-card"><div class="label">Toonsoort (Bb Trompet)</div><div class="value" id="bb-key">{bb_key} {mode_nl}</div></div>
        <div class="meta-card"><div class="label">Toonsoort (Eb Alt Sax)</div><div class="value" id="eb-key">{eb_key} {mode_nl}</div></div>
        <div class="meta-card"><div class="label">Tempo</div><div class="value">{bpm} BPM</div></div>
        <div class="meta-card"><div class="label">Duur</div><div class="value">{int(duration // 60)}:{int(duration % 60):02d}</div></div>
        <div class="meta-card"><div class="label">Secties / Akkoorden</div><div class="value">{len(sections)} / {unique_count}</div><div class="sub">{len(chords)} wissels totaal</div></div>
    </div>
    <div class="toggle-container">
        <label for="transpose-select" style="color:#ccc;">Transpositie:</label>
        <select id="transpose-select" style="background:#1a1a2e; color:#fff; border:1px solid #444; padding:6px 12px; border-radius:6px; font-size:0.95em; margin-left:8px;">
            <option value="bb" selected>Bb Trompet (+2)</option>
            <option value="eb">Eb Alt Sax (+9)</option>
            <option value="concert">Concert pitch</option>
        </select>
    </div>
</header>

<div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#2ecc71;"></div> Chord tone</div>
    <div class="legend-item"><div class="legend-dot" style="background:#3498db;"></div> Spanning</div>
    <div class="legend-item"><div class="legend-dot" style="background:#f39c12;"></div> Approach</div>
    <div class="legend-item"><div class="legend-dot" style="background:#e74c3c;"></div> Avoid</div>
    <div class="legend-item"><div class="legend-dot" style="background:#9b59b6;"></div> Doorgang</div>
</div>

<div class="section-card">
    <h2 style="color:#e94560; font-size:1.2em; margin-bottom:12px;">Chromatische nootkaart — {key} {mode_nl}</h2>
    <p style="color:#888; font-size:0.85em; margin-bottom:12px;">Overzicht van alle noten in de toonsoort. Chord tones = tonica-akkoord, spanning = toonladdernoten, approach = alternatieve toonladder.</p>
    <div class="chromatic-map" id="global-notemap"></div>
    <div id="global-phrases" style="margin-top:16px;"></div>
</div>

<div class="section-card patterns-section">
    <h2>Deep House Patronen — Ingrediënten voor improvisatie</h2>
    <p>Intervalmotieven passend bij {key} {mode_nl}. Gebruik als bouwstenen voor je frases.</p>
    <div class="pattern-filters" id="pattern-filters"></div>
    <div class="pattern-grid" id="pattern-grid"></div>
</div>

<div class="section-card motifs-section" id="motifs-section" style="display:none;">
    <h2 style="color:#e94560; font-size:1.2em; margin-bottom:6px;">Herkende Motieven</h2>
    <p style="color:#888; font-size:0.85em; margin-bottom:16px;">Terugkerende melodische patronen.</p>
    <div class="pattern-grid" id="motif-grid"></div>
</div>

<div class="timeline-container" id="melody-contour-section" style="display:none;">
    <div class="timeline-header"><h2>Melodie Contour</h2></div>
    <div style="color:#888; font-size:0.82em; margin-bottom:8px;" id="melody-stats"></div>
    <div class="timeline" id="contour-canvas" style="height:120px;"></div>
</div>

<div class="section-card" id="melody-empty" style="display:none;">
    <p id="melody-empty-msg" style="color:#888; text-align:center; padding:20px;"></p>
</div>

<div class="timeline-container">
    <div class="timeline-header"><h2>Tijdlijn</h2><span id="time-display" style="color:#888; font-size:0.85em;">0:00</span></div>
    <div class="timeline" id="timeline"></div>
    <div class="section-markers" id="section-markers"></div>
</div>

<div id="sections-container"></div>

<footer>Muzikale Improvisatiegids — Gegenereerd op {datetime.now().strftime('%d-%m-%Y %H:%M')}</footer>
</div>

<script>
const NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
const uniqueChords = {unique_chords_json};
const sectionsData = {sections_json};
const allChords = {all_chords_json};
const barsData = {bars_json};
const globalRoles = {global_roles_json};
const globalPhrases = {global_phrases_json};
const patterns = {patterns_json};
const patternCharacters = {pattern_chars_json};
const melodyData = {melody_json};
const duration = {round(duration, 2)};
const bpm = {bpm};
let transposeMode = 'bb'; // 'concert', 'bb', 'eb'
function getTransposeSemitones() {{ return transposeMode === 'bb' ? 2 : transposeMode === 'eb' ? 9 : 0; }}
let activePatternFilter = 'all';

const ROLE_INFO = {{
    chord_tone: {{ label: 'Chord tone', color: '#2ecc71' }},
    tension:    {{ label: 'Spanning',    color: '#3498db' }},
    approach:   {{ label: 'Approach',    color: '#f39c12' }},
    avoid:      {{ label: 'Avoid',       color: '#e74c3c' }},
    passing:    {{ label: 'Doorgang',    color: '#9b59b6' }},
}};

function noteDisplay(idx) {{ const s = getTransposeSemitones(); return NOTE_NAMES[(idx + s) % 12]; }}

function chordDisplay(s) {{
    const semi = getTransposeSemitones();
    if (semi === 0) return s;
    let root = s[0], rest = s.slice(1);
    if (rest.length > 0 && (rest[0]==='#'||rest[0]==='b')) {{ root += rest[0]; rest = rest.slice(1); }}
    const idx = NOTE_NAMES.indexOf(root);
    if (idx === -1) return s;
    return NOTE_NAMES[(idx + semi) % 12] + rest;
}}

function colorClass(q) {{
    if (q.includes('dim') || q.includes('o') || q.includes('ø')) return 'chord-color-dim';
    if (q.includes('m')) return 'chord-color-minor';
    if (q.includes('7') || q.includes('9') || q.includes('13')) return 'chord-color-dom';
    return 'chord-color-major';
}}

function fmt(s) {{ const m = Math.floor(s / 60); return m + ':' + String(Math.floor(s % 60)).padStart(2, '0'); }}

function buildTimeline() {{
    const tl = document.getElementById('timeline');
    tl.innerHTML = '';
    allChords.forEach(ch => {{
        const b = document.createElement('div');
        b.className = 'chord-block chord-color-' + (ch.quality.includes('dim')||ch.quality.includes('o')||ch.quality.includes('ø') ? 'dim' : ch.quality.includes('m') ? 'minor' : ch.quality.includes('7')||ch.quality.includes('9')||ch.quality.includes('13') ? 'dom' : 'major');
        b.style.left = (ch.start / duration) * 100 + '%';
        b.style.width = Math.max(((ch.end - ch.start) / duration) * 100, 0.5) + '%';
        b.textContent = chordDisplay(ch.chord);
        b.title = chordDisplay(ch.chord) + ' (' + fmt(ch.start) + ' — ' + fmt(ch.end) + ')';
        b.addEventListener('click', () => scrollToChord(ch.chord, ch.start));
        tl.appendChild(b);
    }});
    const sm = document.getElementById('section-markers');
    sm.innerHTML = '';
    sectionsData.forEach(sec => {{
        const m = document.createElement('div');
        m.className = 'section-marker';
        m.style.left = (sec.start / duration) * 100 + '%';
        m.style.width = Math.max(((sec.end - sec.start) / duration) * 100, 1) + '%';
        m.textContent = sec.name;
        sm.appendChild(m);
    }});
}}

function buildSections() {{
    const container = document.getElementById('sections-container');
    container.innerHTML = '';
    sectionsData.forEach((sec, si) => {{
        const card = document.createElement('div');
        card.className = 'section-card'; card.id = 'section-' + si;
        let hdr = '<div class="section-header"><div class="section-label">' + sec.name + '</div>';
        hdr += '<div class="section-time">' + fmt(sec.start) + ' — ' + fmt(sec.end);
        hdr += ' (' + Math.round((sec.end - sec.start) / (4 * 60 / bpm)) + ' maten)</div></div>';
        let ch_html = '<div class="section-chords">';
        sec.chords.forEach((ch, ci) => {{
            const q = ch.chord.replace(/^[A-G][#b]?/, '');
            const bars = Math.max(1, Math.round((ch.end - ch.start) / (4 * 60 / bpm)));
            ch_html += '<div class="section-chord ' + colorClass(q) + '" data-chord="' + ch.chord + '" data-section="' + si + '" onclick="showDetail(this)">';
            ch_html += chordDisplay(ch.chord) + '<span class="chord-dur">' + bars + (bars === 1 ? ' maat' : ' maten') + '</span></div>';
        }});
        ch_html += '</div>';
        card.innerHTML = hdr + ch_html + '<div class="chord-detail" id="detail-' + si + '"></div>';
        container.appendChild(card);
    }});
}}

function showDetail(el) {{
    const chordName = el.dataset.chord, si = el.dataset.section;
    const ch = uniqueChords[chordName];
    if (!ch) return;
    const panel = document.getElementById('detail-' + si);
    const wasActive = el.classList.contains('active');
    el.parentElement.querySelectorAll('.section-chord').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.chord-detail').forEach(d => {{ d.classList.remove('visible'); d.innerHTML = ''; }});
    if (wasActive) return;
    el.classList.add('active'); panel.classList.add('visible');
    let html = '<h2>' + chordDisplay(ch.chord) + '</h2>';
    html += '<div class="detail-grid"><div class="meta-card"><div class="label">Primaire toonladder</div><div class="value" style="font-size:1em;">' + ch.scale_primary + '</div></div>';
    if (ch.scale_alt) html += '<div class="meta-card"><div class="label">Alternatief</div><div class="value" style="font-size:1em;">' + ch.scale_alt + '</div></div>';
    html += '</div>';
    html += '<div class="tips-section"><h3>Trompettips</h3><ul>';
    ch.tips.forEach(t => {{ html += '<li>' + t + '</li>'; }});
    html += '</ul></div>';
    panel.innerHTML = html;
}}

function scrollToChord(chordName, startTime) {{
    for (let si = 0; si < sectionsData.length; si++) {{
        const sec = sectionsData[si];
        if (startTime >= sec.start && startTime <= sec.end) {{
            document.getElementById('section-' + si).scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            const els = document.querySelectorAll('#section-' + si + ' .section-chord');
            for (const el of els) {{ if (el.dataset.chord === chordName) {{ setTimeout(() => showDetail(el), 300); break; }} }}
            break;
        }}
    }}
}}

function buildGlobalNoteMap() {{
    const container = document.getElementById('global-notemap');
    container.innerHTML = '';
    for (let i = 0; i < 12; i++) {{
        const di = (i + getTransposeSemitones()) % 12;
        const role = globalRoles[String(i)] || 'passing';
        const rl = ROLE_INFO[role] ? ROLE_INFO[role].label : role;
        container.innerHTML += '<div class="note-cell ' + role + '"><span class="note-name">' + NOTE_NAMES[di] + '</span><span class="note-role">' + rl + '</span></div>';
    }}
    const pc = document.getElementById('global-phrases');
    let ph = '<h3 style="color:#3498db; margin: 12px 0 8px; font-size:0.95em;">Fraseersuggesties</h3>';
    globalPhrases.forEach(phrase => {{
        ph += '<div class="phrase-card"><h4>' + phrase.name + '</h4>';
        ph += '<p style="color:#ccc; font-size:0.85em;">' + phrase.description + '</p>';
        ph += '<div class="phrase-notes">';
        phrase.notes.forEach((ni, idx) => {{
            const role = globalRoles[String(ni)] || 'passing';
            if (idx > 0) ph += '<div class="phrase-arrow">→</div>';
            ph += '<div class="phrase-note ' + role + '">' + noteDisplay(ni) + '</div>';
        }});
        ph += '</div><p class="phrase-tip">' + phrase.tip + '</p></div>';
    }});
    pc.innerHTML = ph;
}}

function buildPatternFilters() {{
    const container = document.getElementById('pattern-filters');
    container.innerHTML = '';
    const allBtn = document.createElement('button');
    allBtn.className = 'pattern-filter-btn' + (activePatternFilter === 'all' ? ' active' : '');
    allBtn.textContent = 'Alles';
    allBtn.style.borderColor = activePatternFilter === 'all' ? '#e94560' : 'transparent';
    if (activePatternFilter === 'all') allBtn.style.background = 'rgba(233,69,96,0.2)';
    allBtn.onclick = () => {{ activePatternFilter = 'all'; buildPatternFilters(); buildPatternGrid(); }};
    container.appendChild(allBtn);
    const chars = []; const seen = new Set();
    patterns.forEach(p => {{ if (!seen.has(p.character)) {{ seen.add(p.character); chars.push({{ key: p.character, label: p.character_label, icon: p.character_icon, color: p.character_color }}); }} }});
    chars.forEach(ch => {{
        const btn = document.createElement('button');
        const isActive = activePatternFilter === ch.key;
        btn.className = 'pattern-filter-btn' + (isActive ? ' active' : '');
        btn.textContent = ch.icon + ' ' + ch.label;
        btn.style.borderColor = isActive ? ch.color : 'transparent';
        if (isActive) btn.style.background = ch.color + '33';
        btn.onclick = () => {{ activePatternFilter = ch.key; buildPatternFilters(); buildPatternGrid(); }};
        container.appendChild(btn);
    }});
}}

function buildPatternGrid() {{
    const container = document.getElementById('pattern-grid');
    container.innerHTML = '';
    const filtered = activePatternFilter === 'all' ? patterns : patterns.filter(p => p.character === activePatternFilter);
    const dirLabels = {{ up: '\u2191 stijgend', down: '\u2193 dalend', mixed: '\u2195 gemengd' }};
    filtered.forEach(pattern => {{
        const card = document.createElement('div');
        card.className = 'pattern-card';
        const accent = document.createElement('div');
        accent.className = 'pattern-accent';
        accent.style.background = pattern.character_color;
        card.appendChild(accent);
        const header = document.createElement('div');
        header.className = 'pattern-header';
        header.innerHTML = '<span class="pattern-icon">' + pattern.character_icon + '</span><span class="pattern-name">' + pattern.name + '</span><span class="pattern-direction">' + (dirLabels[pattern.direction] || pattern.direction) + '</span>';
        card.appendChild(header);
        const badge = document.createElement('div');
        badge.className = 'pattern-character-badge';
        badge.style.background = pattern.character_color + '22';
        badge.style.color = pattern.character_color;
        badge.textContent = pattern.character_label;
        card.appendChild(badge);
        const desc = document.createElement('div');
        desc.className = 'pattern-desc';
        desc.textContent = pattern.description;
        card.appendChild(desc);
        const notesRow = document.createElement('div');
        notesRow.className = 'pattern-notes-row';
        pattern.notes.forEach((note, idx) => {{
            if (idx > 0) {{
                const prevIv = pattern.notes[idx - 1].interval;
                const arrow = document.createElement('span');
                if (note.interval > prevIv) {{ arrow.className = 'pattern-arrow-up'; arrow.textContent = '\u2197'; }}
                else if (note.interval < prevIv) {{ arrow.className = 'pattern-arrow-down'; arrow.textContent = '\u2198'; }}
                else {{ arrow.className = 'pattern-arrow-same'; arrow.textContent = '\u2192'; }}
                notesRow.appendChild(arrow);
            }}
            const noteEl = document.createElement('div');
            noteEl.className = 'pattern-note ' + note.role;
            noteEl.textContent = NOTE_NAMES[(note.index + getTransposeSemitones()) % 12];
            notesRow.appendChild(noteEl);
        }});
        card.appendChild(notesRow);
        const tip = document.createElement('div');
        tip.className = 'pattern-tip';
        tip.textContent = '\U0001f4a1 ' + pattern.tip;
        card.appendChild(tip);
        container.appendChild(card);
    }});
}}

function buildMelodyContour() {{
    if (!melodyData || !melodyData.notes || melodyData.notes.length === 0) {{
        document.getElementById('melody-contour-section').style.display = 'none';
        document.getElementById('motifs-section').style.display = 'none';
        const emptyEl = document.getElementById('melody-empty');
        const emptyMsg = document.getElementById('melody-empty-msg');
        if (melodyData === null) {{
            emptyEl.style.display = 'block';
            emptyMsg.textContent = 'Geen melodiedata beschikbaar.';
        }} else {{
            emptyEl.style.display = 'block';
            emptyMsg.textContent = 'Geen duidelijke melodie gedetecteerd.';
        }}
        return;
    }}
    document.getElementById('melody-empty').style.display = 'none';
    document.getElementById('melody-contour-section').style.display = 'block';
    const stats = melodyData.stats;
    const statsEl = document.getElementById('melody-stats');
    let sh = '<strong>' + stats.total_notes + '</strong> noten | <strong>' + stats.total_phrases + '</strong> frases | <strong>' + stats.total_motifs + '</strong> motieven';
    if (stats.most_common_note) sh += ' | Meest: <strong>' + noteDisplay(NOTE_NAMES.indexOf(stats.most_common_note)) + '</strong>';
    statsEl.innerHTML = sh;
    const canvas = document.getElementById('contour-canvas');
    canvas.innerHTML = '';
    const notes = melodyData.notes;
    const midiVals = notes.map(n => n.midi);
    const minM = Math.min(...midiVals) - 2, maxM = Math.max(...midiVals) + 2;
    const mR = maxM - minM || 1;
    const cH = 120;
    const RC = {{ chord_tone: '#2ecc71', tension: '#3498db', approach: '#f39c12', avoid: '#e74c3c', passing: '#9b59b6' }};
    for (let i = 1; i < notes.length; i++) {{
        if (notes[i].start - notes[i-1].end > 1.0) continue;
        const x1 = (notes[i-1].start / duration) * 100;
        const y1 = ((maxM - notes[i-1].midi) / mR) * (cH - 16) + 8;
        const x2 = (notes[i].start / duration) * 100;
        const y2 = ((maxM - notes[i].midi) / mR) * (cH - 16) + 8;
        const line = document.createElement('div');
        line.style.cssText = 'position:absolute;height:1px;transform-origin:left center;z-index:1;opacity:0.4;background:#555;';
        const dx = (x2 - x1) * (canvas.offsetWidth || 800) / 100;
        const dy = y2 - y1;
        line.style.left = x1 + '%';
        line.style.top = y1 + 'px';
        line.style.width = Math.sqrt(dx*dx+dy*dy) + 'px';
        line.style.transform = 'rotate(' + Math.atan2(dy,dx)*180/Math.PI + 'deg)';
        canvas.appendChild(line);
    }}
    notes.forEach(note => {{
        const x = (note.start / duration) * 100;
        const y = ((maxM - note.midi) / mR) * (cH - 16) + 8;
        const dot = document.createElement('div');
        dot.style.cssText = 'position:absolute;width:8px;height:8px;border-radius:50%;transform:translate(-50%,-50%);z-index:2;';
        dot.style.left = x + '%';
        dot.style.top = y + 'px';
        dot.style.background = RC[note.role] || '#888';
        canvas.appendChild(dot);
    }});
}}

function buildMotifCards() {{
    if (!melodyData || !melodyData.motifs || melodyData.motifs.length === 0) {{
        document.getElementById('motifs-section').style.display = 'none';
        return;
    }}
    document.getElementById('motifs-section').style.display = 'block';
    const grid = document.getElementById('motif-grid');
    grid.innerHTML = '';
    melodyData.motifs.forEach(motif => {{
        const card = document.createElement('div');
        card.className = 'pattern-card';
        let html = '<div style="position:absolute;top:0;left:0;right:0;height:3px;background:#e94560;border-radius:12px 12px 0 0;"></div>';
        html += '<div style="display:flex;align-items:center;gap:10px;margin:4px 0 8px;"><span style="font-weight:700;color:#fff;">' + motif.name + '</span>';
        html += '<span style="font-size:0.7em;font-weight:600;padding:2px 10px;border-radius:12px;background:rgba(233,69,96,0.2);color:#e94560;">' + motif.occurrence_count + '\u00d7</span></div>';
        const contourIcons = motif.contour_summary.split('-').map(d => d==='up'?'\u2191':d==='down'?'\u2193':'\u2192').join(' ');
        html += '<div style="font-size:0.75em;color:#888;margin-bottom:8px;">Contour: ' + contourIcons + '</div>';
        html += '<div class="pattern-notes-row">';
        const exN = motif.example_notes || [];
        function mnd(n) {{ const i = NOTE_NAMES.indexOf(n); return i >= 0 ? noteDisplay(i) : (n || '?'); }}
        html += '<div class="pattern-note tension">' + (exN.length > 0 ? mnd(exN[0]) : '\u25cf') + '</div>';
        motif.intervals.forEach((iv, idx) => {{
            html += '<span style="font-size:0.65em;color:#888;margin:0 2px;">' + (iv>0?'+':'') + iv + '</span>';
            html += '<div class="pattern-note ' + (Math.abs(iv)<=2?'tension':Math.abs(iv)<=5?'approach':'passing') + '">' + (exN.length > idx+1 ? mnd(exN[idx+1]) : '\u25cf') + '</div>';
        }});
        html += '</div>';
        if (motif.occurrences) {{
            const times = motif.occurrences.map(o => fmt(o.start)).join(', ');
            html += '<div style="font-size:0.78em;color:#aaa;">Gevonden bij: <strong style="color:#e94560;">' + times + '</strong></div>';
        }}
        card.innerHTML = html;
        grid.appendChild(card);
    }});
}}

document.getElementById('transpose-select').addEventListener('change', function() {{
    transposeMode = this.value;
    buildGlobalNoteMap(); buildTimeline(); buildSections(); buildPatternGrid();
    buildMelodyContour(); buildMotifCards();
}});

buildGlobalNoteMap(); buildTimeline(); buildSections();
buildPatternFilters(); buildPatternGrid();
buildMelodyContour(); buildMotifCards();
</script>
</body>
</html>"""
    return html


def generate_markdown(track_name, analysis_data):
    """Generate a Markdown improvisation guide."""
    d = _prepare_template_data(track_name, analysis_data)
    lines = []

    lines.append(f"# Improvisatiegids: {track_name}\n")

    # Overview
    lines.append("## Overzicht\n")
    lines.append(f"| | |")
    lines.append(f"|---|---|")
    lines.append(f"| **Toonsoort (Concert)** | {d['key']} {d['mode_nl']} ({round(d['key_confidence'] * 100)}%) |")
    lines.append(f"| **Toonsoort (Bb Trompet)** | {d['bb_key']} {d['mode_nl']} |")
    lines.append(f"| **Toonsoort (Eb Alt Sax)** | {d['eb_key']} {d['mode_nl']} |")
    lines.append(f"| **Tempo** | {d['bpm']} BPM |")
    dur = d['duration']
    lines.append(f"| **Duur** | {int(dur // 60)}:{int(dur % 60):02d} |")
    lines.append(f"| **Secties** | {len(d['sections_data'])} |")
    lines.append(f"| **Unieke akkoorden** | {len(d['unique_chords'])} |")
    lines.append("")

    # Global chromatic note map
    lines.append("## Chromatische nootkaart\n")
    role_labels = {'chord_tone': 'CT', 'tension': 'T', 'approach': 'A', 'avoid': 'X', 'passing': 'D'}
    header_notes = []
    header_roles = []
    for i in range(12):
        note = NOTE_NAMES[i]
        role = d['global_note_roles'].get(i, 'passing')
        header_notes.append(f" {note:>3} ")
        header_roles.append(f" {role_labels.get(role, '?'):>3} ")
    lines.append("|" + "|".join(header_notes) + "|")
    lines.append("|" + "|".join(["----"] * 12) + "|")
    lines.append("|" + "|".join(header_roles) + "|")
    lines.append("")
    lines.append("CT = Chord tone, T = Spanning, A = Approach, X = Avoid, D = Doorgang\n")

    # Global phrase suggestions
    lines.append("## Fraseersuggesties\n")
    for phrase in d['global_phrases']:
        note_names = [index_to_note(n) for n in phrase['notes']]
        lines.append(f"### {phrase['name']}")
        lines.append(f"{phrase['description']}")
        lines.append(f"*{phrase['tip']}*\n")

    # Deep House Patterns
    lines.append("## Deep House Patronen\n")
    lines.append("Intervalmotieven als bouwstenen voor improvisatie.\n")

    # Group patterns by character
    from collections import OrderedDict
    char_groups = OrderedDict()
    for pattern in d['patterns']:
        ch = pattern['character']
        if ch not in char_groups:
            char_groups[ch] = []
        char_groups[ch].append(pattern)

    for char_key, char_patterns in char_groups.items():
        char_info = d['pattern_characters'].get(char_key, {})
        lines.append(f"### {char_info.get('icon', '')} {char_info.get('label', char_key)} — {char_info.get('description', '')}\n")

        for pattern in char_patterns:
            dir_labels = {'up': '↑', 'down': '↓', 'mixed': '↕'}
            dir_str = dir_labels.get(pattern['direction'], '')
            note_names = [n['name'] for n in pattern['notes']]
            lines.append(f"**{pattern['name']}** {dir_str}")
            lines.append(f"  {' → '.join(note_names)}")
            lines.append(f"  {pattern['description']}")
            lines.append(f"  *{pattern['tip']}*\n")

    # Melody & Motifs
    melody = d.get('melody')
    if melody and melody.get('motifs'):
        lines.append("## Melodie & Motieven\n")
        stats = melody.get('stats', {})
        lines.append(f"- **Gedetecteerde noten:** {stats.get('total_notes', 0)}")
        lines.append(f"- **Frases:** {stats.get('total_phrases', 0)}")
        lines.append(f"- **Motieven:** {stats.get('total_motifs', 0)}")
        pr = stats.get('pitch_range')
        if pr:
            lines.append(f"- **Bereik:** {pr.get('low_name', '?')} — {pr.get('high_name', '?')}")
        if stats.get('most_common_note'):
            lines.append(f"- **Meest voorkomend:** {stats['most_common_note']}")
        lines.append("")

        for motif in melody['motifs']:
            contour_icons = ' '.join('↑' if d == 'up' else '↓' if d == 'down' else '→' for d in motif['contour_summary'].split('-'))
            iv_str = ' '.join(('+' if iv > 0 else '') + str(iv) for iv in motif['intervals'])
            lines.append(f"### {motif['name']} ({motif['occurrence_count']}× herhaald)")
            lines.append(f"- Intervallen: `{iv_str}`")
            lines.append(f"- Contour: {contour_icons}")
            times = ', '.join(_fmt_time(o['start']) for o in motif.get('occurrences', []))
            lines.append(f"- Gevonden bij: {times}")
            lines.append("")

    # Sections & chords
    lines.append("## Structuur & Akkoorden\n")
    for sec in d['sections_data']:
        dur_sec = sec['end'] - sec['start']
        approx_bars = round(dur_sec / (4 * 60 / d['bpm']))
        lines.append(f"### {sec['name']} ({_fmt_time(sec['start'])} — {_fmt_time(sec['end'])}, {approx_bars} maten)\n")

        for ch in sec['chords']:
            chord_str = ch['chord']
            ch_data = d['unique_chords'].get(chord_str, {})
            bars = max(1, round((ch['end'] - ch['start']) / (4 * 60 / d['bpm'])))
            lines.append(f"**{chord_str}** ({bars} {'maat' if bars == 1 else 'maten'})")
            if ch_data:
                lines.append(f"- Toonladder: {ch_data.get('scale_primary', '?')}")
                if ch_data.get('scale_alt'):
                    lines.append(f"- Alternatief: {ch_data['scale_alt']}")
                for tip in ch_data.get('tips', []):
                    lines.append(f"- {tip}")
            lines.append("")

    lines.append(f"\n---\n*Gegenereerd op {datetime.now().strftime('%d-%m-%Y %H:%M')}*")
    return "\n".join(lines)


def _fmt_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"
