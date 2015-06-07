# -*- coding: utf-8 -*-
# -*- mode: python -*-
# TODO, if anything needs this: BijectiveSetListMap, BijectiveListListMap
from .base import BMBase

class BijectiveSetSetMap(BMBase):
    '''Many to many bijective map (graph) with hash sets.
    Can be pretty memory-heavy due to set with keys for each value.
    get_key method returns set with keys.'''
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
                self.m_vk[v].remove(key)
        except KeyError:
            pass
        self.m_kv[key] = set(values)
        for v in values:
            try:
                self.m_vk[v].add(key)
            except KeyError:
                self.m_vk[v] = set((key,))

    def update_values(self, key, values):
        try:
            self.m_kv[key].update(values)
        except KeyError:
            self.m_kv[key] = set(values)
        for v in values:
            try:
                self.m_vk[v].add(key)
            except KeyError:
                self.m_vk[v] = set((key,))

    def add_value(self, key, value):
        try:
            self.m_kv[key].add(value)
        except KeyError:
            # Escaping value as tuple to allow addition of strings
            self.m_kv[key] = set((value,))
        try:
            self.m_vk[value].add(key)
        except KeyError:
            self.m_vk[value] = set((key,))

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
            self.m_vk[v].remove(key)
        del self.m_kv[key]

    def del_value(self, key, value):
        self.m_kv[key].remove(value)
        self.m_vk[value].remove(key)

    def pop_value(self, key, value):
        v = self.m_kv[key].pop(value)
        self.m_vk[v].remove(key)
        return v
        
    def del_key(self, value):
        key = self.get_key(value)
        self.del_values(key)

    def clear_values(self, key):
        for v in self.get_values(key):
            self.m_vk[v].remove(key)
        self.m_kv[key].clear()

    def clear_keys(self, value):
        keys = self.get_key(value)
        for k in keys:
            self.m_kv[k].remove(value)
        self.m_vk[value].clear()

class BijectiveListSetMap(BMBase):
    '''Many to many bijective map (graph) with list for keys and hash set for values.
    Can be pretty memory-heavy due to set with keys for each value.
    get_key method returns set with keys.'''
    def __setitem__(self, key, values):
        return self.set_values(key, values)
    
    def __getitem__(self, key, default=False):
        return self.get_values(key, default)

    def __delitem__(self, key):
        return self.del_values(key)

    def set_values(self, key, values=list()):
        # filter previous values
        try:
            pvs = self.m_kv[key]
            for v in pvs:
                if not v in values:
                    self.m_vk[v].remove(key)
        except KeyError:
            pass
        self.m_kv[key] = values
        for v in values:
            try:
                self.m_vk[v].add(key)
            except KeyError:
                self.m_vk[v] = set((key,))

    def extend_values(self, key, values):
        try:
            self.m_kv[key].extend(values)
        except KeyError:
            self.m_kv[key] = [values]
        for v in values:
            try:
                self.m_vk[v].add(key)
            except KeyError:
                self.m_vk[v] = set((key,))

    def append_value(self, key, value):
        try:
            self.m_kv[key].append(value)
        except KeyError:
            # Escaping value as tuple to allow addition of strings
            self.m_kv[key] = [value]
        try:
            self.m_vk[value].add(key)
        except KeyError:
            self.m_vk[value] = set((key,))

    def insert_value(self, key, index, value):
        self.m_kv[key].insert(index, value)
        try:
            self.m_vk[value].add(key)
        except KeyError:
            self.m_vk[value] = set((key,))

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
            self.m_vk[v].remove(key)
        del self.m_kv[key]

    def del_value(self, key, value):
        self.m_kv[key].remove(value)
        self.m_vk[value].remove(key)

    def pop_value(self, key, index=None):
        v = self.m_kv[key].pop(index)
        self.m_vk[v].remove(key)
        return v
        
    def del_key(self, value):
        key = self.get_key(value)
        self.del_values(key)

    def clear_keys(self, value):
        keys = self.get_key(value)
        for k in keys:
            self.m_kv[k].remove(value)
        self.m_vk[value].clear()
