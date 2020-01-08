from collections import OrderedDict


class OrderedSet:
    def __init__(self, contents=()):
        self.set = OrderedDict((c, None) for c in contents)

    def __contains__(self, item):
        return item in self.set

    def __iter__(self):
        return iter(self.set.keys())

    def __len__(self):
        return len(self.set)

    def add(self, item):
        self.set[item] = None

    def clear(self):
        self.set.clear()

    def index(self, item):
        idx = 0
        for i in self.set.keys():
            if item == i:
                break
            idx += 1
        return idx

    def pop(self):
        item = next(iter(self.set))
        del self.set[item]
        return item

    def remove(self, item):
        del self.set[item]
        
    def discard(self, item):
        if item in self:
            self.remove(item)

    def to_list(self):
        return [k for k in self.set]

    def update(self, contents):
        for c in contents:
            self.add(c)

    def difference_update(self, items):
        """
        Update this OrderedSet to remove items from one or more other sets.
        """
        for i in items:
            if i in self:
                self.remove(i)


if __name__ == '__main__':
    a = OrderedSet()
    a.add(21)
    a.add(12)
    a.add(32)
    a.add(112)
    a.add(98)
