import random
from typing import List, Union

from app_config import MAX_MUTATION_SHIFT, MAX_NOTE
from music_interfaces.composition.composition import Composition
from music_interfaces.note import CompositionNote


def get_random_chord() -> List[int]:
    major_triad = [0, 4, 7]
    minor_triad = [0, 3, 7]
    major_triad_1i = [0, 3, 8]
    major_triad_2i = [0, 5, 9]
    minor_triad_1i = [0, 4, 9]
    minor_triad_2i = [0, 5, 8]
    diminiched_chord = [0, 3, 6]
    sus2_chord = [0, 2, 7]
    sus4_chord = [0, 5, 7]
    empty_chord = []
    chords = [major_triad, minor_triad, major_triad_1i, major_triad_2i, minor_triad_1i, minor_triad_2i,
              diminiched_chord, sus2_chord, sus4_chord, empty_chord]
    return random.choice(chords)


def get_random_absolute_chord() -> List[int]:
    random_chord = get_random_chord()
    absolute_chord = _randomly_teleport_chord(random_chord)
    return absolute_chord


def _get_random_chord_position(chord: Union[List[CompositionNote], List[int]]) -> int:
    """Returns new valid random position for chord or 0 if chord is empty"""
    random_position = 0
    if len(chord) > 0:
        if isinstance(chord[0], CompositionNote):
            max_note = max([note.note for note in chord])
        else:
            max_note = max(chord)
        random_position = random.randrange(0, MAX_NOTE - max_note + 1)
    return random_position


def get_random_candidate(melody: Composition) -> Composition:
    chord_duration = melody.ticks_per_beat
    duration_in_chords = round(melody.duration / chord_duration)
    notes = []
    for i in range(duration_in_chords):
        notes += [CompositionNote(note, i * chord_duration, chord_duration) for note in get_random_absolute_chord()]
    candidate = melody.clone()
    candidate.notes = notes
    return candidate


def make_mutation(candidate: Composition, mutation_chance: float) -> Composition:
    assert 0 <= mutation_chance <= 1, "mutation_chance must belong to [0:1] interval"
    chord_duration = candidate.ticks_per_beat
    duration_in_chords = round(candidate.duration / chord_duration)
    c_notes_at = candidate.notes_at
    notes = []
    for i in range(duration_in_chords):
        time = i * chord_duration
        if random.random() < mutation_chance:
            c_notes_at[time] = c_notes_at.get(time, [])
            c_notes_at[time] = mutate_chord(c_notes_at[time], start_time=time, duration=chord_duration)
        notes += c_notes_at.get(time, [])
    mutated_candidate = candidate.clone()
    mutated_candidate.notes = notes
    return mutated_candidate


def mutate_chord(chord: List[CompositionNote], **context) -> List[CompositionNote]:
    actions = [_randomly_shift_chord, _randomly_teleport_chord, _replace_chord_type_by_random]
    random_action = random.choice(actions)
    return random_action(chord, **context)


def _randomly_shift_chord(chord: List[CompositionNote], **context) -> List[CompositionNote]:
    min_note = min([note.note for note in chord]) if len(chord) > 0 else 0
    max_note = max([note.note for note in chord]) if len(chord) > 0 else 0
    lower_shift_bound = max(0, min_note - MAX_MUTATION_SHIFT) - min_note
    upper_shift_bound = min(MAX_NOTE, max_note + MAX_MUTATION_SHIFT) - max_note
    random_shift = random.randrange(lower_shift_bound, upper_shift_bound+1)
    shifted_chord = [note.clone() for note in chord]
    for note in shifted_chord:
        note.note = note.note + random_shift
    return shifted_chord


def _randomly_teleport_chord(chord: Union[List[CompositionNote], List[int]], **context) -> Union[List[CompositionNote], List[int]]:
    lowest_note_num = _get_random_chord_position(chord)
    teleported_chord = []
    if len(chord) > 0:
        if isinstance(chord[0], CompositionNote):
            teleported_chord = [note.clone() for note in chord]
            for note in teleported_chord:
                note.note = lowest_note_num + note.note
        else:
            teleported_chord = [lowest_note_num + note for note in chord]
    return teleported_chord


def _replace_chord_type_by_random(chord: List[CompositionNote], **context) -> List[CompositionNote]:
    start_time = context["start_time"]
    duration = context["duration"]
    random_chord = get_random_chord()
    chord_lowest_note = min([note.note for note in chord]) if len(chord) > 0 else 0
    r_chord_highest_note = max([note for note in random_chord]) if len(random_chord) > 0 else 0
    shift = min(MAX_NOTE, chord_lowest_note + r_chord_highest_note) - (chord_lowest_note + r_chord_highest_note)
    replaced_chord = [CompositionNote(note=chord_lowest_note + note + shift, start_time=start_time, duration=duration)
                      for note in random_chord]
    return replaced_chord
