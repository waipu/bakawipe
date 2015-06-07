import logging, threading, time

class TerminableThread(threading.Thread):
    def __init__(self, name=None, start_timer=None):
        super().__init__()
        self.running = threading.Event()
        self.wakeup = threading.Event()
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

# class TaskThread(TerminableThread):
#     def __init__(self, call, *args, **kvargs):
#         super().__init__(*args, **kvargs)
#         self.call = call

#     def _run(self):
#         self.call()

# class ReloaderThread(TerminableThread):
#     def __init__(self, check, call, *args, **kvargs):
#         super().__init__(*args, **kvargs)
#         self.timeout = timeout
#         self.check, self.call = check, call

#     def _run(self):
#         while self.running.is_set():
#             try:
#                 if self.check():
#                     self.call()
#             except Exception as e:
#                 self.log.error(e)

import multiprocessing

class TerminableProcess(multiprocessing.Process):
    def __init__(self, name=None, start_timer=None):
        super().__init__()
        self.running = multiprocessing.Event()
        self.name = name if name else type(self).__name__
        self.start_timer = start_timer
        self.log = logging.getLogger(self.name)

    def run(self):
        if self.start_timer:
            time.sleep(self.start_timer)
        self.running.set()
        self.log.info('Starting')
        self._run()
        self.log.info('Terminating')

    def _run(self):
        raise NotImplementedError

    def term(self):
        self.running.clear()
