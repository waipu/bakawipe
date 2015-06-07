# -*- coding: utf-8 -*-
# -*- mode: python -*-
import abc

class AMail(metaclass=abc.ABCMeta):
    '''Generic ABC class for mail registration api'''
    def __init__(self, net):
        self.net = net

    @abc.abstractmethod
    def get_domains(self):
        raise NotImplementedError

class ARandMail(AMail):
    '''For fully random mail registration api
    where you don't need to register address in any way'''
    @abc.abstractmethod
    def get_messages(self, email):
        raise NotImplementedError

class ALoginGenMail(AMail):
    @abc.abstractmethod
    def get_addr(self, domain):
        raise NotImplementedError

    @abc.abstractmethod
    def get_messages(self, email):
        raise NotImplementedError
