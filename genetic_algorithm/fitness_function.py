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
EVENT_TO_AWARD_WEIGHTS = {
    MISSING_ACCOMP_FOR_MELODY_TICK: -1,
    EXCESS_ACCOMP_TICK_FOR_MELODY: -10,
    TOO_BIG_CHORD_DROP: -20,
    ACCOMP_TICK_NOT_BELOW_MELODY: -5,
    DISSONANCE_INSIDE: -3
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
        DISSONANCE_INSIDE: 0
    }
    m_notes_at = melody.notes_at
    a_notes_at = accompaniment.notes_at

    # preprocess inputs
    for time, notes in m_notes_at.items():
        m_notes_at[time] = sorted(notes, key=lambda note: note.note)
    for time, notes in a_notes_at.items():
        a_notes_at[time] = sorted(notes, key=lambda note: note.note)

    # calculate metrics
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
            # if ENABLE_DISSONANCE_INSIDE:
            #     for i in range(1, len(a_notes_at[a_time])):
            #         pass  # TODO
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
