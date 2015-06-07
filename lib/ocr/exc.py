# -*- coding: utf-8 -*-
# -*- mode: python -*-
from exceptions import *

class OCRError(Exception):
    def __init__(self, errstr=None, value=None, cahash=None, caurl=None):
        if value:
            try: errstr = errstr%value
            except TypeError: pass
        super().__init__(errstr)
        self.value = value
        self.caurl, self.cahash = caurl, cahash
        
class PermOCRError(OCRError, PermanentError): pass
class TempOCRError(OCRError, TemporaryError): pass
