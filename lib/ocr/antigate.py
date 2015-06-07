# -*- coding: utf-8 -*-
# -*- mode: python -*-
import os, time
from urllib.parse import urlencode
import sup
import .exc

min_len = 5
max_len = 5
post_url = 'http://antigate.com/in.php'
postdata = {
    'method': 'post',
    'key': None, # api key
    'file': None, # formed image file
    'phrase': '0', # 0 - one word, 1 - two words
    'regsense': '0', # case sensetive
    'numeric': '0', # 1 - numeric, 2 - no numbers
    'calc': '0', # math on pic
    'min_len': str(min_len),
    'max_len': str(max_len),
    'is_russian': '0',
    # 'soft_id': '',
    }
get_url = 'http://antigate.com/res.php'
getdata = {
    'action': 'get',
    'key': None,
    'id': None,
    }
report_url = 'http://antigate.com/res.php'
reportdata = {
    'action': 'reportbad',
    'key': None,
    'id': None,
    }

class Antigate(object):
    def __init__(self, net, key):
        self.net = net
        self.key = key
    
    def upload(self, img, **kvargs):
        p = postdata.copy()
        p.update({'key': self.key, 'file': self.net.formfile(img)})
        p.update(kvargs)
    
        res = self.net.req(post_url, p).decode()
        if res.startswith('OK'):
            cid = res.partition('|')[2]
            return cid # raise exc.Success?
        elif res.startswith('ERROR'):
            error = res.partition('_')[2]
            if error in ('WRONG_USER_KEY', 'KEY_DOES_NOT_EXIST',
                         'ZERO_CAPTCHA_FILESIZE', 'TOO_BIG_CAPTCHA_FILESIZE',
                         'WRONG_FILE_EXTENSION', 'IMAGE_TYPE_NOT_SUPPORTED'):
                raise exc.PermOCRError("Antigate returned %s error", error)
            elif error in ('ZERO_BALANCE', 'NO_SLOT_AVAILABLE', 'IP_NOT_ALLOWED'):
                raise exc.TempOCRError('Antigate returned %s error', error)
        raise exc.TempOCRError('Unknown answer "%s" from antigate', res)

    def parse_result(self, res, bulk=False):
        if not bulk and res.startswith('OK'):
            code = res.partition('|')[2]
            if (code == 'ERROR_CAPTCHA_UNSOLVABLE'
                or code == 'ERROR_CAPTCHA_UNSOLVABLE'.lower()
                or len(code) < min_len or len(code) > max_len):
                #raise stupid.antigate
                raise exc.PermOCRError('Antigate returned %s instead of code', code)
            return code # raise exc.Succes?
        elif res == 'CAPCHA_NOT_READY': return # and may be exc.Something here?
        elif res.startswith('ERROR'):
            error = res.partition('_')[2]
            if error in ('KEY_DOES_NOT_EXIST', 'WRONG_ID_FORMAT', 'CAPTCHA_UNSOLVABLE',
                         'BAD_DUPLICATES'):
                raise exc.PermOCRError('Antigate returned %s error', res)
        else:
            if not bulk:
                raise exc.TempOCRError('Unknown answer "%s" from antigate', res)
            else:
                if (len(res) < min_len or len(res) > max_len):
                    #raise stupid.antigate
                    raise exc.PermOCRError('Antigate returned %s instead of code', res)
                return res

    def check(self, cid):
        data = getdata.copy()
        data.update({'key': self.key, 'id': cid})
        q = urlencode(data)
        res = self.net.req('?'.join((get_url, q))).decode()
        return self.parse_result(res)

    def parse_results(self, cids, results):
        rlist = []
        if len(cids) != len(results):
            raise KeyError('len(cids) != len(results), this is probably wrong')
        for i in range(len(cids)):
            try:
                res = self.parse_result(results[i], bulk=True)
                if res: rlist.append((cids[i], res))
            except exc.PermOCRError as e:
                rlist.append((cids[i], e))
            except exc.TempOCRError as e:
                pass
        return rlist
    
    def check_bulk(self, cids):
        data = getdata.copy()
        data.update({'key': self.key, 'ids': ','.join(cids)})
        del data['id']
        q = urlencode(data)
        res = self.net.req('?'.join((get_url, q))).decode()
        return self.parse_results(cids, res.split('|'))

    def report_bad(self, cid):
        data = reportdata.copy()
        data.update({'key': self.key, 'id': cid})
        q = urlencode(data)
        res = self.net.req('?'.join((report_url, q))).decode()
        return res # raise exc.Succes?
