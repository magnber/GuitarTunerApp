from threading import Lock

class SharedQueue(object):
    """ Simple queue to share data between Threads with lock protection.
        Standard buffer length is set to 8 """

    def __init__(self, buffer_size=8):
        self.elements = []
        self.buffer_size = buffer_size
        self.lock = Lock()

    def put(self, element):
        """
        Add an element to the queue. If the queue limit is reached, removed the oldest element.
        """
        with self.lock:
            self.elements.append(element)
            if len(self.elements) > self.buffer_size:
                self.elements.pop(0)

    def get(self):
        """
        Return the first element of the queue
        """
        with self.lock:
            if len(self.elements) > 0:
                return self.elements.pop(0)
            else:
                return None

    def __repr__(self):
        with self.lock: 
            return str(self.elements)
