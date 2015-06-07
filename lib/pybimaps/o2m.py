# -*- coding: utf-8 -*-
# -*- mode: python -*-
from .base import BMBase

class BijectiveListMap(BMBase):
    '''One to many bijective map with indexed list'''
    def __setitem__(self, key, values):
        return self.set_values(key, values)
    
    def __getitem__(self, key, default=False):
        return self.get_values(key, default)

    def __delitem__(self, key):
        return self.del_values(key)

    def set_values(self, key, values=[]):
        # filter previous values
        # sets may be faster than lists here
        try:
            pvs = self.m_kv[key]
            for v in pvs:
                if not v in values:
                    del self.m_vk[v]
        except KeyError:
            pass
        self.m_kv[key] = values
        for v in values:
            self.m_vk[v] = key

    def extend_values(self, key, values):
        try:
            self.m_kv[key].extend(values)
        except KeyError:
            self.m_kv[key] = values
        for v in values:
            self.m_vk[v] = key

    def append_value(self, key, value):
        try:
            self.m_kv[key].append(value)
        except KeyError:
            self.m_kv[key] = [value]
        self.m_vk[value] = key

    def insert_value(self, key, index, value):
        self.m_kv[key].insert(index, value)
        self.m_vk[value] = key
    
    def get_values(self, key, default=False):
        try:
            return self.m_kv[key]
        except KeyError:
            if default != False:
                return default
            raise
    
    def del_values(self, key):
        values = self.get_values(key)
        for v in values:
            del self.m_vk[v]
        del self.m_kv[key]

    def del_value(self, key, value):
        self.m_kv[key].remove(value)
        del self.m_vk[value]

    def pop_value(self, key, index=None):
        v = self.m_kv[key].pop(index)
        del self.m_vk[v]
        return v
        
    def del_key(self, value):
        key = self.get_key(value)
        self.del_values(key)

class BijectiveSetMap(BMBase):
    '''One to many bijective map with hash set'''
    def __setitem__(self, key, values):
        return self.set_values(key, values)
    
    def __getitem__(self, key, default=False):
        return self.get_values(key, default)

    def __delitem__(self, key):
        return self.del_values(key)

    def set_values(self, key, values=set()):
        # filter previous values
        try:
            for v in self.m_kv[key].difference(values):
                del self.m_vk[v]
        except KeyError:
            pass
        self.m_kv[key] = set(values)
        for v in values:
            self.m_vk[v] = key

    def update_values(self, key, values):
        try:
            self.m_kv[key].update(values)
        except KeyError:
            self.m_kv[key] = set(values)
        for v in values:
            self.m_vk[v] = key

    def add_value(self, key, value):
        try:
            self.m_kv[key].add(value)
        except KeyError:
            # Escaping value as tuple to allow addition of strings
            self.m_kv[key] = set((value,))
        self.m_vk[value] = key

    def get_values(self, key, default=False):
        try:
            return self.m_kv[key]
        except KeyError:
            if default != False:
                return default
            raise

    def del_values(self, key):
        values = self.get_values(key)
        for v in values:
            del self.m_vk[v]
        del self.m_kv[key]

    def del_value(self, key, value):
        self.m_kv[key].remove(value)
        del self.m_vk[value]

    def pop_value(self, key, value):
        v = self.m_kv[key].pop(value)
        del self.m_vk[v]
        return v
        
    def del_key(self, value):
        key = self.get_key(value)
        self.del_values(key)

    def clear_values(self, key):
        for v in self.get_values(key):
            del self.m_vk[v]
        self.m_kv[key].clear()
