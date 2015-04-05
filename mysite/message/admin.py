from django.contrib import admin
from .models import *
from .forms import *

admin.site.register(Message)
admin.site.register(Thread)