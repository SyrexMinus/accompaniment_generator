from typing import Dict

from app_config import ENABLE_EMPTY_ACCOMPANIMENT, ENABLE_MISSING_ACCOMP_FOR_MELODY_TICK, \
    ENABLE_EXCESS_ACCOMP_TICK_FOR_MELODY, ENABLE_TOO_BIG_CHORD_DROP, TOO_BIG_CHORD_DROP_IN_NOTES, \
    ENABLE_ACCOMP_TICK_NOT_BELOW_MELODY, ENABLE_DISSONANCE_INSIDE, EVENT_TO_AWARD_WEIGHTS, \
    ENABLE_ACCOMPANIMENT_CHORD_EXISTS, ENABLE_TOO_WIDE_ACCOMPANIMENT_RANGE, TOO_WIDE_ACCOMPANIMENT_RANGE_IN_NOTES, \
    ENABLE_CORRECT_TRIAD_FOR_MELODY_KEY, ALLOWED_ACCOMP_TRIADS_FOR_MELODY_TONIC, ENABLE_CHORD_INCLUDE_MELODY_NOTE, \
    ENABLE_PARTIAL_PROGRESSION, ENABLE_COMPLETED_PROGRESSION, ENABLE_TOO_LOW_CHORD, TOO_LOW_NOTE_UPPER_BOUND
from music_interfaces.composition.composition import Composition
from genetic_algorithm.fitness_function.fitness_constants import MISSING_ACCOMP_FOR_MELODY_TICK, \
    EXCESS_ACCOMP_TICK_FOR_MELODY, TOO_BIG_CHORD_DROP, ACCOMP_TICK_NOT_BELOW_MELODY, DISSONANCE_INSIDE, \
    EMPTY_ACCOMPANIMENT, DISSONANCE_WITH_MELODY, ACCOMPANIMENT_CHORD_EXISTS, TOO_WIDE_ACCOMPANIMENT_RANGE, \
    CORRECT_TRIAD_FOR_MELODY_KEY, CHORD_INCLUDE_MELODY_NOTE, COMPLETED_PROGRESSION, PARTIAL_PROGRESSION, TOO_LOW_CHORD
from music_interfaces.composition.composition_constants import PROGRESSIONS


def fitness_function(melody: Composition, accompaniment: Composition) -> float:
    """Less fitness means better accompaniment"""
    metrics = calculate_metrics(melody, accompaniment)
    return _event_to_award(metrics)


