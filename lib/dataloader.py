import os, logging
from pybimaps import BijectiveMap
from sup.ticker import Ticker
from sup.net import NetError
from sup import construct_url, SpecialBytes

class DataLoader(object):
    domain = 'nphr.net'
    url_api = '/api/1.0'
    urlp_idforum = 'data/idforum.json'
    urlp_ualist = 'data/ua_list.json'
    urlp_addrs = 'data/addrs.json'
    urlp_witch_domains = 'witch/domains/json'
    urlp_witch_targets = 'witch/targets/json'
    tmp_path = 'temp'
    def __init__(self, net, only_cache=False):
        self.tickers = {}
        self.net = net
        self.log = logging.getLogger(type(self).__name__)
        self.log.info('Created for {0}'.format(self.domain))
        self.only_cache = only_cache

    def _load_data(self, urlp):
        # TODO: check for modification
        u = construct_url(self.domain, (self.url_api, urlp))
        fpath = os.path.join(self.tmp_path, type(self).__name__, urlp)
        if self.only_cache:
            self.log.info('Getting %s from cache', urlp)
            rec = False
        else:
            self.log.info('Loading %s', urlp)
            try:
                rec = self.net.http_req(u)
            except NetError as e:
                self.log.error(e)
                rec = False
            if rec:
                try:
                    rjson = rec.json()
                except Exception as e:
                    self.log.exception(e)
                    rec = False
        if not rec:
            if not self.only_cache:
                self.log.warning('Failed to load %s, using cache', urlp)
            with open(fpath, 'rb') as f:
                rec = SpecialBytes(f.read())
            return rec.json()
        else:
            dpath = os.path.dirname(fpath)
            if not os.path.isdir(dpath):
                os.makedirs(dpath)
            with open(fpath, 'wb') as f:
                f.write(bytes(rec))
            return rjson
    
    @property
    def bm_id_forum(self):
        if not 'bm_id_forum' in self.tickers:
            self.tickers['bm_id_forum'] = Ticker()
        ticker = self.tickers['bm_id_forum']
        e = ticker.elapsed(False)
        if e > 300 or not hasattr(self, '_bm_id_forum'):
            ticker.tick()
            jdata = self._load_data(self.urlp_idforum)
            bm = BijectiveMap()
            for k, v in jdata.items():
                bm[k] = v
            self._bm_id_forum = bm
        return self._bm_id_forum

    @property
    def ua_list(self):
        if not 'ua_list' in self.tickers:
            self.tickers['ua_list'] = Ticker()
        ticker = self.tickers['ua_list']
        e = ticker.elapsed(False)
        if e > 300 or not hasattr(self, '_ua_list'):
            ticker.tick()
            self._ua_list = self._load_data(self.urlp_ualist)
        return self._ua_list

    @property
    def addrs(self):
        if not hasattr(self, '_addrs'):
            self._addrs = self._load_data(self.urlp_addrs)
        return self._addrs
    
    @property
    def witch_domains(self):
        if not 'witch_domains' in self.tickers:
            self.tickers['witch_domains'] = Ticker()
        ticker = self.tickers['witch_domains']
        e = ticker.elapsed(False)
        if e > 30 or not hasattr(self, '_witch_domains'):
            ticker.tick()
            self._witch_domains = self._load_data(self.urlp_witch_domains)
        return self._witch_domains

    @property
    def witch_targets(self):
        if not 'witch_targets' in self.tickers:
            self.tickers['witch_targets'] = Ticker()
        ticker = self.tickers['witch_targets']
        e = ticker.elapsed(False)
        if e > 30 or not hasattr(self, '_witch_targets'):
            ticker.tick()
            self._witch_targets = self._load_data(self.urlp_witch_targets)
        return self._witch_targets
