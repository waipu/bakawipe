''' '''
# targetregexp = r'\/{forum}\/(\d*)-(\d*)\-[\w|\-]*([vb]-?i*-?r-?t|se(?:x|ks|kas)|eb(?:at|i)|t-?r-?a-?h|(?:-ja|ischu)-(?:m\-|j\-|zh\-|devushk|par(?:en|nja)|hozja)|ots[o|\-]s|rolevit|-sis[\-|e][kc]|v(?:-pop|du(?:i\-|va))|rabyn|droch|[ob]?liz(?:at\-|va[it])|hentai|shlju(?:hu|shk)|kisk[au]-(?:vsja|mokr)|do-orgazm|shali|min-?et|nakaz(?:iva|hi|at)|(?:parni|devushki)-kto-hochet|hoch(?:u|esh)-tak-)[\w|\-]*\-read\.shtml'
s_id = r'(\d+)\-(\d+)\-[\w\-]*(?:\-read)?\.[sz]?html'
s_topic = r'(\d+-\d+\-[\w|\-]*(?:\-read)?\.[sz]?html)'
s_uni = r'((\d+)-(\d+)\-[\w|\-]*(?:\-read)?\.[sz]?html)'

ud_prefix = r'http:\/\/(?:(\w+)\.)?(\w+\.\w+)\/(?:[\w._-]+\/)?'
udf_prefix = r'http:\/\/(?:(\w+)\.)?(\w+\.\w+)\/(?:([\w._-]+)\/)?'
sub_prefix = r'http:\/\/(?:{0}\.)?{1}\/(?:{2}\/)?'
ds_u_prefix = r'http:\/\/(?:(\w+)\.)?{0}\/(?:[\w._-]+\/)?'

f_udi = ud_prefix + s_id # -> (user, domain, (id1, id2))
f_udfi = udf_prefix + s_id # -> (user, domain, forum, (id1, id2))
f_udft = udf_prefix + s_topic # -> (user, domain, forum, topic)
f_udfti = udf_prefix + s_uni # -> (user, domain, forum, topic, (id1, id2))
f_sub_id = sub_prefix + s_id # -> (id1, id2)
f_sub_topic = sub_prefix + s_topic # -> (topic)

picregexp = r'(http\:\/\/i\d+\.{0}\/\d+\/\d+\/\d+\/\d+\/\d+\/Picture\d*\.jpe?g)'
chashregexp = r'value\=\'?(\w+)\'?.*?name\=\'?cahash\'?' # Regexp for captcha hash.

wait5min_register = r'Пожалуйста, подождите 5 минут и попробуйте зарегистрировать пользователя снова.'
wait5min_uni = r'<font color=ff0000>' # Stupid one, isn't it?
aregexp = r'http:\/\/a(\d)\.{0}\/i\/captcha\/' # Regexp for auth server.
var_login = r'var user_login = \'(\w*)\';' # Parse current login from js var.
imgregexp = r'\[image-\w*-\w*-http:\/\/a{0}.{1}\/i\/temp\/\d*\/[\w.]*\]' # wtf is this?
captchaurl = 'http://a{0}.{1}/i/captcha/{2}.png'
hashinmail = r'http:\/\/{0}\/p\/validate_user_email\.cgi\?p(?:=|&#61;)(\w+)'
show_link_options = r"showLinksOptions\(this,\s*?'\w+?',\s*?'(\d+?)',\s*?\d,\s*?\d,\s*?\d\)"
img_codes = r'(\[image-original-none-[\w:\.\/]+?\])'
deobfuscate_html = r'<script.*?>.*?dеobfuscate_html\s*?\(.*?\).*?<\/script>'
r302_found = r'302 Found'
r502_bad_gateway = r'502 Bad Gateway'


class getposts:
    addcomment = r"AddComment\s*?\(\s*?[\'\"](.+?)[\'\"]\s*?\)\s*?;"
    setlastcomment = r"setLastComment\s*?\(\s*?[\'\"]?(\d+?)[\'\"]?\s*?\)\s*?;"
    cookie = r"document.cookie\s*?=\s*?[\'\"](.*)[\'\"]\s*?;"
    runchecker = r"runChecker\s*?\(\s*?\)\s*?;"
