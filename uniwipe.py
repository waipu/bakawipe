# -*- coding: utf-8 -*-
# -*- mode: python -*-
from sup.net import NetError
from wzworkers import WorkerInterrupt
from wipeskel import WipeSkel, WipeState, cstate
from beon import exc, regexp
from collections import ChainMap
import re


class UniWipe(WipeSkel):
    def __init__(self, forums, targets, sbjfun, msgfun, *args, **kvargs):
        self.sbjfun = sbjfun
        self.msgfun = msgfun
        self.forums = forums
        self.targets = (type(targets) == str and [('', targets)]
                        or type(targets) == tuple and list(targets)
                        or targets)
        super().__init__(*args, **kvargs)
        self.ignore_map = ChainMap(
            self.get_set('closed'), self.get_set('bumplimit'),
            self.get_set('bugged'), self.get_set('protected'),
            self.targets)

    def on_caprate_limit(self, rate):
        if not self.logined:
            self._capdata = (0, 0)
            return
        self.log.warning('Caprate limit reached, calling dologin() for now')
        self.dologin()
        # super().on_caprate_limit(rate)

    def comment_loop(self):
        for t in self.targets:
            self.schedule(self.add_comment, (t, self.msgfun()))
        if len(self.targets) == 0:
            self.schedule(self.scan_targets_loop)
        else:
            self.schedule(self.comment_loop)

    def add_comment(self, t, msg):
        # with cstate(self, WipeState.posting_comment):
        if True: # Just a placeholder
            try:
                # self.counter_tick()
                self.postmsg(t[1], msg, t[0])
            except exc.Success as e:
                self.counters['comments'] += 1
                self.w.sleep(self.comment_successwait)
            except exc.Antispam as e:
                self.w.sleep(self.comment_successwait)
                self.schedule(self.add_comment, (t, msg))
            except (exc.Closed, exc.UserDeny, exc.Bumplimit) as e:
                try:
                    self.targets.remove(t)
                except ValueError:
                    pass
                self.w.sleep(self.comment_successwait)
            except exc.Captcha as e:
                self.log.error('Too many wrong answers to CAPTCHA')
                self.switch_user()
                self.schedule(self.add_comment, (t, msg))
            except exc.UnknownAnswer as e:
                self.log.warn('%s: %s', e, e.answer)
                self.schedule(self.add_comment, (t, msg))
            except exc.Wait5Min as e:
                self.schedule(self.add_comment, (t, msg))
                self.schedule_first(self.switch_user)
            except exc.EmptyAnswer as e:
                self.log.info('Removing %s from targets and adding to bugged', t)
                self.add_waiting('bugged', t, 86400)
                try:
                    self.targets.remove(t)
                except ValueError as e:
                    pass
                self.w.sleep(self.errorwait)
            except exc.TopicDoesNotExist as e:
                self.log.info('Removing %s from targets and adding to bugged', t)
                self.add_waiting('bugged', t, 86400)
                try:
                    self.targets.remove(t)
                except ValueError as e:
                    pass
                self.w.sleep(self.errorwait)
            except exc.TemporaryError as e:
                self.schedule(self.add_comment, (t, msg))
                self.w.sleep(self.errorwait)
            except exc.PermanentError as e:
                try:
                    self.targets.remove(t)
                except ValueError as e:
                    pass
                self.w.sleep(self.errorwait)
            except UnicodeDecodeError as e:
                self.log.exception(e)
                self.w.sleep(self.errorwait)

    def forumwipe_loop(self):
        for f in self.forums.copy():
            if f[0] != '' or f[1] == '':
                # ignore users for now
                continue
            forum_id = self.get_forum_id(f[1])
            self.counter_tick()
            try:
                self.addtopic(self.msgfun(), self.sbjfun(), forum_id, f[0])
            except exc.Success as e:
                self.counters['topics'] += 1
                self.w.sleep(self.topic_successwait)
            except exc.Wait5Min as e:
                self.topic_successwait = self.topic_successwait + 0.1
                self.log.info('Wait5Min exc caught, topic_successwait + 0.1, cur: %f',
                    self.topic_successwait)
                self.w.sleep(self.topic_successwait)
            except exc.Captcha as e:
                self.log.error('Too many wrong answers to CAPTCHA')
                self.long_sleep(10)
            except exc.UnknownAnswer as e:
                self.log.warning('%s: %s', e, e.answer)
                self.w.sleep(self.errorwait)
            except exc.PermanentError as e:
                self.log.error(e)
                self.w.sleep(self.errorwait)
            except exc.TemporaryError as e:
                self.log.warn(e)
                self.w.sleep(self.errorwait)
        if len(self.forums) > 0:
            self.schedule(self.forumwipe_loop)
        else:
            self.schedule(self.wait_loop)

    def get_forum_id(self, name):
        return self.pc.forum_id_table.get_key(name)

    def get_targets(self):
        found_count = 0
        for user, forum in self.forums:
            targets = []
            self.log.debug('Scanning first page of the forum %s:%s', user, forum)
            page = self.site.get_page('1', forum, user)
            rxp = re.compile(regexp.f_sub_id.format(user, self.site.domain, forum))
            found = set(map(lambda x: (user, x[0]+x[1]), rxp.findall(page)))
            for t in found:
                if t in self.ignore_map:
                    continue
                targets.append(t)
            lt = len(targets)
            found_count += lt
            if lt > 0:
                self.log.info('Found %d new targets in forum %s:%s', lt, user, forum)
            else:
                self.log.debug('Found no new targets in forum %s:%s', user, forum)
            self.targets.extend(targets)
        return found_count

    def scan_targets_loop(self):
        with cstate(self, WipeState.scanning_for_targets):
            while len(self.targets) == 0:
                c = self.get_targets()
                if c == 0:
                    self.log.info('No targets found at all, sleeping for 30 seconds')
                    self.long_sleep(30)
            self.schedule(self.comment_loop)
        if len(self.forums) == 0:
            self.schedule(self.wait_loop)

    def wait_loop(self):
        if len(self.targets) > 0:
            self.schedule(self.comment_loop)
            return
        if len(self.forums) == 0:
            with cstate(self, WipeState.waiting_for_targets):
                while len(self.forums) == 0:
                    self.counter_tick()
                    self.w.sleep(1)
        self.schedule(self.scan_targets_loop)
        # self.schedule(self.forumwipe_loop)

    def _run(self):
        self.schedule(self.dologin)
        self.schedule(self.wait_loop)
        self.schedule(self.counter_ticker.tick)
        try:
            self.perform_tasks()
        except NetError as e:
            self.log.error(e)
        except WorkerInterrupt as e:
            self.log.warning(e)
        except Exception as e:
            self.log.exception(e)
        self.return_user()
# tw_flag = False
# if len(self.targets) > 0:
#     with cstate(self, WipeState.posting_comment):
#         while len(self.targets) > 0:
#             self.threadwipe_loop()
#     if not tw_flag:
#         tw_flag = True
# if tw_flag:
#     # Sleep for topic_successwait after last comment
#     # to prevent a wait spike
#     self.w.sleep(self.topic_successwait)
#     tw_flag = False
# with cstate(self, WipeState.posting_topic):
# self.forumwipe_loop()