def calculate_metrics(melody: Composition, accompaniment: Composition) -> Dict[str, float]:
    metrics = {
        MISSING_ACCOMP_FOR_MELODY_TICK: 0,
        EXCESS_ACCOMP_TICK_FOR_MELODY: 0,
        TOO_BIG_CHORD_DROP: 0,
        ACCOMP_TICK_NOT_BELOW_MELODY: 0,
        DISSONANCE_INSIDE: 0,
        EMPTY_ACCOMPANIMENT: 0,  # accompaniment level metric
        DISSONANCE_WITH_MELODY: 0,
        ACCOMPANIMENT_CHORD_EXISTS: 0,
        TOO_WIDE_ACCOMPANIMENT_RANGE: 0,
        CORRECT_TRIAD_FOR_MELODY_KEY: 0,
        CHORD_INCLUDE_MELODY_NOTE: 0,
        COMPLETED_PROGRESSION: 0,
        PARTIAL_PROGRESSION: 0,
        TOO_LOW_CHORD: 0
    }
    m_notes_at = melody.notes_at
    a_notes_at = accompaniment.notes_at
    m_key_tonic, m_key_scale = melody.key
    allowed_triads = []
    for triad in ALLOWED_ACCOMP_TRIADS_FOR_MELODY_TONIC[m_key_scale]:
        min_note = triad[0]
        octave_shift = ((m_key_tonic + min_note) // 12) * 12
        allowed_triads.append([m_key_tonic + note - octave_shift for note in triad])

    # preprocess inputs
    for time, notes in m_notes_at.items():
        m_notes_at[time] = sorted(notes, key=lambda note: note.note)
    for time, notes in a_notes_at.items():
        a_notes_at[time] = sorted(notes, key=lambda note: note.note)

    # calculate metrics
    if ENABLE_ACCOMPANIMENT_CHORD_EXISTS:
        metrics[ACCOMPANIMENT_CHORD_EXISTS] += len(a_notes_at)
    if ENABLE_EMPTY_ACCOMPANIMENT:
        if len(m_notes_at) == 0:
            metrics[EMPTY_ACCOMPANIMENT] += 1
    if ENABLE_MISSING_ACCOMP_FOR_MELODY_TICK:
        for m_time in m_notes_at.keys():
            if a_notes_at.get(m_time) is None:
                metrics[MISSING_ACCOMP_FOR_MELODY_TICK] += 1
    if ENABLE_EXCESS_ACCOMP_TICK_FOR_MELODY:
        for a_time in a_notes_at.keys():
            if m_notes_at.get(a_time) is None:
                metrics[EXCESS_ACCOMP_TICK_FOR_MELODY] += 1
    if ENABLE_PARTIAL_PROGRESSION or ENABLE_COMPLETED_PROGRESSION:
        triad_names_by_beats = accompaniment.triad_names_by_beats
        progression_len = 4
        for i_four_beats in range(0, len(triad_names_by_beats) - progression_len + 1, progression_len):
            done_partial_max = 0
            for progression in PROGRESSIONS:
                done_partial = 0
                prev_min_chord_note = triad_names_by_beats[i_four_beats][0]
                for i in range(4):
                    delta_note = triad_names_by_beats[i_four_beats + i][0] - prev_min_chord_note
                    triad = triad_names_by_beats[i_four_beats + i][1]
                    done_partial += 1 if (delta_note, triad) == progression[i] else 0
                done_partial_max = max(done_partial_max, done_partial)
                if done_partial_max == 4:
                    if ENABLE_COMPLETED_PROGRESSION:
                        metrics[COMPLETED_PROGRESSION] += 1
                    break
            if ENABLE_PARTIAL_PROGRESSION:
                metrics[PARTIAL_PROGRESSION] += done_partial_max / progression_len
    if len(a_notes_at) > 0:
        prev_max_chord_note = None
        prev_min_chord_note = None
        min_min_chord_note = None
        max_min_chord_note = None
        low_notes_sum = 0
        for a_time in sorted(a_notes_at.keys()):
            min_chord_note = a_notes_at[a_time][0].note
            max_chord_note = a_notes_at[a_time][-1].note
            a_notes_as_numbers = [note.note for note in a_notes_at[a_time]]
            low_notes_sum += min_chord_note
            if ENABLE_TOO_LOW_CHORD:
                if min_chord_note <= TOO_LOW_NOTE_UPPER_BOUND:
                    metrics[TOO_LOW_CHORD] += 1
            if ENABLE_CHORD_INCLUDE_MELODY_NOTE:
                melody_notes_included = 0
                a_notes_as_chord_numbers = [note % 12 for note in a_notes_as_numbers]
                m_notes_in_bucket = melody.notes_by_buckets.get(a_time, [])
                for m_note in m_notes_in_bucket:
                    if m_note.note % 12 in a_notes_as_chord_numbers:
                        melody_notes_included += 1
                if len(m_notes_in_bucket) > 0:
                    metrics[CHORD_INCLUDE_MELODY_NOTE] += melody_notes_included / len(m_notes_in_bucket)
            if ENABLE_CORRECT_TRIAD_FOR_MELODY_KEY:
                octave_note = (min_chord_note // 12) * 12
                if [note.note - octave_note for note in a_notes_at[a_time]] in allowed_triads:
                    metrics[CORRECT_TRIAD_FOR_MELODY_KEY] += 1
            if min_min_chord_note is None or a_notes_at[a_time][0].note < min_min_chord_note:
                min_min_chord_note = a_notes_at[a_time][0].note
            if max_min_chord_note is None or a_notes_at[a_time][0].note > max_min_chord_note:
                max_min_chord_note = a_notes_at[a_time][0].note
            if ENABLE_TOO_BIG_CHORD_DROP and (
                    (prev_max_chord_note is not None and
                     abs(max_chord_note - prev_max_chord_note) >= TOO_BIG_CHORD_DROP_IN_NOTES) or
                    (prev_min_chord_note is not None and
                     abs(prev_min_chord_note - min_chord_note) >= TOO_BIG_CHORD_DROP_IN_NOTES)
            ):
                metrics[TOO_BIG_CHORD_DROP] += 1
            if ENABLE_ACCOMP_TICK_NOT_BELOW_MELODY:
                if m_notes_at.get(a_time) is not None:
                    m_min_chord_note = m_notes_at[a_time][0].note
                    if m_min_chord_note <= max_chord_note:
                        metrics[ACCOMP_TICK_NOT_BELOW_MELODY] += 1
            for i1 in range(len(a_notes_at[a_time])):
                # if ENABLE_DISSONANCE_WITH_MELODY:
                #     pass  # TODO
                if ENABLE_DISSONANCE_INSIDE:
                    # includes septimes, seconds, tritons https://ru.wikipedia.org/wiki/Консонанс_и_диссонанс
                    for i2 in range(i1 + 1, len(a_notes_at[a_time])):
                        note1 = a_notes_at[a_time][i1]
                        note2 = a_notes_at[a_time][i2]
                        note1_num = note1.note % 12
                        note2_num = note2.note % 12
                        if abs(note1_num - note2_num) == 11:  # septima (big septima)
                            metrics[DISSONANCE_INSIDE] += 1
                        # elif abs(note1_num - note2_num) == 10:  # small septima
                        #     metrics[DISSONANCE_INSIDE] += 1
                        # elif abs(note1_num - note2_num) == 12:  # increased septima
                        #     metrics[DISSONANCE_INSIDE] += 1
                        # elif abs(note1_num - note2_num) == 9:  # diminished septima
                        #     metrics[DISSONANCE_INSIDE] += 1
                        elif abs(note1_num - note2_num) == 2:  # second (big second)
                            metrics[DISSONANCE_INSIDE] += 1
                        # elif abs(note1_num - note2_num) == 1:  # small second
                        #     metrics[DISSONANCE_INSIDE] += 1
                        # elif abs(note1_num - note2_num) == 3:  # increased second
                        #     metrics[DISSONANCE_INSIDE] += 1
                        # elif abs(note1_num - note2_num) == 2:  # big second
                        #     metrics[DISSONANCE_INSIDE] += 1
                        elif abs(note1_num - note2_num) == 6:  # triton
                            metrics[DISSONANCE_INSIDE] += 1
            prev_max_chord_note = max_chord_note
            prev_min_chord_note = min_chord_note
        low_notes_median = low_notes_sum / len(a_notes_at)
        for a_time in sorted(a_notes_at.keys()):
            min_chord_note = a_notes_at[a_time][0].note
            if ENABLE_TOO_WIDE_ACCOMPANIMENT_RANGE:
                if abs(min_chord_note - low_notes_median) > TOO_WIDE_ACCOMPANIMENT_RANGE_IN_NOTES / 2:
                    metrics[TOO_WIDE_ACCOMPANIMENT_RANGE] += 1

    return metrics


def _event_to_award(metrics: Dict[str, float]) -> float:
    award = 0
    weights = EVENT_TO_AWARD_WEIGHTS
    for metric, count in metrics.items():
        if metric not in weights:
            print(f"WARNING: metric {metric} is not in weights")
        award += weights.get(metric, 0) * count
    return award
