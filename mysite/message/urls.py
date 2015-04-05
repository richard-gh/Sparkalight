from django.conf.urls import patterns, include, url
from django.contrib import admin



urlpatterns = patterns('',
 
         url(
            r'^message/$',
            'message.views.message',
            name = 'message',
        ),    
        url(
            r'^read/(?P<id>\d+)/$',
            'message.views.read',
            name = 'read',
        ),
        url(
            r'^readsentmessage/(?P<id>\d+)/$',
            'message.views.readsentmessage',
            name = 'readsentmessage',
        ),   
        url(
            r'^create/$',
            'message.views.Create',
            name = 'Create',
        ),  

        url(
            r'^read/trash/(?P<id>\d+)/$',
            'message.views.ReadDraft',
            name = 'ReadDraft',
        ), 
        url(
            r'^draft/$',
            'message.views.Draft',
            name = 'Draft',
        ), 
        url(
            r'^sentmessage/$',
            'message.views.sentmessage',
            name = 'sentmessage',
        ), 
)