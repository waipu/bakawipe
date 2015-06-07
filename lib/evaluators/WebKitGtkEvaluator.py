# -*- coding: utf-8 -*-
# -*- mode: python -*-
import re
from webkit import WebView
import os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0, parentdir)
import exceptions as exc
from BeautifulSoup import BeautifulSoup

class Evaluator(object):
    _replacechars = u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьъэюя'
    
    def __init__(self, domain):
        self.domain = domain
        self.view = WebView()
        self.frame = self.view.get_main_frame()

    def set_html(self, html, base_uri=''):
        self.view.load_html_string(html, base_uri)

    def reset_html(self):
        self.set_html(u'<html><head></head><body></body></html>')

    def eval_js(self, script):
        self.view.execute_script(script)
        # returns None

    def get_html(self):
        self.eval_js('document.title=document.documentElement.innerHTML;')
        html = self.frame.get_title()
        return unicode(html)

    def find_script(self, page):
        soup = BeautifulSoup(page)
        script = soup.body.find(text=re.compile(u'dеobfuscate_html\(\)'))
        s = unicode(script)
        return s

    def deobfuscate_form(self, script):
        self.reset_html()
        self.eval_js(script)
        self.eval_js(u'captcha_div2.innerHTML=dеobfuscate_html();')

        return self.get_html()
    
    def _filter_markup(self, form):
        for c in self._replacechars: form = form.replace(c, '')
        return form

    def find_capair(self, form):
        '''Finds cahash on deobfuscated page.'''
        soup = BeautifulSoup(form)
        cahash = soup.body.find(attrs={'name': re.compile('cahash')})
        if cahash:
            caimg = soup.body.find(attrs=
                    {'src': re.compile(''.join(('\/a\d\.',
                                                self.domain,
                                                '\/i\/captcha\/')))})
            if caimg:
                return [str(cahash.get('value')), str(caimg.get('src'))]
            else:
                raise exc.PermanentError('caimg not found in form')
        else:
            raise exc.PermanentError('cahash not found in form')

    def solve_capage(self, page):
        s = self.find_script(page)
        if s:
            form = self.deobfuscate_form(s)
            return self.find_capair(self._filter_markup(form))
        else:
            raise exc.PermanentError('Obfuscated html not found in page')
