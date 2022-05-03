from random import random
from typing import Tuple

from music_interfaces.composition.composition import Composition


def make_crossover(candidate1: Composition, candidate2: Composition) -> Tuple[Composition, Composition]:
    """Note: candidate compostitions should have chords should be placed exactly at places that are multiples of
    4 quarter"""
    child1_notes = []
    child2_notes = []
    cand1_notes_as = candidate1.notes_at
    cand2_notes_as = candidate2.notes_at
    times = set(list(cand1_notes_as.keys()) + list(cand2_notes_as.keys()))
    for time in times:
        if random() > 0.5:
            child1_notes += cand2_notes_as.get(time, [])
            child2_notes += cand1_notes_as.get(time, [])
        else:
            child1_notes += cand1_notes_as.get(time, [])
            child2_notes += cand2_notes_as.get(time, [])
    child1 = candidate1.clone()
    child2 = candidate2.clone()
    child1.notes = child1_notes
    child2.notes = child2_notes
    return child1, child2
