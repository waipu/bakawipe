# -*- coding: utf-8 -*-
# -*- mode: python -*-
import re
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebPage
from BeautifulSoup import BeautifulSoup
import exceptions as exc

class Evaluator(object):
    _replacechars = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьъэюя'
    
    def __init__(self):
        self.app = QApplication([])
        self.page = QWebPage()
        self.frame = self.page.mainFrame()
        
    def __del__(self):
        del self.frame
        del self.page
        del self.app

    def set_html(self, html):
        self.frame.setHtml(html)
    
    def reset_html(self):
        self.set_html('<html><head></head><body></body></html>')

    def eval_js(self, script):
        res = self.frame.evaluateJavaScript(str(script))
        if type(res) == str:
            return res
        else:
            del res
    
    def get_html(self):
        res = self.frame.toHtml()
        s = str(res)
        del res
        return s

    def find_script(self, page):
        soup = BeautifulSoup(page)
        script = soup.body.find(text=re.compile('dеobfuscate_html\(\)'))
        s = str(script)
        return s

    def deobfuscate_form(self, script):
        self.reset_html()
        self.eval_js(script)
        self.eval_js('captcha_div2.innerHTML=dеobfuscate_html();')

        return self.get_html()
    
    def _filter_markup(self, form):
        for c in self._replacechars: form = form.replace(c, '')
        return form
    
    def find_capair(self, domain, form):
        '''Finds cahash on deobfuscated page.'''
        soup = BeautifulSoup(form)
        cahash = soup.body.find(attrs={'name': re.compile('cahash')})
        if cahash:
            caimg = soup.body.find(attrs=
                    {'src': re.compile(''.join(('\/a\d\.',
                                                domain,
                                                '\/i\/captcha\/')))})
            if caimg:
                return [str(cahash.get('value')), str(caimg.get('src'))]
            else:
                raise exc.PermanentError('caimg not found in form')
        else:
            raise exc.PermanentError('cahash not found in form')
    
    def solve_capage(self, domain, page):
        s = self.find_script(page)
        if s:
            if type(domain) == bytes: domain = domain.decode('utf-8')
            form = self._filter_markup(self.deobfuscate_form(s))
            return self.find_capair(domain, form)
        else:
            raise exc.PermanentError('Obfuscated html not found in page')
