class Note:
    def __init__(self, note: int, duration: int):
        assert note >= 0, "note must be positive"
        assert duration >= 0, "duration must be positive"
        self.note = note
        self.duration = duration


class CompositionNote(Note):
    def __init__(self, note: int, start_time: int, duration: int):
        super().__init__(note=note, duration=duration)
        assert start_time >= 0, "start_time must be positive"
        self.start_time = start_time

    @property
    def end_time(self) -> int:
        return self.start_time + self.duration

    def clone(self):
        return CompositionNote(note=self.note, start_time=self.start_time, duration=self.duration)
