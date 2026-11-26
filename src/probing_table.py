from .hash_table import TableBase, horner


class ProbingTable(TableBase):
    def __init__(self, capacity=16, max_load=0.75):
        if max_load is not None and max_load > 1:
            raise ValueError("probing load limit cannot exceed 1")
        super().__init__(capacity, max_load)

    def _locate(self, key):
        index = horner(key, self.capacity)
        for inspected in range(1, self.capacity + 1):
            entry = self.slots[index]
            if entry is None or entry[0] == key:
                return index, inspected
            index = (index + 1) % self.capacity
        return None, self.capacity

    def find(self, key):
        index, inspected = self._locate(key)
        if index is None or self.slots[index] is None:
            return None, inspected
        return self.slots[index][1], inspected

    def put(self, key, value):
        index, _ = self._locate(key)
        if index is not None and self.slots[index] is not None:
            self.slots[index] = (key, value)
            return
        if self.grow_before_insert():
            index, _ = self._locate(key)
        if index is None:
            raise OverflowError("fixed-size table is full")
        self.slots[index] = (key, value)
        self.count += 1

    def entries(self):
        for index, entry in enumerate(self.slots):
            if entry is not None:
                yield index, entry[0], entry[1]
