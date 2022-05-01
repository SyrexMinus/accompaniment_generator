from composition.composition import Composition
from composition.note import CompositionNote

notes = [CompositionNote(note=57, start_time=0, duration=192), CompositionNote(note=57, start_time=192, duration=192),
         CompositionNote(note=64, start_time=0, duration=192)]
comp = Composition(notes=notes, ticks_per_beat=384, tempo=545454)
comp.save_midi("output.mid")
