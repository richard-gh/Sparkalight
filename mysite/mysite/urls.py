from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
admin.autodiscover()

urlpatterns = patterns('',

	url(
	    r'^',
	    include('pet.urls',namespace = 'world')
	),

        url(
            r'^account/',
            include('django.contrib.auth.urls')
        ),
        url(
            r'^account/',
            include('accounts.urls', namespace="accounts")
        ),

        url(
            r'^secert/', 
            include(admin.site.urls)
        ),

        url(
            r'^message/',
            include('message.urls', namespace="message")
        ),



        url(
            r'^robots\.txt$', 
            lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")
        ),
        
        url(r'^admin/', include('admin_honeypot.urls')),


)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
