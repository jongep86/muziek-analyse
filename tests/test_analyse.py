"""Tests voor analyse.py — muziektheorie helpers."""

import pytest
from analyse import (
    note_to_index, index_to_note, transpose_for_bb, transpose_for_eb,
    get_chord_tones, get_chord_quality, get_scale_for_chord,
    classify_notes_for_key, classify_notes_for_chord,
    generate_phrase_suggestions, get_trumpet_tips,
    parse_filename_metadata, NOTE_NAMES, ENHARMONIC, SCALES,
)


class TestNoteConversion:
    def test_note_to_index_basic(self):
        assert note_to_index('C') == 0
        assert note_to_index('A') == 9
        assert note_to_index('B') == 11

    def test_note_to_index_sharps(self):
        assert note_to_index('C#') == 1
        assert note_to_index('F#') == 6

    def test_note_to_index_enharmonic(self):
        assert note_to_index('Db') == note_to_index('C#')
        assert note_to_index('Eb') == note_to_index('D#')
        assert note_to_index('Bb') == note_to_index('A#')
        assert note_to_index('Gb') == note_to_index('F#')
        assert note_to_index('Ab') == note_to_index('G#')

    def test_note_to_index_special_enharmonic(self):
        assert note_to_index('E#') == note_to_index('F')
        assert note_to_index('B#') == note_to_index('C')
        assert note_to_index('Cb') == note_to_index('B')
        assert note_to_index('Fb') == note_to_index('E')

    def test_index_to_note(self):
        assert index_to_note(0) == 'C'
        assert index_to_note(9) == 'A'
        assert index_to_note(12) == 'C'  # wraps around
        assert index_to_note(14) == 'D'

    def test_roundtrip(self):
        for i, name in enumerate(NOTE_NAMES):
            assert note_to_index(index_to_note(i)) == i


class TestTranspose:
    def test_transpose_bb(self):
        # Bb trumpet: concert C sounds as D (+2)
        assert transpose_for_bb(0) == 2
        assert transpose_for_bb(10) == 0  # concert Bb -> C

    def test_transpose_eb(self):
        # Eb alto sax: concert C sounds as A (+9)
        assert transpose_for_eb(0) == 9
        assert transpose_for_eb(3) == 0  # concert Eb -> C


class TestChordParsing:
    def test_get_chord_quality(self):
        assert get_chord_quality('Cm7') == 'm7'
        assert get_chord_quality('F#maj7') == 'maj7'
        assert get_chord_quality('G7') == '7'
        assert get_chord_quality('D') == ''
        assert get_chord_quality('Bbm7b5') == 'm7b5'

    def test_get_chord_tones_basic(self):
        tones = get_chord_tones('C')
        assert 0 in tones  # C
        assert 4 in tones  # E
        assert 7 in tones  # G

    def test_get_chord_tones_minor(self):
        tones = get_chord_tones('Am')
        assert 9 in tones   # A
        assert 0 in tones   # C
        assert 4 in tones   # E

    def test_get_chord_tones_invalid_fallback(self):
        # Invalid chord should at least return the root
        tones = get_chord_tones('Xzz')
        assert isinstance(tones, list)
        assert len(tones) >= 1

    def test_get_scale_for_chord(self):
        result = get_scale_for_chord('Cm7')
        assert result['primary'] == 'Dorisch'

        result = get_scale_for_chord('Fmaj7')
        assert result['primary'] == 'Lydisch'

        result = get_scale_for_chord('G7')
        assert result['primary'] == 'Mixolydisch'

        result = get_scale_for_chord('Bm7b5')
        assert result['primary'] == 'Locrisch'


