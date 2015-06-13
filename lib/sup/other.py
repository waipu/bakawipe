# -*- coding: utf-8 -*-
# -*- mode: python -*-
# from time import asctime
from urllib.parse import quote_plus
from .special import *

def formquery(**args) -> str:
    '''Wheel must be reinvented! Try urllib.urlencode before using this.'''
    return '&'.join('='.join((k, v)) for k, v in args.items())

def construct_url(domain, path=(), query='', method='http') -> str:
    s = '://'.join((method, domain))
    if path:
        p = '/'.join(path)
        u = ('' if p.startswith('/') else '/').join((s, p))
    else:
        u = '/'.join((s, ''))
    if query:
        q = (query if isinstance(query, str)
             else urlencode(query))
        u = '?'.join((u, q))
    return u

def urlencode(d, to='utf-8') -> bytes:
    data = []
    for k, v in d.items():
        try:
            data.append('='.join((k, quote_plus(v, encoding=to))))
        except TypeError:
            print(k, v)
            raise
    return '&'.join(data)

def encode_dict(in_dict, frm='utf8', to='utf8') -> dict:
    '''Encode str/unicode dict in str.'''
    out_dict = {}
    for k, v in in_dict.items():
        if isinstance(v, str):
            if type(v) == SpecialString:
                v = v.encode()
            else:
                v = v.encode(to)
        elif isinstance(v, bytes):
            if type(v) == SpecialBytes:
                if v.encoding == to:
                    v = bytes(v)
                else:
                    v = v.decode().encode(to)
            else:
                if frm == to:
                     v.decode(to) # test
                else:
                     v = v.decode(frm).encode(to)
        out_dict[k] = v
    return out_dict

# def qrgen(text,size=120, addr=None) -> object:
#     '''Generate sizexsize qr code from text. Depends on pyqrencode.'''
#     import qrencode
#     image = qrencode.encode_scaled(text,size)[2]
#     return (addr and image.save(addr)
#             or image)
