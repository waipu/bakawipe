# -*- coding: utf-8 -*-
# -*- mode: python -*-
import time

class Ticker(object):
    def __init__(self):
        self.lasttick = 0

    def elapsed(self, tick=True) -> int:
        now = time.monotonic()
        ltick = self.lasttick
        if tick:
            self.lasttick = now
        if ltick > 0:
            return now - ltick
        else:
            return 0

    def tick(self) -> None:
        self.lasttick = time.monotonic()

    def __iter__(self):
        while True:
            yield self.elapsed()
