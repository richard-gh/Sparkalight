from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import User


urlpatterns = patterns('accounts.views',
   url(
       r'^forgot-password/$',
       'forgot_password',
       name="forgot-password"
   ),
   url(
       r'^change-email/$',
       'change_email',
       name="change_email"
   ),

   url(
       r'^Termination/$',
       'Termination',
       name="Termination"
   ),
)


urlpatterns += patterns('',
		url(r'^change-password/$', 'django.contrib.auth.views.password_change',name='change'), 
	(r'^password-changed/$', 'django.contrib.auth.views.password_change_done'),
(r'^password_reset_done/$', 'django.contrib.auth.views.password_reset_done'),

)
