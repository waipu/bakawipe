# -*- coding: utf-8 -*-
import random, string

def randstr(f, b, charset=None) -> str:
    '''Returns random string.
    charset default to lowercase+digits'''
    s = ''.join(
        random.choice(charset
            or ''.join((string.ascii_lowercase,  string.digits)))
        for x in range(random.randint(f, b)))
    return s

def randline(fobj, separator='\n\n', count=1) -> bytes:
    '''Returns random line from file'''
    return random.choice(fobj.read().split(separator))
