# -*- coding: utf-8 -*-
import os, time
import pycurl
# from io import BytesIO
from threading import Lock, Event
from .other import encode_dict
from .special import *
from .workers import TerminableThread

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
        self.data = data
        super().__init__(*args, **kvargs)

class proxytype:
    http = pycurl.PROXYTYPE_HTTP
    socks4 = pycurl.PROXYTYPE_SOCKS4
    socks5 = pycurl.PROXYTYPE_SOCKS5

class RequestGenerator(object):
  # conlim = 3 # Retry limit
  # Timeouts (float seconds):
  contimeout = 10 # Connection
  timeout = 10 # Read
  # errtimeout = 3 # Sleep after error

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

  def __init__(self, mp):
    self.proxy = ''
    self.proxy_type = proxytype.socks5
    self.mp = mp

  def http_req(self, url, postdata=None, onlyjar=False, referer=None, encoding=None):
    '''PycURL get/post request.'''
    curl = pycurl.Curl()

    curl.setopt(pycurl.FOLLOWLOCATION, self.followlocation)
    curl.setopt(pycurl.FAILONERROR, self.failonerror)
    curl.setopt(pycurl.VERBOSE, self.verbose)

    curl.setopt(pycurl.CONNECTTIMEOUT, self.contimeout)
    curl.setopt(pycurl.TIMEOUT, self.timeout)

    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.ENCODING, self.accept_encoding)
    curl.setopt(pycurl.REFERER, (referer
                                 or self.def_referer
                                 or url))
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
        if encoding:
          raise TypeError('postdata is bytes and encoding specified')
        curl.setopt(pycurl.POSTFIELDS, postdata)
      elif type(postdata) == SpecialBytes:
          if encoding:
            if postdata.encoding == encoding:
              curl.setopt(pycurl.POSTFIELDS, bytes(postdata))
            else:
              curl.setopt(pycurl.POSTFIELDS,
                          postdata.decode().encode(encoding))
          else:
            curl.setopt(pycurl.POSTFIELDS, bytes(postdata))
      elif type(postdata) == SpecialString:
        curl.setopt(pycurl.POSTFIELDS, postdata.encode(encoding))
      elif type(postdata) == str:
        curl.setopt(pycurl.POSTFIELDS,
                    postdata.encode(encoding if encoding
                                    else self.default_encoding))
      elif type(postdata) == dict:
        _data = encode_dict(postdata,
                            to=encoding if encoding
                            else self.default_encoding)
        curl.setopt(pycurl.HTTPPOST, list(_data.items()))
      else:
        raise TypeError('Type %s is not supported' % type(postdata))
    else:
      curl.setopt(pycurl.HTTPGET, 1)

    if self.use_cookies:
        if self.use_cookiefile:
            if not os.path.isdir(self.cookies_root):
                os.makedirs(self.cookies_root)
            cookiefile = os.path.join(self.cookies_root, self.proxy+'.pot')
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

  def http_req_add(self, curl, decoding):
    buf = SpecialBytesIO()
    buf.encoding = decoding or self.default_decoding
    evt = Event()
    curl.setopt(pycurl.WRITEFUNCTION, buf.write)
    self.mp.add_handle(curl, evt)
    return evt, buf

  def check_errors(self, curl, data):
    if not curl in self.mp.errors:
      return
    code, errstr = self.mp.errors.pop(curl)
    if (code == pycurl.E_URL_MALFORMAT
        or code == pycurl.E_PARTIAL_FILE):
      raise NetError(code, errstr)
    elif (code == pycurl.E_COULDNT_RESOLVE_PROXY
        or code == pycurl.E_COULDNT_RESOLVE_HOST):
      raise DNSError(code, errstr)
    elif code == pycurl.E_HTTP_RETURNED_ERROR:
      raise HTTPError(curl.getinfo(pycurl.HTTP_CODE), data, code, errstr)
    elif (code == pycurl.E_COULDNT_CONNECT
          or code == pycurl.E_OPERATION_TIMEOUTED
          or code == pycurl.E_SEND_ERROR
          or code == pycurl.E_RECV_ERROR):
      raise ConnError(curl.getinfo(pycurl.OS_ERRNO), code, errstr)
    else:
      raise NetError(code, errstr)

  def http_req_perform(self, curl, decoding=None):
    evt, buf = self.http_req_add(curl, decoding)
    evt.wait()
    data = buf.s_getvalue()
    buf.close()
    self.check_errors(curl, data)
    return data

class MultiPerformer(TerminableThread):
  def __init__(self, *args, **kvargs):
    super().__init__(*args, **kvargs)
    self.curlm = pycurl.CurlMulti()
    self.new_handles = []
    self.events = {}
    self.errors = {}

  def add_handle(self, curl, evt):
      self.events[curl] = evt
      self.new_handles.append(curl)

  # def _add_handles(self):
  #   return added_handles

  def _run(self):
    while self.running.is_set():
      while self.running.is_set():
        for i in range(len(self.new_handles)):
          self.curlm.add_handle(self.new_handles.pop())
        ret, num_handles = self.curlm.perform()
        # while len(self.new_handles) > 0:
        if ret != pycurl.E_CALL_MULTI_PERFORM:
            break

      while self.running.is_set():
        num_msgs, oks, errors = self.curlm.info_read()
        for ch in oks:
          self.curlm.remove_handle(ch)
          self.events.pop(ch).set()
        for ch, ec, es in errors:
          self.curlm.remove_handle(ch)
          self.errors[ch] = (ec, es)
          self.events.pop(ch).set()
        if num_msgs == 0:
          break

      # if num_handles == 0:
      #   sys.stderr.write(' al:'+'1')
      #   while self.running.is_set():
      #     added_handles = self._add_handles()
      #     sys.stderr.write(' ah:'+str(added_handles))
      #     if added_handles > 0:
      #       break
      #     time.sleep(0.1)
      # else:
      #   sys.stderr.write(' al:'+'2')
      #   while self.running.is_set():
      #     added_handles = self._add_handles()
      #     sys.stderr.write(' ah:'+str(added_handles))
      #     if added_handles > 0:
      #       break
      #     ret = self.curlm.select(1.0)
      #     sys.stderr.write(' r:'+str(ret))
      #     if ret > 0:
      #       break
      while self.running.is_set():
        added_handles = 0
        while len(self.new_handles) > 0:
          added_handles += 1
          self.curlm.add_handle(self.new_handles.pop())
        if added_handles > 0:
          break

        if num_handles > 0:
          ret = self.curlm.select(1.0)
          if ret >= 0:
            break
        time.sleep(0.1)


def formfile(fileaddr):
    '''Form file in postdata.'''
    return (pycurl.FORM_FILE, fileaddr)
