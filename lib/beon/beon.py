# -*- coding: utf-8 -*-
import re
from threading import Lock
from BeautifulSoup import BeautifulSoup
from random import randint
from sup import formquery, formfile, urlencode, construct_url, randstr
from . import url, postdata, rsp, exc, regexp

class Beon(object):
  url = url
  rsp = rsp
  commentenc = 'utf8'
  topicenc = 'cp1251'
  chatenc = 'utf8' # ?
  ajaxenc = 'utf8'
  regenc = 'cp1251'
  siteenc = 'cp1251'
  refound = re.compile(regexp.r302_found) # TODO: use something more reliable
  bad_gateway = re.compile(regexp.r502_bad_gateway)
  deobfuscate_html = re.compile(regexp.deobfuscate_html)

  def __init__(self, domain, req_fun=None):
    self.domain = domain # Yep, domain. beon.ru/ltalk.ru/etc
    self.ptforum = 'anonymous' # Default plaintext forum
    self.ud = {} # Current user data
    self.logined = True # Logined (cookie) mode.
    self.login_lock = Lock()
    self.ref = 'http://'+randstr(3, 6)+'.'+domain+'/' # Referer in postdata.
    self.a = str(randint(0, 6)) # Auth server.

    self.req = req_fun

  def addcomment(self, topicid, text, user=None, logined=True, **kvargs):
    '''Post message to topic'''
    tpair = (user, topicid)
    p = postdata.addcomment.copy()
    p.update({'topic_id': topicid,
              'r': '',
              'message': text})
    if self.logined == True and logined:
      p['user_type'] = ''
    elif self.postuser != None:
      p['user_type'] = 'notanon'
      p['alogin'] = self.postuser
      if self.postpass != None:
        p['password'] = self.postpass
        p['authorize'] = 'on'
    else:
      p['user_type'] = 'anonymous'
    if user:
      p['blog_login'] = user
    p.update(kvargs)
    s = urlencode(p, to=self.siteenc).encode(self.siteenc)
    s+= ('&add='+'Прoкoммeнтировaть Ctrl+Enter').encode(self.siteenc)
    u = (construct_url(user+'.'+self.domain, (url.addcomment,)) if user
           else construct_url(self.domain, (url.addcomment,)))
    rec = self.req(u, s).decode()
    if self.deobfuscate_html.search(rec):
      raise exc.Captcha(rec, 'We got a captcha!',
                        tpair, p,
                        catry=(int(kvargs['catry'])+1 if 'catry' in kvargs else 1))
    elif re.search(regexp.wait5min_uni, rec):
      raise exc.Wait5Min('We`re banned for 5 minutes', tpair, rec, p)
    elif self.bad_gateway.search(rec):
      raise exc.BadGateway('502 Bed Gateway', tpair, rec, p)
    else:
      raise exc.Success('Probably posted, or unknown answer', tpair, rec, p)

  def addcommentfin(self, cahash, cacode, *args, catry=1, **kvargs):
    return self.addcomment(*args, cahash=cahash, cacode=cacode, catry=str(catry),
      **kvargs)

  def ajax_addcomment(self, topicid, text, user=None, logined=True, **kvargs):
    '''Post message to topic'''
    tpair = (user, topicid)
    p = postdata.addcomment.copy()
    p.update({'ajax': '1',
              'topic_id': topicid,
              'r': '',
              'message': text})
    if self.logined is True and logined:
      p['user_type'] = ''
    elif self.postuser is not None:
      p['user_type'] = 'notanon'
      p['alogin'] = self.postuser
      if self.postpass is not None:
        p['password'] = self.postpass
        p['authorize'] = 'on'
    else:
      p['user_type'] = 'anonymous'
    if user:
      p['blog_login'] = user
    p.update(kvargs)
    s = urlencode(p, to=self.commentenc).encode(self.commentenc)
    s += ('&add='+'Прoкoммeнтировaть Ctrl+Enter').encode(self.commentenc)
    u = (construct_url(user+'.'+self.domain, (url.addcomment,)) if user
        else construct_url(self.domain, (url.addcomment,)))
    rec = self.req(u, s).decode()
    if not rec:
        raise exc.EmptyAnswer('Empty response on ajax_addcomment to %s:%s',
            tpair, rec, p)
    if rec == rsp.succes or rec == rsp.othersucces:
      raise exc.Success("post in %s:%s was posted", tpair, rec, p)
    elif rec == rsp.redir:
      raise exc.Redir("%s:%s: rec redir", tpair, rec, s)
    elif rec == rsp.antispam:
      raise exc.Antispam("%s:%s: Antispam error", tpair, rec, p)
    elif (rec == rsp.useronlyregistred if user
          else rec == rsp.onlyregistred):
      raise exc.GuestDeny("%s:%s: Guests can't post here", tpair, rec, s)
    elif ((rec == rsp.useronlyfriend
           or rec == rsp.useronlymember
           or rec == rsp.useronlysome
           or rec == rsp.useronlyvip
           or rec == rsp.useropblacklisted) if user
         else (rec == rsp.onlyfriend
              or rec == rsp.onlysome
              or rec == rsp.onlyvip
              or rec == rsp.opblacklisted)):
      raise exc.UserDeny("%s:%s: This user can't post here", tpair, rec, p)
    elif (rec == rsp.userbumplimit if user
          else rec == rsp.bumplimit):
      raise exc.Bumplimit("%s:%s: Bumplimit reached", tpair, rec, p)
    elif (rec == rsp.cantadd or
          rec == rsp.userclosed if user
          else rec == rsp.closed):
      raise exc.Closed("%s:%s is closed", tpair, rec, p)
    elif self.refound.search(rec):
      raise exc.TopicDoesNotExist("Topic %s:%s does not exist", tpair, rec, p)
    else:
      raise exc.UnknownAnswer("%s:%s: Unknown answer", tpair, rec, p)

  def delcomment(self, topic_id, comment_id, user=None):
    '''Delete comment from topic.'''
    query = formquery(topic_id=topic_id, comment_id=comment_id)
    u = (construct_url(user+'.'+self.domain, (url.deletecomment,)) if user
        else construct_url(self.domain, (url.deletecomment,)))
    return self.req('?'.join((u, query))).decode()

  def dellink(self, link_id, user=None):
    '''Delete link.'''
    query = formquery(link_id=link_id)
    u = (construct_url(user+'.'+self.domain, (url.deletelink,)) if user
        else construct_url(self.domain, (url.deletelink,)))
    return self.req('?'.join((u, query))).decode()

  def reportspam(self, spam_type, spam_id, topic_id=None, user=None):
    '''Report spam. Types are: topic blog_topic comment blog_comment.'''
    query = (spam_type == 'topic' or spam_type == 'blog_topic'
             and formquery(type=spam_type, id=spam_id)
             or spam_type == 'comment' or spam_type == 'blog_comment'
             and topic_id
             and formquery(type=spam_type, id=spam_id, topic_id=topic_id)
             or False)
    u = (construct_url(user+'.'+self.domain, (url.reportspam,)) if user
        else construct_url(self.domain, (url.reportspam,)))
    return (query and self.req('?'.join((u, query))).decode())

  def get_page(self, page, forum=None, user=None):
    '''Get page from user/forum.'''
    if forum is None:
        forum = self.ptforum # '' is correct.
    u = (construct_url(user+'.'+self.domain, (page+'.html',)) if user
        else construct_url(self.domain, (forum, page+'.html')))
    return self.req(u).decode()

  def getlinks(self, user):
    '''Get links from user.'''
    u = construct_url(user+'.'+self.domain, ('links', ''))
    page = self.req(u).decode()
    return re.findall(regexp.show_link_options, page)

  def uploadimg(self, images, size='original', position='none'):
    p = postdata.uploadimg.copy()
    p.update({'image_url0': '',
              'position': position,
              'size': size})
    if isinstance(images, str):
      p.update({'image_file0': formfile(images)})
    else:
      for i in range((len(images))):
        p.update({''.join(('image_file', str(i))): formfile(images.pop())})
    u = construct_url('a'+self.a+'.'+self.domain, (url.addimage,))
    res = self.req(u, p).decode()

    codes = set(re.findall(regexp.img_codes, res))
    print(res)
    print(codes)
    return codes

  def uploadavatar(self, avatar_id, fileaddr):
    p = postdata.uploadavatar.copy()
    p.update({'avatar_id': avatar_id,
              'image_file': formfile(fileaddr)})
    u = construct_url(self.domain, (url.manageavatars,))
    if self.logined:
        return self.req(u, p).decode()
    else:
        raise exc.UsageError('You must be logined to change your avatar')

  def uploadbgm(self, bgm_file):
    p = postdata.uploadbgm.copy()
    p.update({'mp3_file': formfile(bgm_file)})
    u = construct_url(self.domain, (url.managebgm,))
    if self.logined:
       return self.req(u, p).decode()
    else:
        raise exc.UsageError('You must be logined to change your bgm')

  def getposts(self, topicurl, forum=None, user=None):
    '''Get posts from topic.'''
    if forum is None:
       forum = self.ptforum
    u = (construct_url(user+'.'+self.domain, (forum, topicurl)) if user
        else construct_url(self.domain, (forum, topicurl)))
    return self.req(u).decode()

  def getpostsdict(self, topicurl, forum=None, user=None):
    '''Get posts from topic. Returns posts in dict.'''
    if forum is None:
       forum = self.ptforum
    u = (construct_url(user+'.'+self.domain, (forum, topicurl)) if user
        else construct_url(self.domain, (forum, topicurl)))
    rec = self.req(u).decode()
    if rec:
      from .BeautifulSoup import BeautifulSoup
      _comments = BeautifulSoup(rec).body(attrs={'class': 'commentbg'})
      _commentsdict = {}
      for comment in _comments:
        _trs = comment.findAll('tr')
        _commentsdict.update({_trs[1].td.a['name']:
                              _trs[2].find(colspan='2')})
      return _commentsdict
    else:
        return rec

  def ajax_getposts(self, tid, lcid, adc='0', user=''):
    '''
    tid: topic id
    lcid: last comment id
    adc: ?
    '''
    p = postdata.ajax_getposts.copy()
    p.update({'tid': tid.lstrip('0'),
              'lcid': lcid,
              'adc': adc})
    s = urlencode(p, to=self.ajaxenc).encode(self.ajaxenc)
    u = (construct_url(user+'.'+self.domain, (url.ajax_getcomments,)) if user
        else construct_url(self.domain, (url.ajax_getcomments,)))
    rsp = self.req(u, s).decode()
    data = {'posts': [], 'lcid': None, 'cookie': None, 'runChecker': None}
    data['posts'] = re.findall(regexp.getposts.addcomment, rsp)
    try:
      data['lcid'] = int(re.findall(regexp.getposts.setlastcomment, rsp).pop())
    except IndexError:
      if len(rsp) == 0:
        raise exc.UnknownAnswer('Empty response', (tid, lcid), rsp, p)
    try:
      data['cookie'] = re.findall(regexp.getposts.cookie, rsp).pop()
    except IndexError:
      pass
    if re.search(regexp.getposts.runchecker, rsp):
      data['runChecker'] = True
    else:
      data['runChecker'] = False
    return data

  def parse_posts(self, posts):
    '''Parses posts from table/ajax_getposts.'''
    rposts = []
    for post in posts:
      soup = BeautifulSoup(post)
      rposts.append({
          'date': soup.fetch('tr')[1].fetch('font')[0].text,
          'link': soup.fetch('tr')[1].fetch('font')[1].a['href'],
          'html': soup.fetch('tr')[2].fetch('td')[1],
          'plaintext': soup.fetch('tr')[2].fetch('td')[1].text,
      })
    return rposts

  def addtopicinc(self, text, forumid='122', subject='', user=None, **kvargs):
    '''Add topic to forum - initial stage.'''
    tpair = (forumid, user)
    p = postdata.addtopic.copy()
    p.update({'subject': subject,
              'forum_id': forumid,
              'message': text})
    if self.logined is True:
      p['user_type'] = 'logined'
    elif self.postuser is not None:
      p['user_type'] = 'notanon'
      p['alogin'] = self.postuser
      if self.postpass is not None:
        p['password'] = self.postpass
        p['authorize'] = 'on'
    else:
      p['user_type'] = 'anonymous'
    p.update(kvargs)
    s = urlencode(p, to=self.topicenc)
    u = (construct_url(user+'.'+self.domain, (url.addtopic,)) if user
        else construct_url('a'+self.a+'.'+self.domain, (url.addtopic,)))
    rec = self.req(u, s).decode()
    if rec == '':
        raise exc.Success('Topic to %s:%s posted: empty response', tpair, rec, p)
    elif self.deobfuscate_html.search(rec):
      raise exc.Captcha(rec, 'We got a captcha on addtopicinc to %s:%s',
                        tpair, p, catry=1)
    elif re.search(regexp.wait5min_uni, rec):
      raise exc.Wait5Min('Requested to wait 5 min on addtopicinc to %s:%s', tpair, rec, p)
    elif self.bad_gateway.search(rec):
      raise exc.BadGateway('502 Bed Gateway', tpair, rec, p)
    else:
      raise exc.UnknownAnswer('Unknown answer on addtopicfin to %s:%s', tpair, rec, p)

  def addtopicfin(self, cahash, cacode,
                  text, forumid='122', subject='', user=None, catry='1', **kvargs):
    '''Add topic to forum - final stage.'''
    tpair = (forumid, user)
    p = postdata.addtopic.copy()
    p.update({'stage': 'final',
              'catry': str(catry),
              'forum_id': forumid,
              'subject': subject,
              'message': text,
              'cahash': cahash,
              'cacode': cacode})
    if self.logined is True:
      p['user_type'] = 'logined'
    elif self.postuser is not None:
      p['user_type'] = 'notanon'
      p['alogin'] = self.postuser
      if self.postpass is not None:
        p['password'] = self.postpass
        p['authorize'] = 'on'
    else:
      p['user_type'] = 'anonymous'
    p.update(kvargs)
    try:
      s = urlencode(p, to=self.topicenc)
    except TypeError:
      print(p)
      raise
    u = (construct_url('a'+self.a+'.'+self.domain, (url.addtopic,)) if user
        else construct_url('a'+self.a+'.'+self.domain, (url.addtopic,)))
    rec = self.req(u, s).decode()
    if rec == '':
      raise exc.Success('Topic to %s:%s posted: empty response', tpair, rec, p)
    elif self.deobfuscate_html.search(rec):
      raise exc.Captcha(rec, 'We got a captcha on addtopicfin to %s:%s',
                        tpair, p, catry=catry+1)
    elif re.search(regexp.wait5min_uni, rec):
      raise exc.Wait5Min('Requested to wait 5 min on addtopicinc to %s:%s', tpair, rec, p)
    elif self.bad_gateway.search(rec):
      raise exc.BadGateway('502 Bed Gateway', tpair, rec, p)
    else:
      raise exc.UnknownAnswer('Unknown answer on addtopicfin to %s:%s', tpair, rec, p)

  def logininc(self, login, passwd, **kvargs):
    '''Log in. Initial stage.'''
    p = postdata.login.copy()
    p.update({'login': login,
              'pass': passwd,
              'r': ''})
    p.update(kvargs)
    s = urlencode(p, to=self.regenc)
    rec = self.req(construct_url(self.domain, (url.login,)), s).decode()
    if rec:
      if self.deobfuscate_html.search(rec):
        raise exc.Captcha(rec, 'We got a captcha on logininc as %s:%s',
                          (login, passwd), p, catry=1)
      elif self.refound.search(rec):
        raise exc.Success('logined as %s:%s', (login, passwd), rec, p)
      elif self.bad_gateway.search(rec):
        raise exc.BadGateway('502 Bad Gateway', (login, passwd), rec, p)
      else:
        raise exc.InvalidLogin('Invalid login %s:%s', (login, passwd), rec, s)
    else:
      raise exc.EmptyAnswer('Empty response on logininc as %s:%s',
        (login, passwd), rec, p)

  def loginfin(self, cahash, cacode,
               login, passwd, catry='1', **kvargs):
    '''Log in. Final stage.'''
    p = postdata.login.copy()
    p.update({'stage': 'final',
              'login': login,
              'pass': passwd,
              'r': '',
              'cahash': cahash,
              'cacode': cacode,
              'catry': str(catry)})
    p.update(kvargs)
    s = urlencode(p, to=self.regenc)
    rec = self.req(construct_url(self.domain, (url.login,)), s).decode()
    if rec:
      if self.deobfuscate_html.search(rec):
        raise exc.Captcha(rec, 'We got a captcha on loginfin as %s:%s',
                          (login, passwd), p, catry=catry+1)
      elif self.refound.search(rec):
        raise exc.Success('logined as %s:%s', (login, passwd), rec, p)
      elif self.bad_gateway.search(rec):
        raise exc.BadGateway('502 Bad Gateway', (login, passwd), rec, p)
      else:
        raise exc.InvalidLogin('Invalid login %s:%s', (login, passwd), rec, s)
    else:
      raise exc.EmptyAnswer('Empty response on loginfin as %s:%s',
        (login, passwd), rec, p)

  def logout(self):
    rec = self.req(construct_url(
        self.domain, (url.logout,), query={'r': self.ref})).decode()
    if rec:
      if self.refound.search(rec):
          raise exc.Success('Logged out', (), rec)
      raise exc.UnknownAnswer('Unknown answer on logout', (), rec)
    else:
        raise exc.EmptyAnswer('Empty response on logout', (), rec)

  def reginc(self, login, passwd, name, email, **kvargs):
    '''Registration. Initial stage.'''
    p = postdata.register.copy()
    p.update({'r': '',
              'login': login,
              'password': passwd,
              'password2': passwd,
              'name': name,
              'email': email,
              })
    p.update(kvargs)
    s = urlencode(p, to=self.regenc)
    rec = self.req(
        construct_url('a'+self.a+'.'+self.domain, (url.register,)),
        s).decode()
    if rec:
      if self.deobfuscate_html.search(rec):
        raise exc.Captcha(rec, 'We got a captcha on reginc as %s:%s',
                          (login, passwd), s, catry=1)
      elif self.refound.search(rec):
        raise exc.UnknownAnswer('302 Found received, which is wrong. onlyjar=True?',
                                (login, passwd), rec, s)
      elif self.bad_gateway.search(rec):
        raise exc.BadGateway('502 Bad Gateway', (login, passwd), rec, s)
      else:
        raise exc.UnknownAnswer('Can`t register %s:%s', (login, passwd), rec, s)
    else:
      raise exc.EmptyAnswer('Empty response on reginc as %s:%s', (login, passwd), rec, s)

  def regfin(self, cahash, cacode, login, passwd, name, email, catry='1', **kvargs):
    '''Registration. Final stage.'''
    p = postdata.register.copy()
    p.update({'r': '',
              'login': login,
              'password': passwd,
              'password2': passwd,
              'name': name,
              'email': email,
              'cahash': cahash,
              'cacode': cacode})
    p.update(kvargs)
    s = urlencode(p, to=self.regenc)
    rec = self.req(
        construct_url('a'+self.a+'.'+self.domain, (url.register,)),
        s).decode()
    if rec:
      if self.deobfuscate_html.search(rec):
        raise exc.Captcha(rec, 'We got a captcha on regfin as %s:%s',
                          (login, passwd), s, catry=catry+1)
      elif self.refound.search(rec):
        raise exc.Success('Registred', (login, passwd), rec, s)
      elif self.bad_gateway.search(rec):
        raise exc.BadGateway('502 Bad Gateway', (login, passwd), rec, s)
      elif re.search(regexp.wait5min_register, rec):
        raise exc.Wait5Min('We need to wait 5 min before retrying',
            (login, passwd), rec, s)
      else:
        raise exc.EmptyAnswer('Empty response on regfin as %s:%s',
            (login, passwd), rec, s)
    else:
      raise exc.EmptyAnswer('rec empty', (login, passwd), rec, s)

  def validate_email_inc(self, **kvargs):
    if not self.logined:
      raise exc.UsageError('You must be logined to request validation mail')
    p = postdata.validate_email_inc.copy()
    p.update(kvargs)
    u = construct_url(self.domain, (url.validate_user_email,), p)
    rec = self.req(u).decode()
    if rsp.mail_success in rec:
      raise exc.Success('Validation mail requested', '', rec)
    elif rsp.mail_server_connection_error in rec:
      raise exc.BadGateway('Error while connecting to the server', '', rec)
    else:
      raise exc.UnknownError('No flag in answer', '', rec)

  def validate_email_fin(self, hash_, **kvargs):
    if not self.logined:
      raise exc.UsageError('You must be logined to validate email address')
    p = postdata.validate_email_fin.copy()
    p['p'] = hash_
    p.update(kvargs)
    u = construct_url(self.domain, (url.validate_user_email,), p)
    rec = self.req(u).decode()
    raise exc.Success('Email address validated', hash_, rec) # No validation for now

  def ajax_sendmessage(self, recipient, subject, message, **kvargs):
    '''Post message to chat.'''
    p = postdata.sendmessage.copy()
    p.update({'ajax': '1',
              'send': '1',
              'recipient': recipient,
              'subject': subject,
              'message': message})
    p.update(kvargs)
    s = urlencode(p, to=self.chatenc).encode(self.chatenc)
    rec = self.req(construct_url('a'+self.a+'.'+self.domain,
        (url.sendchatmessage if recipient.startswith('chat_')
        else url.sendmessage)), s).decode()
    if rec == rsp.chatsucces % recipient:
      raise exc.Success("Message to %s sent", recipient, rec, s)
    elif rec == rsp.chatredir:
      raise exc.Redir("Recvd redir, captcha handling is not implemented",
        recipient, rec, s)
    else:
      raise exc.UnknownAnswer("Unknown answer on ajax_sendmessage to %s",
        recipient, rec, s)

  # def getmessages

  def getonline_count(self):
    '''Returns (online, went_offline).'''
    u = construct_url(self.domain, ('online', ''))
    page = self.req(u).decode()
    try:
      return [re.findall(r, page)[0] for r in ('Сейчас\s+?на\s+?сайте\s+?(\d+)\s+?',
                  'Только\s+?что\s+?с\s+?сайта\s+?(?:ушёл|ушли)\s+?(\d+)\s+?')]
    except IndexError:
      raise exc.UnknownAnswer('UnknownAnswer', 'online_count', page)

  def find_user_status(self, page):
    '''Finds user status in page'''
    # font.m1:nth-child(41)
    # font.m2:nth-child(42)
    try:
      soup = BeautifulSoup(page)
      status = soup.body.find(text=re.compile('Статус: '))
      print(status)
    except Exception:
      raise
      # raise exc.UnknownAnswer('UnknownAnswer', 'user_status', page)


# Other fun defuns.


def addimg(link, size='original', position='none'):
  '''Add tags to img link.'''
  return ''.join(('[', '-'.join(('image', size, position, link)), ']'))


def make_topic_url(domain, id_, forum='', user=''):
    if len(id_) > 3:
        split_id = (id_[:-3], id_[-3:])
    else:
        split_id = ('0', id_)
    u = construct_url((user+'.'+domain) if user else domain,
                      (forum, '-'.join(split_id+('.zhtml' if user else '.shtml',))))
    return u
