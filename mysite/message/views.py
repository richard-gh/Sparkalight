from .forms import *
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.http import Http404
from django import forms
from .forms import *
from .models import *
from itertools import chain
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Q
from sorl.thumbnail import get_thumbnail
from el_pagination.decorators import page_template
from mysite import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import json
from django.http import HttpResponse
from django.template import RequestContext
import math
from django.shortcuts import render, get_object_or_404, redirect
from friendship.models import Friend, Follow, FriendshipRequest
from sorl.thumbnail import delete


@login_required
def message(request):
    posts = Message.objects.filter(recipient=request.user, sentmessage=True, is_deleted_by_recipient=False).order_by(
        "-created")
    person = Person.objects.get(username=request.user, )
    if request.method == 'POST':
        delete_list = request.POST.get('hidden_field', False)
        if delete_list:
            values = [int(i) for i in delete_list.split("~")]
            m = Message.objects.filter(pk__in=values)
            message = m.filter(recipient=request.user)
            for m in message:
                m.is_deleted_by_recipient = "True"
                m.save()
    paginator = Paginator(posts, 7)

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)

    return render(request, 'messages.html', {'posts': posts, 'person': person})


@login_required
def Draft(request):
    person = Person.objects.get(username=request.user)
    posts = Message.objects.filter(recipient=request.user, draft=True).order_by("-created")
    if request.method == 'POST':
        delete_list = request.POST.get('hidden_field', False)
        if delete_list:
            values = [int(i) for i in delete_list.split("~")]
            m = Message.objects.filter(pk__in=values)
            m = m.filter(recipient=request.user, draft=True)
            m.delete()
            return HttpResponseRedirect(reverse('world:Draft'))

    paginator = Paginator(posts, 7)

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)

    return render(request, 'draft.html', {'posts': posts, 'person': person, })


@login_required
def sentmessage(request):
    person = Person.objects.get(username=request.user)
    posts = Message.objects.filter(user=request.user, sentmessage=True, is_deleted_by_sender=False).order_by("-created")
    sentmessage = "Hello"
    if request.method == 'POST':
        delete_list = request.POST.get('hidden_field', False)
        if delete_list:
            values = [int(i) for i in delete_list.split("~")]
            m = Message.objects.filter(pk__in=values)
            message = m.filter(user=request.user, sentmessage=True)
            for m in message:
                m.is_deleted_by_sender = "True"
                m.save()

    paginator = Paginator(posts, 7)

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)

    return render(request, 'sentmessage.html', {'posts': posts, 'person': person, 'sentmessage': sentmessage})


@login_required
def readsentmessage(request, id):
    try:
        messages = Message.objects.get(pk=id, user=request.user, sentmessage=True, draft=False)
    except Message.DoesNotExist:
        return HttpResponseRedirect(reverse('world:Display'))

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            id = request.POST.get('hidden_field', False)
            try:
                messages = Message.objects.get(pk=id, user=request.user, sentmessage=True, draft=False)

            except Message.DoesNotExist:
                return HttpResponseRedirect(reverse('world:LoginRequest'))

            body = form.cleaned_data['body']

            Message.objects.create(user=request.user, recipient=messages.recipient, body=body, thread=messages.thread,
                                   sentmessage=True, read=False)
            return HttpResponseRedirect(reverse('world:message'))

    message = Message.objects.filter(thread=messages.thread).filter(created__lte=messages.created)
    person = Person.objects.get(username=request.user)

    initial = {}
    initial.update({'hidden_field': messages.id})
    form = ReplyForm(initial=initial)

    return render(request, 'read.html', {'messages': messages, 'form': form, 'message': message, 'person': person})


@login_required
def read(request, id):
    try:
        messages = Message.objects.get(pk=id, recipient=request.user)
    except Message.DoesNotExist:
        return HttpResponseRedirect(reverse('world:Display'))
    messages.read = True
    messages.save()
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['hidden_field']

            try:
                messages = Message.objects.get(pk=id, recipient=request.user, sentmessage=True, draft=False)

            except Message.DoesNotExist or Thread.DOesNotExist:
                return HttpResponseRedirect(reverse('world:LoginRequest'))
            person = Person.objects.get(username=messages.user)
            if person.inbox == "D":
                return HttpResponseRedirect(reverse('world:message'))
            body = form.cleaned_data['body']

            Message.objects.create(user=request.user, recipient=messages.user, body=body, thread=messages.thread,
                                   sentmessage=True, read=False)
            return HttpResponseRedirect(reverse('world:message'))
        else:
            raise ValidationError

    message = Message.objects.filter(thread=messages.thread).filter(created__lte=messages.created)
    person = Person.objects.get(username=request.user)

    initial = {}
    initial.update({'hidden_field': messages.id})
    form = ReplyForm(initial=initial)

    return render(request, 'read.html', {'messages': messages, 'form': form, 'message': message, 'person': person})


@login_required
def Create(request):
    person = Person.objects.get(username=request.user)
    form = NewMessageForm(request)
    if request.POST.get('_send', False):
        form = NewMessageForm(request, request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            if recipient:
                thread = Thread.objects.create(subject=subject, user=request.user)
                Recipient = Person.objects.get(username=request.user)
                if Recipient.inbox == "D":
                    return HttpResponseRedirect(reverse('world:message'))
                message = Message.objects.create(user=request.user, recipient=recipient, body=message, thread=thread,
                                                 sentmessage=True, read=False)
                return HttpResponseRedirect(reverse('world:message'))
            else:
                thread = Thread.objects.create(subject=subject, user=request.user)
                Message.objects.create(user=request.user, recipient=request.user, body=message, thread=thread,
                                       draft=True)
                return HttpResponseRedirect(reverse('world:message'))

    elif request.POST.get('_save', False):
        form = NewMessageForm(request, request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            thread = Thread.objects.create(subject=subject, user=request.user)
            Message.objects.create(user=request.user, recipient=request.user, body=message, thread=thread, draft=True,
                                   sentmessage=False)
            return HttpResponseRedirect(reverse('world:message'))
    return render(request, 'create.html', {'form': form, 'person': person})


@login_required
def ReadDraft(request, id):
    try:
        messages = Message.objects.get(pk=id, recipient=request.user)
    except Message.DoesNotExist:
        return HttpResponseRedirect(reverse('world:Display'))
    thread = Thread.objects.get(message=messages)
    initial = {}
    initial.update({'hidden_field': messages.id})
    draft = DraftForm(request, instance=messages, initial=initial)
    thread = ThreadForm(instance=thread)
    person = Person.objects.get(username=request.user)

    if request.method == 'POST':
        id = request.POST.get('hidden_field', False)
        form = ThreadForm(request.POST)
        forms = DraftForm(request, request.POST)
        if form.is_valid() and forms.is_valid():

            m = Message.objects.get(pk=id, )
            recipient = forms.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            body = forms.cleaned_data['body']
            person = Person.objects.get(username=request.user)

            m.user = request.user
            m.recipient = recipient
            m.body = body
            m.draft = False
            m.sentmessage = True
            m.save()
            return HttpResponseRedirect(reverse('world:message'))
        else:
            ctx = {'DraftForm': forms, 'ThreadForm': form, 'person': person}
            return render(request, 'create.html', ctx)

    return render(request, 'create.html', {'DraftForm': draft, 'ThreadForm': thread, 'person': person})
