class Note:
    """Note object that contain note number and duration of its play."""
    def __init__(self, note: int, duration: int):
        assert note >= 0, "note must be positive"
        assert duration >= 0, "duration must be positive"
        self.note = note
        self.duration = duration


class CompositionNote(Note):
    """Note object that has start_time of play."""
    def __init__(self, note: int, start_time: int, duration: int):
        super().__init__(note=note, duration=duration)
        assert start_time >= 0, "start_time must be positive"
        self.start_time = start_time

    @property
    def end_time(self) -> int:
        """Returns end time of play."""
        return self.start_time + self.duration

    def clone(self):
        """Returns exact copy of the note."""
        return CompositionNote(note=self.note, start_time=self.start_time, duration=self.duration)
