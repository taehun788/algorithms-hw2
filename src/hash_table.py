from dataclasses import dataclass


def horner(key, capacity, trace=None):
    value = 0
    for char in key:
        previous = value
        value = (31 * value + ord(char)) % capacity
        if trace is not None:
            trace.append((char, previous, value))
    return value


class TableBase:
    def __init__(self, capacity, max_load):
        if capacity < 1 or (max_load is not None and max_load <= 0):
            raise ValueError("capacity and load limit must be positive")
        self.slots = [None] * capacity
        self.max_load = max_load
        self.count = 0

    def __len__(self):
        return self.count

    @property
    def capacity(self):
        return len(self.slots)

    @property
    def load_factor(self):
        return self.count / self.capacity

    def get(self, key):
        return self.find(key)[0]

    def __contains__(self, key):
        return self.get(key) is not None

    def grow_before_insert(self):
        if self.max_load is None or self.count + 1 <= self.capacity * self.max_load:
            return False
        entries = [(key, value) for _, key, value in self.entries()]
        self.slots = [None] * (2 * self.capacity)
        self.count = 0
        for key, value in entries:
            self.put(key, value)
        return True


@dataclass(slots=True)
class Node:
    key: str
    value: str
    next: "Node | None" = None


class HashTable(TableBase):
    def __init__(self, capacity=16, max_load=2.0):
        super().__init__(capacity, max_load)

    def find(self, key):
        node = self.slots[horner(key, self.capacity)]
        comparisons = 0
        while node is not None:
            comparisons += 1
            if node.key == key:
                return node.value, comparisons
            node = node.next
        return None, comparisons

    def put(self, key, value):
        index = horner(key, self.capacity)
        node = self.slots[index]
        while node is not None:
            if node.key == key:
                node.value = value
                return
            node = node.next
        if self.grow_before_insert():
            index = horner(key, self.capacity)
        self.slots[index] = Node(key, value, self.slots[index])
        self.count += 1

    def entries(self):
        for index, node in enumerate(self.slots):
            while node is not None:
                yield index, node.key, node.value
                node = node.next
