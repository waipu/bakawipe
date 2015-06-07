# -*- coding: utf-8 -*-
# -*- mode: python -*-
import logging, time
import threading, multiprocessing

class BaseWorker(object):
    def __init__(self, name=None, start_timer=None):
        super().__init__()
        self.name = name if name else type(self).__name__
        self.start_timer = start_timer
        self.log = logging.getLogger(self.name)

    def inter_sleep(self, timeout):
        self.wakeup.wait(timeout)

    def run(self):
        self.running.set()
        if self.start_timer:
            self.inter_sleep(self.start_timer)
        if self.running.is_set():
            self.log.info('Starting')
            self._run()
        self.log.info('Terminating')
    
    def _run(self):
        raise NotImplementedError

    def term(self):
        self.running.clear()
        self.wakeup.set()

class TerminableThread(BaseWorker, threading.Thread):
    def __init__(self, name=None, start_timer=None):
        self.running = threading.Event()
        self.wakeup = threading.Event()
        super().__init__(name, start_timer)

class TerminableProcess(BaseWorker, multiprocessing.Process):
    def __init__(self, name=None, start_timer=None):
        self.running = multiprocessing.Event()
        self.wakeup = multiprocessing.Event()
        super().__init__(name, start_timer)
