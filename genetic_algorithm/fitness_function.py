from typing import Dict

from composition.composition import Composition

ENABLE_MISSING_ACCOMP_FOR_MELODY_TICK = True
MISSING_ACCOMP_FOR_MELODY_TICK = "missing_accompaniment_for_melody_tick"
ENABLE_EXCESS_ACCOMP_TICK_FOR_MELODY = True
EXCESS_ACCOMP_TICK_FOR_MELODY = "excessive_accompaniment_tick_for_melody"
ENABLE_TOO_BIG_CHORD_DROP = True
TOO_BIG_CHORD_DROP = "too_big_chord_drop"
TOO_BIG_CHORD_DROP_IN_NOTES = 8
ENABLE_ACCOMP_TICK_NOT_BELOW_MELODY = True
ACCOMP_TICK_NOT_BELOW_MELODY = "accompaniment_tick_is_not_below_melody"
ENABLE_DISSONANCE_INSIDE = True
DISSONANCE_INSIDE = "dissonance_inside"
ENABLE_DISSONANCE_WITH_MELODY = True
DISSONANCE_WITH_MELODY = "dissonance_with_melody"
ENABLE_EMPTY_ACCOMPANIMENT = True
EMPTY_ACCOMPANIMENT = "empty_accompaniment"
EVENT_TO_AWARD_WEIGHTS = {
    MISSING_ACCOMP_FOR_MELODY_TICK: -1,
    EXCESS_ACCOMP_TICK_FOR_MELODY: -10,
    TOO_BIG_CHORD_DROP: -20,
    ACCOMP_TICK_NOT_BELOW_MELODY: -5,
    DISSONANCE_INSIDE: -3,
    EMPTY_ACCOMPANIMENT: -1000
}


def fitness_function(melody: Composition, accompaniment: Composition) -> float:
    metrics = _calculate_metrics(melody, accompaniment)
    return _event_to_award(metrics)


def _calculate_metrics(melody: Composition, accompaniment: Composition) -> Dict[str, int]:
    metrics = {
        MISSING_ACCOMP_FOR_MELODY_TICK: 0,
        EXCESS_ACCOMP_TICK_FOR_MELODY: 0,
        TOO_BIG_CHORD_DROP: 0,
        ACCOMP_TICK_NOT_BELOW_MELODY: 0,
        DISSONANCE_INSIDE: 0,
        EMPTY_ACCOMPANIMENT: 0
    }  # TODO add anti-metrics
    m_notes_at = melody.notes_at
    a_notes_at = accompaniment.notes_at

    # preprocess inputs
    for time, notes in m_notes_at.items():
        m_notes_at[time] = sorted(notes, key=lambda note: note.note)
    for time, notes in a_notes_at.items():
        a_notes_at[time] = sorted(notes, key=lambda note: note.note)

    # calculate metrics
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
    if len(a_notes_at) > 0:
        prev_max_chord_note = None
        prev_min_chord_note = None
        for a_time in sorted(a_notes_at.keys()):
            min_chord_note = a_notes_at[a_time][0].note
            max_chord_note = a_notes_at[a_time][-1].note
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
            if ENABLE_DISSONANCE_INSIDE:
                # includes septimes, seconds, tritons https://ru.wikipedia.org/wiki/Консонанс_и_диссонанс
                for i1 in range(len(a_notes_at[a_time])):
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
            # if ENABLE_DISSONANCE_WITH_MELODY:
            #     pass  # TODO
            prev_max_chord_note = max_chord_note
            prev_min_chord_note = min_chord_note

    return metrics


def _event_to_award(metrics: Dict[str, int]) -> float:
    award = 0
    weights = EVENT_TO_AWARD_WEIGHTS
    for metric, count in metrics.items():
        award += weights[metric] * count
    return award
