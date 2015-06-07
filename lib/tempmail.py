# -*- coding: utf-8 -*-
# -*- mode: python -*-
# from abcmail import *
import time
from simplejson import scanner
from sup import randstr, construct_url, net
from hashlib import md5

domain = 'api.temp-mail.ru'
url_domains = '/request/domains'
url_mail = '/request/mail/id/{0}'
urlp_json = 'format/json/'

# class TempMail(ARandMail):
#     def get_domains(self):
#         u = construct_url(domain, (url_domains, urlp_json))
#         rec = self.net.req(u)
#         if len(rec) == 0:
#             raise exc.EmptyAnswer('Rec empty')
#         return list(filter(
#             lambda s: s.lstrip('@'), rec.json()))
#     def get_messages(self, email):
#         if type(email) == str:
#             email = email.encode('utf-8')
#         mailhash = md5(email).hexdigest()
#         u = construct_url(domain, (url_mail, urlp_json)).format(mailhash)
#         try:
#             rec = self.net.http_req_perform(self.net.http_req(u))
#         except net.HTTPError as e:
#             if e.code == 404:
#                 raise ValueError('No mail in here')
#             raise
#         if len(rec) == 0:
#             raise exc.EmptyAnswer('Rec empty', email)
#         rlist = []
#         for m in rec.json():
#             rlist.append((m['mail_from'], m['mail_subject'],
# m['mail_text_only']))
#         return html

import random
from threading import Event
class TempMail:
    def __init__(self, net, running=None, sleep=None):
        self.net = net
        if running:
            self.running = running
        else:
            self.running = Event()
            self.running.set()
        if sleep:
            self.sleep = sleep
        else:
            self.sleep = time.sleep

    def get_domains(self):
        """
        Return list of available domains.
        """
        if not hasattr(self, '_available_domains'):
            u = construct_url(domain, (url_domains, urlp_json))
            domains = self.net.http_req(u).json()
            setattr(self, '_available_domains', domains)
        return self._available_domains

    def gen_addr(self, f=5, b=16, charset=None):
        login = randstr(f, b, charset)
        return ''.join((login, random.choice(self.get_domains())))

    def get_messages(self, email, timeout=300, interval=5):
        if type(email) == str:
            email = email.encode('utf-8')
        mailhash = md5(email).hexdigest()
        u = construct_url(domain, (url_mail, urlp_json)).format(mailhash)
        sleeptime = 0
        while self.running.is_set():
            try:
                rec = self.net.http_req(u)
                return rec.json()
            except net.HTTPError as e:
                if not e.code == 404:
                    raise
                if sleeptime > timeout:
                    raise ValueError('No mail in here')
                sleeptime += interval
                self.sleep(interval)
            except scanner.JSONDecodeError as e:
                print(email, e, rec)
