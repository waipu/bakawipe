
class BMBase(object):
    def __init__(self):
        self.m_kv = {}
        self.m_vk = {}

    def __contains__(self, key):
        return key in self.m_kv

    def keys(self):
        return self.m_kv.keys()

    def values(self):
        return self.m_vk.keys()
    
    def items_keys(self):
        return self.m_kv.items()

    def items_values(self):
        return self.m_vk.items()
    
    def get_key(self, value, default=False):
        try:
            return self.m_vk[value]
        except KeyError:
            if default != False:
                return default
            raise
