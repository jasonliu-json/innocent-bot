class AverageQueue:

    def __init__(self, size=5):
        self.queue = []
        self.size = size
        self.sum = 0
        self.length = 0

    def add(self, x):
        self.queue.append(x)
        self.sum += x
        if self.length < self.size:
            self.length += 1
        else:
            self.pop()

    def pop(self):
        if self.queue != []:
            x = self.queue.pop(0)
            self.length -= 1
            self.sum -= x
            return x
        else:
            return None

    def average(self):
        if self.length == 0:
            return None
        else:
            return self.sum / self.length


