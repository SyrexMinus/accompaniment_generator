from typing import List, Tuple

from mido import MidiFile, Message

from music_interfaces.composition.composition_constants import MAJOR_TONIC, MINOR_TONIC
from music_interfaces.note import CompositionNote


class Composition:
    MIDI_TEMPLATE_PATH = "music_interfaces/composition/template.mid"
    min_duration: int = None

    def __init__(self, notes: List[CompositionNote] = None, ticks_per_beat: int = None, tempo: int = None,
                 midi_file: MidiFile = None):
        assert (notes is None and ticks_per_beat is None and tempo is None or midi_file is None) and \
               (notes is not None and ticks_per_beat is not None and tempo is not None or midi_file is not None), \
            "exactly one of {(notes, ticks_per_beat), midi_file} must be used"
        self._midi_file = midi_file
        if notes and ticks_per_beat and tempo:
            self.notes = notes
            self.ticks_per_beat = ticks_per_beat
            self.tempo = tempo
        else:
            self.notes, self.ticks_per_beat, self.tempo = self._read_midi_file(midi_file)

    @property
    def notes_at(self):
        notes_at = {}
        for note in self.notes:
            notes_at[note.start_time] = notes_at.get(note.start_time, [])
            notes_at[note.start_time].append(note)
        return notes_at

    @property
    def as_midi(self) -> MidiFile:
        # Note: order of messages in tracks matters
        mid = MidiFile(self.MIDI_TEMPLATE_PATH, clip=True)
        mid.ticks_per_beat = self.ticks_per_beat
        mid.tracks[0][1].tempo = self.tempo
        mid.tracks[1] = mid.tracks[1][:2] + self._notes_to_midi_messages() + [mid.tracks[1][-1]]
        if self.min_duration is not None:
            mid.tracks[1][-1].time = self.min_duration - max([note.end_time for note in self.notes])
        return mid

    def save_midi(self, filename: str):
        self.as_midi.save(filename)

    @property
    def key(self) -> Tuple[int, str]:
        """Returns the most probable key as (tonic (int[0-11]), scale (str["major"/"minor"]))"""
        MAJOR_KEY_OFFSETS = [0, 2, 2, 1, 2, 2, 2, 1]
        MINOR_KEY_OFFSETS = [0, 2, 1, 2, 2, 1, 2, 2]
        min_note_num = self.notes[0].note
        max_note_num = self.notes[0].note
        notes_used = {}
        for note in self.notes:
            note_num = note.note
            if note_num < min_note_num:
                min_note_num = note_num
            if note_num > max_note_num:
                max_note_num = note_num
            notes_used[note_num] = notes_used.get(note_num, 0)
            notes_used[note_num] += 1
        most_similar_key_tonic = min_note_num % 12
        most_similar_key_scale = MAJOR_TONIC
        max_similarity = 0
        considered_keys = [i for i in range(min_note_num, min_note_num-13, -1)] + \
                          [i for i in range(min_note_num+1, max_note_num+1)]
        for key in considered_keys:
            major_similarity = 0
            minor_similarity = 0
            for offset in MAJOR_KEY_OFFSETS:
                major_similarity += notes_used.get(key + offset, 0)
            for offset in MINOR_KEY_OFFSETS:
                minor_similarity += notes_used.get(key + offset, 0)
            if major_similarity > max_similarity:
                most_similar_key_tonic = key % 12
                most_similar_key_scale = MAJOR_TONIC
                max_similarity = major_similarity
            if minor_similarity > max_similarity:
                most_similar_key_tonic = key % 12
                most_similar_key_scale = MINOR_TONIC
                max_similarity = minor_similarity
        return most_similar_key_tonic, most_similar_key_scale

    @property
    def duration(self) -> int:
        """Returns duration in ticks"""
        return max([note.end_time for note in self.notes] + [self.min_duration])

    def clone(self):
        copy = Composition(notes=self.notes, ticks_per_beat=self.ticks_per_beat, tempo=self.tempo)
        copy.min_duration = self.min_duration
        return copy

    def _notes_to_midi_messages(self) -> List[Message]:
        messages = []
        times = {}
        for note in self.notes:
            times[note.start_time] = times.get(note.start_time, [])
            times[note.start_time].append((note.note, "note_on"))
            times[note.end_time] = times.get(note.end_time, [])
            times[note.end_time].append((note.note, "note_off"))
        prev_time = 0
        for i, time in enumerate(sorted(times.keys())):
            for event in times[time]:
                messages.append(Message(type=event[1], channel=0, note=event[0],
                                        velocity=50 if event[1] == "note_on" else 0, time=time-prev_time))
                prev_time = time
        return messages

    def _read_midi_file(self, midi_file: MidiFile) -> Tuple[List[CompositionNote], int, int]:
        """Returns (notes, ticks_per_beat, tempo)"""
        # Note: order of messages in tracks matters
        note_messages = midi_file.tracks[1][2:-1]
        notes = []
        notes_buffer = {}
        time = 0
        for note_message in note_messages:
            time += note_message.time
            if note_message.type == 'note_on':
                if note_message.note in notes_buffer:
                    notes_buffer[note_message.note].append(time)
                else:
                    notes_buffer[note_message.note] = [time]
            elif note_message.type == 'note_off':
                start_time = notes_buffer[note_message.note][0]
                duration = time - start_time
                notes.append(CompositionNote(note=note_message.note, start_time=start_time, duration=duration))
                if len(notes_buffer[note_message.note]) > 1:
                    notes_buffer[note_message.note] = notes_buffer[note_message.note][1:]
                else:
                    notes_buffer.pop(note_message.note)
            else:
                raise TypeError(f"Cannot read note_message with type {note_message.type}")
        return notes, midi_file.ticks_per_beat, midi_file.tracks[0][1].tempo
