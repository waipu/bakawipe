# -*- coding: utf-8 -*-
# -*- mode: python -*-
from exceptions import *

class InvalidLogin(PermanentError, AnswerException): pass
class GuestDeny(PermanentError, AnswerException): pass
class UserDeny(PermanentError, AnswerException): pass
class Bumplimit(PermanentError, AnswerException): pass
class PermClosed(PermanentError, AnswerException): pass
class TopicDoesNotExist(PermanentError, AnswerException): pass
    
class BadGateway(TemporaryError, AnswerException): pass
class EmptyAnswer(TemporaryError, AnswerException): pass
class Antispam(TemporaryError, AnswerException): pass
class Redir(TemporaryError, AnswerException): pass
class Wait5Min(TemporaryError, AnswerException): pass
class Closed(TemporaryError, AnswerException): pass
class UnknownAnswer(TemporaryError, AnswerException): pass

class RegRetryLimit(PermanentError): pass
class DosVersionError(PermanentError, NotImplementedError): pass

class Captcha(AnswerException):
    def __init__(self, page, errstr=None, target=None, postdata=None, catry=1):
        '''
        page: raw page with captcha
        catry: see Beon.addtopicfin()
        '''
        super(Captcha, self).__init__(errstr, target, page, postdata)
        self.page, self.catry = page, catry

class Success(AnswerException): pass
