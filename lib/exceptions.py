# -*- coding: utf-8 -*-
# -*- mode: python -*-
class UsageError(Exception): pass

class AnswerException(Exception):
    def __init__(self, errstr=None, target=None, answer=None, postdata=None):
        if target:
            try: errstr = errstr%target
            except TypeError: pass
        super().__init__(errstr)
        self.target, self.answer, self.postdata = target, answer, postdata

class PermanentError(Exception):
    '''Error that doesn't go away if the same thing is done 10 seconds after'''
    pass

class TemporaryError(Exception):
    '''Error that may go away if the same thing is done 10 seconds after'''
    pass
