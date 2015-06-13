# -*- coding: utf-8 -*-
'''Various cgi urls'''
addcomment = '/p/add_comment.cgi'
addtopic = '/p/add_topic.cgi'
deletecomment = '/p/delete_comment.cgi'
editcomment = '/p/edit_comment.cgi'
deletetopic = '/p/delete_topic.cgi' # Note: uses blog addr, not aN.
approvecomment = '/p/approve_comment.cgi'
emailit = '/p/email_it.cgi'
subscribe = '/p/subscribe.cgi'
addtofavourite = '/p/add_to_favourite.cgi'
addtoquotations = '/p/add_to_quotations.cgi'
reportspam = '/p/report_spam.cgi'
repost = '/p/repost.cgi'
addimage = '/p/add_image.cgi'
login = '/p/login.cgi'
logout = '/p/logout.cgi'
register = '/p/register.cgi'
setcookie = '/p/set_cookie.cgi'
validate_user_email = '/p/validate_user_email.cgi'
manageavatars = '/p/manage_avatars.cgi'
managebgm = '/p/manage_background_music.cgi'
ajax_getcomments = '/ajax/get_comments' # tid=topic&lcid=last comment&adc=dunno, 0.

addlink = '/p/add_link.cgi'
deletelink = '/p/delete_link.cgi'

sendmessage = '/p/send_message.cgi'
sendchatmessage = '/p/send_chat_message.cgi'
ajax_getmessages = '/ajax/get_messages' # ci=chatid?&co=?&m=1(message?)&login=&ch=
markasread = '/p/mark_as_read.cgi' # i=id
chats = '/e/chats/'
nicksent = '/c/p/%s-sent'
nickincoming = '/c/p/%s-incoming'
chatmsgs = '/c/p/%s'
