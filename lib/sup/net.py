# -*- coding: utf-8 -*-
# -*- mode: python -*-
import os
import pycurl
from multipledispatch import adispatch
from .other import encode_dict
from .special import *

NoneType = type(None)

class NetError(Exception):
    def __init__(self, ec, *args, **kvargs):
        self.ec = ec
        super().__init__(*args, **kvargs)

class ProxyError(NetError):
    pass
class DNSError(NetError):
    pass
class ConnError(NetError):
    def __init__(self, code=None, *args, **kvargs):
        self.code = code
        super().__init__(*args, **kvargs)

class HTTPError(NetError):
    def __init__(self, code=None, data=None, *args, **kvargs):
        self.code = code
        self.buf = data
        super().__init__(*args, **kvargs)

    @property
    def data(self) -> bytes:
        if hasattr(self.buf, 's_getvalue'):
            return self.buf.s_getvalue()
        elif hasattr(self.buf, 'getvalue'):
            return self.buf.getvalue()
        else:
            return self.buf.read()

class proxytype:
    http = pycurl.PROXYTYPE_HTTP
    socks4 = pycurl.PROXYTYPE_SOCKS4
    socks5 = pycurl.PROXYTYPE_SOCKS5

class RequestPerformer(object):
  contimeout = 10 # Connection
  timeout = 10 # Read

  followlocation = False
  failonerror = True
  verbose = False
  default_encoding = 'utf-8'
  default_decoding = 'utf-8'

  accept_encoding = 'gzip, deflate'
  customheaders = [
    'Connection: keep-alive',
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language: en-US,en;q=0.5',
    'Cache-Control: no-cache',
    'Pragma: no-cache',
  ]
  useragent = 'sup.net/PycURL'
  def_referer = ''
  use_cookies = True
  use_cookiefile = True
  cookies_root = 'cookies'
  cookie = ''

  def __init__(self):
    self.proxy = ''
    self.proxy_type = proxytype.socks5
    self.cookiefname = None

  @adispatch()
  def http_req_create(self, url: str, postdata: SpecialBytes,
    onlyjar: bool = False, referer: (str, NoneType) = None,
    encoding: (str, NoneType) = None):
    if encoding and not postdata.encoding == encoding:
        postdata = postdata.decode().encode(encoding)
    else:
        postdata = bytes(postdata)
    return self.http_req_create(url, postdata, onlyjar, referer)

  @adispatch()
  def http_req_create(self, url: str, postdata: SpecialString,
    onlyjar: bool = False, referer: (str, NoneType) = None,
    encoding: (str, NoneType) = None):
    return self.http_req_create(url, postdata.encode(encoding), onlyjar, referer)

  @adispatch()
  def http_req_create(self, url: str, postdata: str,
    onlyjar: bool = False, referer: (str, NoneType) = None,
    encoding: (str, NoneType) = None):
    return self.http_req_create(url,
        postdata.encode(encoding if encoding else self.default_encoding),
        onlyjar, referer)

  @adispatch()
  def http_req_create(self, url: str, postdata: dict,
    onlyjar: bool = False, referer: (str, NoneType) = None,
    encoding: (str, NoneType) = None):
    return self.http_req_create(url,
        list(encode_dict(postdata,
          to=encoding if encoding else self.default_encoding).items()),
        onlyjar, referer)

  @adispatch()
  def http_req_create(self, url: str, postdata: (bytes, list, NoneType) = None,
    onlyjar: bool = False, referer: (str, NoneType) = None,
    encoding: NoneType = None) -> pycurl.Curl:
    return self.http_req_create(url, postdata, onlyjar, referer)

  @adispatch()
  def http_req_create(self, url: str, postdata: (bytes, list, NoneType) = None,
    onlyjar: bool = False, referer: (str, NoneType) = None) -> pycurl.Curl:
    '''PycURL get/post request.'''
    curl = pycurl.Curl()

    curl.setopt(pycurl.FOLLOWLOCATION, self.followlocation)
    curl.setopt(pycurl.FAILONERROR, self.failonerror)
    curl.setopt(pycurl.VERBOSE, self.verbose)

    curl.setopt(pycurl.CONNECTTIMEOUT, self.contimeout)
    curl.setopt(pycurl.TIMEOUT, self.timeout)

    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.ENCODING, self.accept_encoding)
    curl.setopt(pycurl.REFERER, (referer or self.def_referer or url))
    self.useragent and curl.setopt(pycurl.USERAGENT, self.useragent)
    self.customheaders and curl.setopt(pycurl.HTTPHEADER, self.customheaders)

    if self.proxy:
      curl.setopt(pycurl.PROXYTYPE, self.proxy_type)
      curl.setopt(pycurl.HTTPPROXYTUNNEL, 1)
      curl.setopt(pycurl.PROXY, self.proxy)
    else:
      curl.setopt(pycurl.HTTPPROXYTUNNEL, 0)
      curl.setopt(pycurl.PROXY, '')

    if postdata:
      curl.setopt(pycurl.POST, 1)
      if type(postdata) == bytes:
        curl.setopt(pycurl.POSTFIELDS, postdata)
      elif type(postdata) == list:
        curl.setopt(pycurl.HTTPPOST, postdata)
      else:
        raise TypeError('Type %s is not supported' % type(postdata))
    else:
      curl.setopt(pycurl.HTTPGET, 1)

    if self.use_cookies:
        if self.use_cookiefile:
            if not os.path.isdir(self.cookies_root):
                os.makedirs(self.cookies_root)
            if self.cookiefname:
                cookiefile = os.path.join(self.cookies_root, self.cookiefname+'.pot')
            else:
                cookiefile = os.path.join(self.cookies_root,
                            (self.proxy if self.proxy else 'noproxy')+'.pot')
            curl.setopt(pycurl.COOKIEJAR, cookiefile)
            if onlyjar:
                curl.setopt(pycurl.COOKIELIST, 'ALL')
            else:
                curl.setopt(pycurl.COOKIEFILE, cookiefile)
        else:
            curl.setopt(pycurl.COOKIEFILE, '')
            curl.setopt(pycurl.COOKIE, self.cookie)
    else:
        curl.setopt(pycurl.COOKIEJAR, '')
        curl.setopt(pycurl.COOKIEFILE, '')
        curl.setopt(pycurl.COOKIE, '')
    return curl

  def http_req_perform(self, curl: pycurl.Curl, writefun: object) -> None:
    curl.setopt(pycurl.WRITEFUNCTION, writefun)
    try:
        curl.perform()
    except pycurl.error as e:
      code = e.args[0]; errstr = e.args[1]
      if (code == pycurl.E_URL_MALFORMAT
          or code == pycurl.E_PARTIAL_FILE):
        raise NetError(code, errstr)
      elif (code == pycurl.E_COULDNT_RESOLVE_PROXY
            or code == pycurl.E_COULDNT_RESOLVE_HOST):
        raise DNSError(code, errstr)
      elif code == pycurl.E_HTTP_RETURNED_ERROR:
        raise HTTPError(curl.getinfo(pycurl.HTTP_CODE), None, code, errstr)
      elif (code == pycurl.E_COULDNT_CONNECT
            or code == pycurl.E_OPERATION_TIMEOUTED
            or code == pycurl.E_SEND_ERROR
            or code == pycurl.E_RECV_ERROR):
        raise ConnError(curl.getinfo(pycurl.OS_ERRNO), code, errstr)
      else:
        raise NetError(code, errstr)

  def http_req_multiperform(self, curls):
    pass

  def http_req(self, url, postdata=None, onlyjar=False, referer=None,
               encoding=None, decoding=None) -> SpecialBytes:
    curl = self.http_req_create(url, postdata, onlyjar, referer, encoding)
    if self.verbose:
        print(repr(postdata))
    buf = SpecialBytesIO()
    buf.encoding = decoding or self.default_decoding
    try:
      self.http_req_perform(curl, buf.write)
    except HTTPError as e:
      e.buf = buf
      raise e
    finally:
      curl.close()
    data = buf.s_getvalue()
    buf.close()
    if self.verbose:
        print(repr(data))
    return data

def formfile(fileaddr) -> tuple:
    '''Form file in postdata.'''
    return (pycurl.FORM_FILE, fileaddr)
