# -*- coding: utf-8 -*-
# -*- mode: python -*-
from .base import BMBase

class BijectiveMap(BMBase):
    '''Basic one to one bijective map'''
    def __setitem__(self, key, value):
        return self.set_value(key, value)
    
    def __getitem__(self, key, default=False):
        return self.get_value(key, default)

    def __delitem__(self, key):
        return self.del_value(key)

    def set_value(self, key, value):
        self.m_kv[key] = value
        self.m_vk[value] = key

    def get_value(self, key, default=False):
        try:
            return self.m_kv[key]
        except KeyError:
            if default != False:
                return default
            raise
    
    def del_value(self, key):
        v = self.m_kv[key]
        del self.m_kv[key]
        del self.m_vk[v]
    
    def del_key(self, value):
        key = self.get_key(value)
        del self.m_vk[value]
        del self.m_kv[key]
