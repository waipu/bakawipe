# -*- coding: utf-8 -*-
# -*- mode: python -*-
# from simplejson import scanner
from sup import randstr, construct_url, net
from threading import Event
import random, time, logging

domain = 'mailinator.com'
url_webinbox = '/api/webinbox'
url_rendermail = '/rendermail.jsp'


class Mailinator(object):
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
        self.log = logging.getLogger('Mailinator')

    def get_domains(self):
        rlist = []
        with open('mailinator-domains.txt', 'r') as f:
            for line in f:
                rlist.append(line.rstrip('\n'))
        return rlist

    def gen_addr(self, f=5, b=16, charset=None):
        login = randstr(f, b, charset)
        return '@'.join((login, random.choice(self.get_domains())))

    def _grab2(self, inbox, _time=None):
        _time = _time or str(int(time.time()))
        u = construct_url(domain, (url_webinbox,),
                          {'to': inbox, 'time': _time})
        rec = self.net.http_req(u)
        return rec.json()

    def _render(self, msgid, _time=None):
        _time = _time or str(int(time.time()))
        u = construct_url(domain, (url_rendermail,), {'msgid': msgid, 'time': _time})
        rec = self.net.http_req(u)
        return rec

    def get_messages(self, email, timeout=300, interval=10):
        username, domain = email.split('@', 1)
        self.log.info('Requesting messages for %s', username)
        sleeptime = 0
        rlist = []
        while self.running.is_set():
            if sleeptime > timeout:
                raise ValueError('No mail in here')
            try:
                msgs = self._grab2(username)
            except net.HTTPError as e:
                if not e.code == 404:
                    self.log.error(e)
                sleeptime += interval
                self.sleep(interval)
                continue
            except net.NetError as e:
                self.log.error(e)
                sleeptime += interval
                self.sleep(interval)
                continue
            except Exception as e:
                self.log.exception(e)
                continue
            if 'messages' not in msgs or len(msgs['messages']) == 0:
                self.log.debug('No messages found')
                sleeptime += interval
                self.sleep(interval)
                continue
            for i in msgs['messages']:
                # if 'priv' in i: # what is this for?
                #     sleeptime += interval
                #     self.sleep(interval)
                #     continue
                if 'been_read' in i and i['been_read'] is True:
                    continue
                if i['fromfull'].startswith('reminder'):
                    self.log.info('Found unread message from %s, %ds ago', i['fromfull'], i['seconds_ago'])
                    rlist.append({'mail_from': i['fromfull'],
                                  'mail_html': self._render(i['id']).decode('cp1251')})
            if len(rlist) > 0:
                return rlist
            else:
                sleeptime += interval
                self.sleep(interval)
