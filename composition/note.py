from mido import Message
from typing import Tuple


class Note:
    def __init__(self, note: int, duration: float):
        assert note >= 0, "note must be positive"
        assert duration >= 0, "duration must be positive"
        self.note = note
        self.duration = duration


class CompositionNote(Note):
    def __init__(self, note: int, start_time: float, duration: float):
        super().__init__(note=note, duration=duration)
        assert start_time >= 0, "start_time must be positive"
        self.start_time = start_time

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration


# class MidiNote:
#     def __init__(self, note: Tuple[Message, Message]):
#         assert note[0].type == "note_on" and note[1].type == "note_off", "note must consist of (note_on, note_off)"
#         self.note = note
