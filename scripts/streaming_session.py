from queue import Queue
 
class StreamingSession:
 
    _queue: Queue
 
    STOP: str = "__[STOP]__"
 
    def __init__(self):
        self._queue = Queue()
 
    def write_message(self, message: str):               
        self._queue.put(message)
 
    def write_error(self, error_message: str):        
        self.write_message(error_message)
        self.close()
 
    def close(self):
        """
        Terminates the streaming session
        """
        self._queue.put(self.STOP)
 
    def read(self):        
        return self._queue.get() if not self._queue.empty() else None