class TestClassifyNotes:
    def test_classify_for_key_major(self):
        roles = classify_notes_for_key('C', 'major')
        # Tonic chord tones (Cmaj7: C, E, G, B)
        assert roles[0] == 'chord_tone'   # C
        assert roles[4] == 'chord_tone'   # E
        assert roles[7] == 'chord_tone'   # G
        assert roles[11] == 'chord_tone'  # B

    def test_classify_for_key_minor(self):
        roles = classify_notes_for_key('A', 'minor')
        # Tonic chord tones (Am7: A, C, E, G)
        assert roles[9] == 'chord_tone'   # A
        assert roles[0] == 'chord_tone'   # C
        assert roles[4] == 'chord_tone'   # E
        assert roles[7] == 'chord_tone'   # G

    def test_classify_all_12_notes_covered(self):
        roles = classify_notes_for_key('C', 'major')
        assert len(roles) == 12
        for i in range(12):
            assert i in roles
            assert roles[i] in ('chord_tone', 'tension', 'approach', 'passing', 'avoid')

    def test_classify_for_chord(self):
        roles = classify_notes_for_chord('Cm7')
        # C, Eb, G, Bb are chord tones
        assert roles[0] == 'chord_tone'   # C
        assert roles[3] == 'chord_tone'   # Eb
        assert roles[7] == 'chord_tone'   # G
        assert roles[10] == 'chord_tone'  # Bb
        assert len(roles) == 12


class TestPhraseSuggestions:
    def test_generates_suggestions(self):
        suggestions = generate_phrase_suggestions('Cm7', 'Dorisch', 0)
        assert len(suggestions) >= 2
        names = [s['name'] for s in suggestions]
        assert 'Arpeggio' in names

    def test_suggestion_has_required_fields(self):
        suggestions = generate_phrase_suggestions('G7', 'Mixolydisch', 7)
        for s in suggestions:
            assert 'name' in s
            assert 'notes' in s
            assert 'description' in s


class TestTrumpetTips:
    def test_dominant_tips(self):
        tips = get_trumpet_tips('G7', '7')
        assert len(tips) >= 3
        assert any('dominant' in t.lower() or 'Dominant' in t for t in tips)

    def test_minor_tips(self):
        tips = get_trumpet_tips('Am7', 'm7')
        assert any('mineur' in t.lower() or 'Mineur' in t for t in tips)

    def test_major_tips(self):
        tips = get_trumpet_tips('Cmaj7', 'maj7')
        assert any('majeur' in t.lower() or 'Majeur' in t or 'Lydisch' in t for t in tips)


class TestParseFilenameMetadata:
    def test_key_and_bpm(self):
        # Format: "- Am - 120 -" or "- Am - 120"
        meta = parse_filename_metadata('Track Name - Am - 120.mp3')
        assert meta.get('key') == 'A'
        assert meta.get('mode') == 'minor'
        assert meta.get('bpm') == 120

    def test_major_key(self):
        meta = parse_filename_metadata('Song - C - 128.mp3')
        assert meta.get('key') == 'C'
        assert meta.get('mode') == 'major'
        assert meta.get('bpm') == 128

    def test_no_metadata(self):
        meta = parse_filename_metadata('random_song.mp3')
        assert isinstance(meta, dict)
        assert 'key' not in meta

    def test_bpm_between_dashes(self):
        meta = parse_filename_metadata('Track - 125 - remix.mp3')
        assert meta.get('bpm') == 125

    def test_key_only(self):
        meta = parse_filename_metadata('01 Artist - Title - Cm - stuff.mp3')
        assert meta.get('key') == 'C'
        assert meta.get('mode') == 'minor'

    def test_sharp_key(self):
        meta = parse_filename_metadata('Track - F# - 130.mp3')
        assert meta.get('key') == 'F#'
        assert meta.get('mode') == 'major'

    def test_flat_key(self):
        meta = parse_filename_metadata('Track - Bbm - 122.mp3')
        assert meta.get('key') == 'Bb'
        assert meta.get('mode') == 'minor'


class TestScaleDefinitions:
    def test_major_scale_intervals(self):
        assert SCALES['Ionisch (Majeur)'] == [0, 2, 4, 5, 7, 9, 11]

    def test_minor_scale_intervals(self):
        assert SCALES['Aeolisch (Mineur)'] == [0, 2, 3, 5, 7, 8, 10]

    def test_all_scales_start_at_zero(self):
        for name, intervals in SCALES.items():
            assert intervals[0] == 0, f'{name} does not start at 0'

    def test_all_scales_sorted(self):
        for name, intervals in SCALES.items():
            assert intervals == sorted(intervals), f'{name} is not sorted'

    def test_all_intervals_in_range(self):
        for name, intervals in SCALES.items():
            for iv in intervals:
                assert 0 <= iv <= 11, f'{name} has interval {iv} out of range'
