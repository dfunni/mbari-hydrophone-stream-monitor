import os
from collections import deque

class DataDir(object):

    def __init__(self, directory):
        self.directory = directory
        self.file_dq = deque(os.listdir(directory))
        self.on_deck = ""
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.directory + self.file_dq.popleft()
    
    def remaining(self):
        return len(self.file_dq)
    
    def print_remaining(self):
        print(self.file_dq)

    def update(self):
        self.file_dq = deque(os.listdir(self.directory))