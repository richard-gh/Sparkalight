from django.conf.urls import url

import message.views

urlpatterns = [
    url(r'^message/$', message.views.message, name='message'),
    url(r'^read/(?P<id>\d+)/$', message.views.read, name='read'),
    url(r'^read_sent_message/(?P<id>\d+)/$', message.views.read_sent_message, name='read_sent_message'),
    url(r'^create/$', message.views.create, name='create'),
    url(r'^read/trash/(?P<id>\d+)/$', message.views.read_draft, name='read_draft'),
    url(r'^draft/$', message.views.draft, name='draft'),
    url(r'^sent_message/$', message.views.sent_message, name='sent_message'),
]
