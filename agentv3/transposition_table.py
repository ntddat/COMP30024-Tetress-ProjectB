# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

class Entry:
    key: int
    value: float
    depth: int

    def _init_(
        self, 
        key: int,
        value: int,
        depth: int
    ):
        self.key = key
        self.value = value
        self.depth = depth

class Transposition_Table:
    entries: list[Entry]

    def _init_(self, size: int):
        entries = Entry[size]

    """
    def clear(self):
        for i in range(0, len(self.entries)):
    """

            