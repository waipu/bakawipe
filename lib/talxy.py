#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from random import randint
from sup import net, formquery, randstr

class Talxy(net):
    def __init__(self):
        net.__init__(self)
        self.domain = "talxy.ru" # Yep, domain. talxy.ru
        self.cookie = self.domain+'logincookie.jar'
        self.user = randstr(3,5)
    
    class url:
        '''Various cgi urls, internal usage.'''
        users = "/board/users"
        chat = "/board/chat"
        cmd = "/board/cmd/" # note / at the end.
    
    #class rsp:
    #'''Server responses'''

    def set_user(self, user, **kvargs):
        postdata = {"h": self.domain,
                    "u": user, #TODO: url
                    "act": "1"} # init: login, 0: keepalive, 1: change.
        postdata.update(kvargs)
        url = ''.join(('http://', self.domain, self.url.users))
        self.user = user
        return self.req(url, postdata, self.cookie, onlyjar=True)

    def set_cmd(self, text, **kvargs):
        postdata = {"h": self.domain, # host
                    "n": self.user, # nick
                    "d": text, # data
                    "r": str(randint(1, 1000))} #needs testing.
        postdata.update(kvargs)
        url = ''.join(('http://', self.domain, self.url.cmd))
        return self.req(url, postdata, self.cookie)
        
    def postmsg(self, text, **kvargs):
        postdata = {"a": "add", # action
                    "u": self.user, # user
                    "h": self.domain, # host
                    "t": text } # text"""
        postdata.update(kvargs)
        url = ''.join(('http://', self.domain, self.url.chat))
        return self.req(url, postdata, self.cookie)
