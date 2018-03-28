from django.conf.urls import url
import accounts.views
import django.contrib.auth.views

urlpatterns = [
    url(r'^forgot-password/$', accounts.views.forgot_password, name="forgot-password"),
    url(r'^change-email/$', accounts.views.change_email, name="change_email"),
    url(r'^Termination/$', accounts.views.Termination, name="Termination"),
    url(r'^change-password/$', django.contrib.auth.views.password_change, name='change'),
    url(r'^password-changed/$', django.contrib.auth.views.password_change_done),
    url(r'^password_reset_done/$', django.contrib.auth.views.password_reset_done),
]
