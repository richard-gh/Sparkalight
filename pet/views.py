import json
import math
from datetime import datetime, timedelta
from itertools import chain

from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from el_pagination.decorators import page_template
from friendship.models import Friend, Follow, FriendshipRequest
from sorl.thumbnail import get_thumbnail, delete
from mysite import settings
from pet.forms import SearchBoardForm, SearchForm, UserRegistration, PersonForm, BoardChangeNameForm, BoardForm, \
    LoginForm, ProfileForm, BoardDeleteForm, PictureForm, BoardPrivateForm, BoardDescriptionForm, SpecialBoardForm, \
    BoardNameForm, ContactForm, DescriptionForm, BoardCommentForm, BoardTransferForm
from pet.models import Person, Board, BoardComment, LikeBoard, Picture, Contact
from django.shortcuts import redirect


def index(request):
    ### Placeholder index page just redirects to login.
    return redirect('/login/')


@login_required
def search_person(request):
    person = Person.objects.get(username=request.user)

    if request.GET.get('text'):
        request.session['text'] = request.GET.get('text')
        text = request.GET.get('text')
        lists = Person.objects.filter(name__iexact=text, is_active=True)
        lists1 = Person.objects.filter(username__iexact=text, is_active=True)
        posts = list(chain(lists, lists1))
        form = SearchForm(initial={'text': request.session.get('text')})
        paginator = Paginator(posts, 24)
        try:
            page = int(request.GET.get("page", '1'))
        except ValueError:
            page = 1

        try:
            posts = paginator.page(page)
        except (InvalidPage, EmptyPage):
            posts = paginator.page(paginator.num_pages)
        return render(request, 'searchs.html',
                      {'form': form, "posts": posts, 'formula': request.session.get('text'), 'person': person})
    return render(request, "searchs.html", {"form": SearchForm(), 'person': person})


# SHOW PEOPLE WHO FOLLOW YOU
@page_template('pagination.html')
@login_required
def show_followers(request, template='follower.html', extra_context=None):
    Follower = "follower"
    context = {
        'posts': request.user.followers.all(),
        'page_template': 'pagination.html',
    }
    extra_context = {"follower": Follower, }
    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


# SHOW PEOPLE WHO YOU ARE FOLLOWING
@page_template('pagination.html')
@login_required
def show_following(request, template='following.html', extra_context=None):
    Following = "following"
    context = {
        'posts': request.user.following.all(),
        'page_template': 'pagination.html',

    }
    extra_context = {"following": Following, }
    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


@page_template('uninvitedpagination.html', key='other_entries_page')
@page_template('pagination.html')
@login_required
def my_friend(request, template='friend.html', extra_context=None):
    context = {
        'posts': Friend.objects.friends(request.user),
        'F': 'pagination.html',
        'U': 'uninvitedpagination.html',
        'uninvited': Friend.objects.unread_requests(user=request.user),
    }

    extra_context = {"Friend": Friend, }
    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


@login_required
@page_template('archivepagination.html', key='other_entries_page')
@page_template('commentpagination.html', key='other')
def archive(request, template='archive.html', extra_context=None):
    user = Person.objects.get(username=request.user)
    person = Person.objects.get(username=request.user)
    last_month = datetime.today() - timedelta(days=30)
    following = user.following.all()
    lists = [f.followee for f in following]
    board = Board.objects.filter(user=request.user)
    month = datetime.now() - timedelta(days=10)
    a = Board.objects.filter(user__in=lists, created__gte=month).order_by("-created")

    context = {
        'comment': BoardComment.objects.filter(~Q(user=user), board=board, created__gte=month),
        'C': 'commentpagination.html',
        'person': Person.objects.get(username=user),
        'posts': Picture.objects.filter(is_primary=True, board=a),
        'P': 'archivepagination.html',

    }

    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


@login_required
def friendship_accept(request, friendship_request_id):
    """ Accept a friendship request """
    f_request = get_object_or_404(FriendshipRequest, id=friendship_request_id)
    if f_request.to_user == request.user and f_request.to_user.is_active == True:
        f_request.accept()
        return HttpResponseRedirect(reverse('world:my_friend'))

    HttpResponseRedirect(reverse('world:my_friend'))


@login_required
def friendship_reject(request, friendship_request_id):
    """ Cancel a previously created friendship_request_id """
    f_request = get_object_or_404(FriendshipRequest, id=friendship_request_id)
    if f_request.to_user == request.user:
        f_request.cancel()
        return HttpResponseRedirect(reverse('world:my_friend'))

    return HttpResponseRedirect(reverse('world:my_friend'))


@login_required
def friendship_cancel(request, username):
    try:
        person = Person.objects.get(username=username)
    except Person.DoesNotExist:
        return HttpResponseRedirect(reverse('world:edit_friend_func'))

    if Friend.objects.are_friends(request.user, person) == True:
        Friend.objects.remove_friend(person, request.user)

        return HttpResponseRedirect(reverse('world:my_friend'))
    else:
        return HttpResponseRedirect(reverse('world:my_friend'))


@login_required
def follower_remove(request, followee_username):
    """ Remove a following relationship """
    followee = Person.objects.get(username=followee_username)
    follower = request.user
    Follow.objects.remove_follower(follower, followee)

    return HttpResponseRedirect(reverse('world:following_all'))


@login_required
def friendship_add_friend(request, to_username, ):
    # """ create a FriendshipRequest """
    to_user = Person.objects.get(username=to_username)
    from_user = request.user
    if to_user.is_active == False:
        url = reverse('world:profile', kwargs={'slug': to_user.slug})
        return HttpResponseRedirect(url)
    Friend.objects.add_friend(from_user, to_user)
    url = reverse('world:profile', kwargs={'slug': to_user.slug})
    return HttpResponseRedirect(url)


@login_required
def follower_add(request, followee_username, ):
    # """ create a following relationship """
    followee = Person.objects.get(username=followee_username)
    follower = request.user
    if not followee.is_active:
        url = reverse('world:profile', kwargs={'slug': followee.slug})
        return HttpResponseRedirect(url)
    Follow.objects.add_follower(follower, followee)
    url = reverse('world:profile', kwargs={'slug': followee.slug})
    return HttpResponseRedirect(url)


def pet_registration(request):
    if request.user.is_authenticated():
        person = Person.objects.get(username=request.user)
        url = reverse('world:profile', kwargs={'slug': person.slug})
        return HttpResponseRedirect(url)
    form = UserRegistration()
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            user = Person.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                date_of_birth=form.cleaned_data['date_of_birth']
            )
            password = form.cleaned_data['password']
            user.is_active = True
            user.set_password(password)
            user.save()

            person = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            login(request, person)
            return render(request, 'choose.html')

    return render(request, 'register.html', {'form': form}, )


def login_request(request):
    form = LoginForm(request.POST or None)
    if request.user.is_authenticated() and request.user.is_active == True:
        person = Person.objects.get(username=request.user)
        url = reverse('world:profile', kwargs={'slug': person.slug})
        return HttpResponseRedirect(url)
    if request.POST and form.is_valid():
        user = form.authenticate_user()
        login(request, user)
        person = Person.objects.get(username=request.user)
        url = reverse('world:profile', kwargs={'slug': person.slug})
        return HttpResponseRedirect(url)

    return render(request, 'login.html', {'form': form})


@login_required
def spark_profile(request):
    form = PersonForm()
    if request.POST.has_key('pro'):
        form = PersonForm(request.POST, request.FILES)
        if request.POST['pro'] == 'first':
            if form.is_valid():
                person = Person.objects.get(username=request.user)
                image = form.cleaned_data['image']
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                if image:
                    person.image = form.cleaned_data['image']
                if description:
                    person.description = form.cleaned_data['description']
                if name:
                    person.name = form.cleaned_data['name']
                person.save()

                url = reverse('world:profile', kwargs={'slug': person.slug})

                return HttpResponseRedirect(url)

    return render(request, 'sparkprofile.html', {'form': form})


@login_required
def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse('world:login_request'))


@page_template('profilepagination.html')
def profile(request, slug, template='profile.html', extra_context=None):
    person = Person.objects.get(slug=slug)
    if person:
        if person.profile == False:

            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('world:login_request'))
        if person.is_active == False:
            raise Http404
        context = {
            'board': Board.objects.filter(user=person),
            'page_template': 'profilepagination.html',
        }

        Friends = []
        Follows = []
        already = []
        if request.user.is_authenticated():
            Friends = Friend.objects.are_friends(request.user, person)
            Follows = Follow.objects.follows(request.user, person)
            try:
                FriendshipRequest.objects.get(from_user=request.user, to_user=person)
                already = FriendshipRequest.objects.get(from_user=request.user, to_user=person)
            except FriendshipRequest.DoesNotExist:
                pass

        extra_context = {'person': person, 'Friend': Friends, 'Follows': Follows, 'already': already}

        if extra_context is not None:
            context.update(extra_context)
        return render(request, template, context)

    return render(request, 'profile.html', )


def display(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('world:login_request'))
    prof = Person.objects.get(username=request.user)
    form = ProfileForm(instance=prof)
    deleteboard = BoardDeleteForm(request.user)
    if request.POST.has_key('process'):
        form = ProfileForm(request.POST, request.FILES)
        forms = BoardDeleteForm(request.user, request.POST)

        if request.POST['process'] == 'fifth':
            if forms.is_valid():
                board = forms.cleaned_data['board']
                if board:
                    board = board.id
                    try:
                        b = Board.objects.get(pk=board, user=request.user)
                        picture = Picture.objects.filter(board=board)
                        for p in picture:
                            delete(p.image)
                            p.delete()
                        b.delete()
                        return HttpResponseRedirect(reverse('world:display'))
                    except Board.DoesNotExist:
                        return HttpResponseRedirect(reverse('world:display'))
        elif request.POST['process'] == 'fourth':
            if form.is_valid():
                person = Person.objects.get(username=request.user)
                image = form.cleaned_data['image']
                name = form.cleaned_data['name']
                profile = form.cleaned_data['profile']
                description = form.cleaned_data['description']
                checkbox = form.cleaned_data['checkbox']
                if profile == False:
                    person.profile = form.cleaned_data['profile']
                if profile == True:
                    person.profile = form.cleaned_data['profile']

                if description:
                    person.description = form.cleaned_data['description']
                if checkbox:
                    delete(person.image)

                    person.image.delete()
                if image:
                    person.image = form.cleaned_data['image']
                if name:
                    person.name = form.cleaned_data['name']

                person.save()
                return HttpResponseRedirect(reverse('world:display'))
    return render(request, 'edit.html', {'form': form, 'deleteboard': deleteboard, 'prof': prof})


@login_required
def board_creator(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('world:login_request'))
    form = BoardForm()
    person = Person.objects.get(username=request.user)
    if request.method == "POST":
        form = BoardForm(request.POST, request.FILES or None)
        if form.is_valid():
            name = form.cleaned_data['name']
            text = form.cleaned_data['text']
            shirt_size = form.cleaned_data['shirt_size']
            image = form.cleaned_data['image']
            description = form.cleaned_data['description']
            board = Board.objects.create(user=request.user, name=name, description=text, shirt_size=shirt_size)

            user = Person.objects.get(username=request.user)
            if image:
                picture = Picture(user=user)
                picture.board = board
                picture.description = form.cleaned_data['description']
                picture.image = image
                picture.is_primary = True
                picture.save()
                board.picture = picture
                board.save()
                return HttpResponseRedirect(reverse('world:car', kwargs={'slug': board.slug, 'id': board.id}))
            else:
                return HttpResponseRedirect(reverse('world:car', kwargs={'slug': board.slug, 'id': board.id}))
    return render(request, 'board.html', {'form': form, 'person': person})


def picture_creator(request):
    form = PictureForm(request.user)
    person = Person.objects.get(username=request.user)
    if request.method == "POST":

        form = PictureForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            picture = Picture(user=request.user)
            image = request.FILES.get('image')

            if image:
                picture.image = image
            description = form.cleaned_data['description']
            if description:
                picture.description = form.cleaned_data['description']

            board = form.cleaned_data['board']
            if board:
                picture.board = form.cleaned_data['board']
            picture.save()
            return HttpResponseRedirect(reverse('world:picture_creator'))


    else:

        if request.GET.get('board'):
            board = request.GET.get('board')
            b = Board.objects.get(pk=board)
            return HttpResponseRedirect(reverse('world:car', kwargs={'slug': b.slug, 'id': b.id}))

    return render(request, 'picture.html', {'form': form, 'forms': BoardTransferForm(request.user), 'person': person})


@login_required
def board_editor(request):
    person = Person.objects.get(username=request.user)
    board = BoardNameForm(request.user)
    BoardChangeName = BoardChangeNameForm(request.user)
    BoardPrivate = BoardPrivateForm(request.user)
    if request.POST.has_key('process'):
        form = BoardNameForm(request.user, request.POST, )
        formsss = BoardChangeNameForm(request.user, request.POST, )
        formssss = BoardPrivateForm(request.user, request.POST, )
        formsssss = BoardDescriptionForm(request.POST, )
        formssssss = SpecialBoardForm(request.POST, )

        if request.POST['process'] == 'third':
            if form.is_valid():
                board = form.cleaned_data['board']
                boardname = form.cleaned_data['boardname']
                try:
                    bo = Board.objects.get(pk=board.id, user=request.user)
                    bo.name = boardname
                    bo.save()
                    return HttpResponseRedirect(reverse('world:board_editor'))
                except Board.DoesNotExist:
                    return HttpResponseRedirect(reverse('world:board_editor'))
            return HttpResponseRedirect(reverse('world:board_editor'))
        elif request.POST['process'] == 'change':
            if formsss.is_valid():
                board = formsss.cleaned_data['board']
                try:
                    b = Board.objects.get(pk=board.id, user=request.user)
                    form = BoardDescriptionForm(instance=b)

                    return render(request, 'boardeditor.html',
                                  {'b': b, 'form': form, 'board': BoardNameForm(request.user),
                                   'BoardChangeNameForm': BoardChangeNameForm(request.user),
                                   'BoardPrivateForm': BoardPrivateForm(request.user), 'person': person})
                except Board.DoesNotExist:
                    return HttpResponseRedirect(reverse('world:board_editor'))

        elif request.POST['process'] == 'special':
            if formssss.is_valid():
                board = formssss.cleaned_data['board']
                try:
                    c = Board.objects.get(pk=board.id, user=request.user)
                    forms = SpecialBoardForm(instance=c)
                    return render(request, 'boardeditor.html',
                                  {'c': c, 'forms': forms, 'board': BoardNameForm(request.user),
                                   'BoardChangeNameForm': BoardChangeNameForm(request.user),
                                   'BoardPrivateForm': BoardPrivateForm(request.user), 'person': person})

                except Board.DoesNotExist:
                    return HttpResponseRedirect(reverse('world:board_editor'))

        elif request.POST['process'] == 'changename':
            if formsssss.is_valid():
                description = formsssss.cleaned_data['description']
                try:
                    board = request.POST.get('id', False)
                    board = Board.objects.get(pk=board, user=request.user)
                    board.description = description
                    board.save()
                    return HttpResponseRedirect(reverse('world:board_editor'))

                except Board.DoesNotExist:
                    return HttpResponseRedirect(reverse('world:board_editor'))

            return render(request, 'boardeditor.html', {'form': formsssss, 'person': person})

        elif request.POST['process'] == 'specials':
            if formssssss.is_valid():
                board = request.POST.get('d', False)
                try:
                    board = Board.objects.get(pk=board, user=request.user)
                    profile = formssssss.cleaned_data['profile']
                    friends = formssssss.cleaned_data['friends']
                    comments = formssssss.cleaned_data['comments']
                    board.profile = profile
                    board.friends = friends
                    board.comments = comments
                    board.save()
                    return HttpResponseRedirect(reverse('world:board_editor'))
                except Board.DoesNotExist:
                    return HttpResponseRedirect(reverse('world:board_editor'))
            return HttpResponseRedirect(reverse('world:board_editor'))

    return render(request, 'boardeditor.html',
                  {'board': board, 'BoardChangeNameForm': BoardChangeName, 'BoardPrivateForm': BoardPrivate,
                   'person': person})


@login_required
def change_picture(request, picture_id):
    picture = picture_id
    try:
        picture = Picture.objects.get(pk=picture, user=request.user)
        board = Board.objects.get(board=picture)
        board.picture = picture
        board.save()
        return HttpResponseRedirect(reverse('world:board_editor'))
    except Picture.DoesNotExist:
        return HttpResponseRedirect(reverse('world:board_editor'))


@login_required
def cancel_friend(request, slug):
    username = Person.objects.get(slug=slug)
    user = User.objects.get(username=username)
    user1 = User.objects.get(username=request.user)
    try:
        friend = Friend.objects.filter(user=user, friend=user1)
        friend.delete()
        return HttpResponseRedirect(reverse('world:my_friend'))
    except Friend.DoesNotExist:
        return HttpResponseRedirect(reverse('world:my_friend'))


@login_required
def add_friend(request, slug):
    username = Person.objects.get(slug=slug)
    user1 = User.objects.get(username=username)
    user2 = User.objects.get(username=request.user)
    try:
        friend = Friend.objects.get(user=user1, friend=user2)
        if friend:
            friend1 = Friend.objects.create(user=user2, friend=user1, is_accepted=True)
            friend = Friend.objects.get(user=user1, friend=user2)
            friend.is_accepted = True
            friend.save()
            return HttpResponseRedirect(reverse('world:my_friend'))
    except Friend.DoesNotExist:
        return HttpResponseRedirect(reverse('world:logout_request'))


@page_template('page.html')
@login_required
def following_all(request, template='editfollowingall.html', extra_context=None):
    edit_following = 'EditFollowing'
    context = {
        'posts': request.user.following.all(),
        'page_template': 'page.html',

    }
    extra_context = {'EditFollowing': edit_following}
    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


@page_template('page.html')
@login_required
def edit_friend_func(request, template='editfriend.html', extra_context=None):
    edit_friend = 'edit_friend'
    context = {
        'posts': Friend.objects.friends(request.user),
        'page_template': 'page.html',

    }
    extra_context = {'edit_friend': edit_friend, }
    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


def whatspark(request):
    return render(request, 'whatspark.html')


def term(request):
    return render(request, 'term.html')


def privacy(request):
    return render(request, 'privacy.html')


def faq(request):
    return render(request, 'faq.html')


@login_required
def contacts(request):
    person = Person.objects.get(username=request.user)
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            user = Person.objects.get(username=request.user)
            text = form.cleaned_data['text']
            email = form.cleaned_data['email']
            category = form.cleaned_data['Category']
            Contact.objects.create(user=user, text=text, email=email, Category=category)
            return HttpResponseRedirect(reverse('world:contact'))
    return render(request, 'contactform.html', {'form': form, 'person': person})


@login_required
def description(request, slug, id, picture_id):
    person = Person.objects.get(username=request.user)
    user = Person.objects.get(username=request.user)
    try:
        p = Picture.objects.get(pk=picture_id)
    except Picture.DoesNotExist:
        return HttpResponseRedirect(reverse('world:profile', kwargs={'slug': person.slug}))

    if request.method == "POST":
        form = DescriptionForm(request.POST)
        if form.is_valid():
            if p.user == user:
                boolean = form.cleaned_data['boolean']
                description = form.cleaned_data['description']
                primary = form.cleaned_data['primary']
                if boolean == True:
                    delete(p.image)
                    p.delete()
                    return HttpResponseRedirect(reverse('world:car', kwargs={'slug': p.board.slug, 'id': p.board.id}))
                if primary == True:
                    picture = Picture.objects.filter(is_primary=True, board=p.board)
                    for x in picture:
                        x.is_primary = False
                        x.save()
                    p.is_primary = True

                p.description = description
                p.save()
                return HttpResponseRedirect(reverse('world:car', kwargs={'slug': p.board.slug, 'id': p.board.id}))
        return HttpResponseRedirect(reverse('world:car', kwargs={'slug': p.board.slug, 'id': p.board.id}))
    if p.user == user:
        form = DescriptionForm(instance=p)

        return render(request, 'description.html', {'form': form, 'p': p, 'person': person})

    return HttpResponseRedirect(reverse('world:profile', kwargs={'slug': person.slug}))


@login_required
def friend_star(request, slug):
    try:
        person = Person.objects.get(slug=slug)
    except Person.DoesNotExist:
        return HttpResponseRedirect(reverse('world:edit_friend_func'))
    user = User.objects.get(username=request.user)
    if Friend.objects.get(user=user, friend=person.user) and Friend.objects.get(user=person.user, friend=user):
        fried1 = Friend.objects.get(user=user, friend=person.user)
        fried2 = Friend.objects.get(user=person.user, friend=user)
        fried1.delete()
        fried2.delete()
        return HttpResponseRedirect(reverse('world:edit_friend_func'))
    else:
        return HttpResponseRedirect(reverse('world:edit_friend_func'))


@page_template('image_listing.html')
def car(request, id, slug, template='cars.html', extra_context=None):
    board = Board.objects.get(pk=id)
    person = []
    if request.user.is_authenticated():
        person = Person.objects.get(username=request.user)
    show_box = True

    if board.friends:
        if Friend.objects.are_friends(request.user, board.user) or board.user == request.user:
            show_box = True
        else:
            show_box = False
    context = {
        'images': Picture.objects.filter(board=board),
        'page_template': 'image_listing.html',
        'show_box': show_box
    }

    comment = BoardComment.objects.filter(board=board).order_by("-created")
    if request.user.is_authenticated():
        has_liked = LikeBoard.objects.filter(board=board, user=request.user)
    else:
        has_liked = None
    extra_context = {'board': board, 'comment': comment, 'has_liked': has_liked, 'person': person}
    if board.comments == True:
        initial = {}
        initial.update({'hidden_field': board.id})
        form = BoardCommentForm(initial=initial)
        extra_context.update({'form': form})

    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)


def post_comment(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            try:
                car_id = request.POST.get('car_id', 0)
                body = request.POST.get('body', "")
                body = body.strip()
                if not body:
                    return HttpResponse(json.dumps({'success': 'false', "msg": "Comment can not be blank."}),
                                        content_type="application/json")
                car_obj = Board.objects.get(pk=car_id)
                if not car_obj.comments:
                    return HttpResponse(json.dumps({'success': 'false', "msg": "Comments are disabled"}),
                                        content_type="application/json")
                if car_obj.friends:
                    if not Friend.objects.are_friends(request.user, car_obj.user):
                        return HttpResponse(json.dumps({'success': 'false', "msg": "Only friends can comment"}),
                                            content_type="application/json")
                review_obj = BoardComment.objects.create(user=request.user, body=body, board=car_obj)

                return HttpResponse(json.dumps({'success': 'true', "msg": "Success", "user": request.user.username}),
                                    content_type="application/json")
            except Exception, e:
                return HttpResponse(json.dumps(
                    {'success': 'false', "msg": "Some internal error occured request could not be completed."}),
                    content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({'success': 'false', "msg": "Your session has expired. Please login to post a comment."}),
            content_type="application/json")


def like(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            try:
                car_id = request.POST.get('car_id', 0)
                carid = int(car_id)
                car_obj = Board.objects.get(pk=carid)
                LikeBoard.objects.get_or_create(user=request.user, board=car_obj)
            except Exception, e:
                return HttpResponse(json.dumps({'success': 'false'}), content_type="application/json")
            like_count = car_obj.likeboard_set.count()
            return HttpResponse(json.dumps({'success': 'true', 'count': like_count}), content_type="application/json")
        return HttpResponse(json.dumps({'success': 'false'}), content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({'success': 'false', "msg": "Your session has expired. Please login to post a comment."}),
            content_type="application/json")


def get_comment(request):
    if request.is_ajax():
        context = dict()
        review_list = list()
        user_list = list()
        try:
            car_id = request.GET.get('car_id', 0)
            carid = int(car_id)
            page_num = request.GET.get('comment_page', 0)
            page_num = int(page_num)
            review_count = BoardComment.objects.filter(board_id=carid).count()

            per_page = settings.REVIEW_PAGINATION_PER_PAGE
            previous_label = settings.REVIEW_PAGINATION_PREVIOUS_LABEL
            next_label = settings.REVIEW_PAGINATION_NEXT_LABEL

            totalPages = int(math.ceil(review_count / float(per_page)))

            if page_num in (0, 1):
                reviews = BoardComment.objects.filter(board_id=carid).order_by("-created")[:per_page]
            else:
                start_index = (page_num - 1) * per_page
                end_index = page_num * per_page
                reviews = BoardComment.objects.filter(board_id=carid).order_by("-created")[start_index:end_index]
            if reviews:
                for comment in reviews:
                    if comment.user == request.user or comment.board.user == request.user:
                        flag = "true"
                    else:
                        flag = "false"
                    review_list.append(flag + "~" + str(comment.id) + "~" + str(comment.body))
                    user_list.append(comment.user.username)
            context.update({'page_num': page_num,
                            'review_count': review_count,
                            'per_page': per_page,
                            'previous_label': previous_label,
                            'next_label': next_label,
                            'success': 'true',
                            'reviews': review_list,
                            'total_pages': totalPages,
                            'users': user_list
                            })
        except Exception, e:
            return HttpResponse(
                json.dumps({'success': 'false', "msg": "Some internal error occured, request could not be completed."}),
                content_type="application/json")
        return HttpResponse(json.dumps(context), content_type="application/json")


def delete_comment(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            try:
                delete_id = request.POST.get('comment_id')
                comment = BoardComment.objects.get(pk=delete_id)
                if comment.user == request.user or comment.board.user == request.user:
                    comment.delete()
            except Exception, err:
                return HttpResponse(json.dumps(
                    {'success': 'false', "msg": "Some internal error occured, request could not be completed."}),
                    content_type="application/json")
            return HttpResponse(json.dumps({'success': 'true'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'success': 'false', "msg": "Your session has expired. Please login again."}),
                            content_type="application/json")


@login_required
def board_finder(request):
    form = SearchBoardForm()
    person = Person.objects.get(username=request.user)
    return render(request, "search.html", {'form': form, 'person': person})


def search_boards(request):
    if request.user.is_authenticated():
        if request.is_ajax():
            context = dict()
            board_list = list()
            image_list = list()
            board_user = list()
            board_id = list()
            board_slug = list()

            try:
                ## Retreive data from request ##
                search_key = request.GET.get('search_key')
                most_recent = request.GET.get('recent_flag')
                most_liked = request.GET.get('liked_flag')
                shirt_size = request.GET.get('shirt_size')

                ## Set pagination variables ##
                page_num = request.GET.get('page', 0)
                page_num = int(page_num)
                per_page = settings.SEARCH_PAGINATION_PER_PAGE
                previous_label = settings.SEARCH_PAGINATION_PREVIOUS_LABEL
                next_label = settings.SEARCH_PAGINATION_NEXT_LABEL

                if page_num not in (0, 1):
                    start_index = (page_num - 1) * per_page
                    end_index = page_num * per_page

                board_ids = Picture.objects.filter(is_primary=True).values_list('board_id', flat=True)

                ## Start: Block for keyword search ##
                if search_key:
                    if shirt_size == "all":

                        board_count = Board.objects.filter(name__icontains=search_key, id__in=board_ids).count()
                    else:
                        board_count = Board.objects.filter(name__icontains=search_key, shirt_size=shirt_size,
                                                           id__in=board_ids).count()

                    if page_num in (0, 1):
                        if shirt_size == "all":
                            boards = Board.objects.filter(name__icontains=search_key, id__in=board_ids)[:per_page]
                        else:
                            boards = Board.objects.filter(name__icontains=search_key, shirt_size=shirt_size,
                                                          id__in=board_ids)[:per_page]
                    else:
                        if shirt_size == "all":
                            boards = Board.objects.filter(name__icontains=search_key, id__in=board_ids)[
                                     start_index:end_index]
                        else:
                            boards = Board.objects.filter(name__icontains=search_key, shirt_size=shirt_size,
                                                          id__in=board_ids)[start_index:end_index]
                ## End: Block for keyword search ##

                ## Start: Block for Most Recent or Most Liked board search ##
                elif most_recent or most_liked:
                    board_count = Board.objects.filter(id__in=board_ids).count()
                    if page_num in (0, 1):
                        if shirt_size == "all":
                            if most_recent:
                                boards = Board.objects.filter(id__in=board_ids).order_by("-created")[:per_page]
                            elif most_liked:
                                b = Board.objects.filter(id__in=board_ids)
                                boards = b.annotate(num_likes=Count('likeboard')).order_by('-num_likes')[:per_page]
                        else:
                            board_count = Board.objects.filter(shirt_size=shirt_size, id__in=board_ids).count()
                            if most_recent:
                                boards = Board.objects.filter(shirt_size=shirt_size, id__in=board_ids).order_by(
                                    "-created")[:per_page]
                            else:
                                b = Board.objects.filter(shirt_size=shirt_size, id__in=board_ids)
                                boards = b.annotate(num_likes=Count('likeboard')).order_by('-num_likes')[:per_page]
                    else:
                        if shirt_size == "all":
                            if most_recent:
                                boards = Board.objects.filter(id__in=board_ids).order_by("-created")[
                                         start_index:end_index]
                            elif most_liked:
                                b = Board.objects.filter(id__in=board_ids)
                                boards = b.annotate(num_likes=Count('likeboard')).order_by('-num_likes')[
                                         start_index:end_index]
                        else:
                            board_count = Board.objects.filter(shirt_size=shirt_size, id__in=board_ids).count()
                            if most_recent:
                                boards = Board.objects.filter(shirt_size=shirt_size, id__in=board_ids).order_by(
                                    "-created")[start_index:end_index]
                            else:
                                b = Board.objects.filter(shirt_size=shirt_size, id__in=board_ids)
                                boards = b.annotate(num_likes=Count('likeboard')).order_by('-num_likes')[
                                         start_index:end_index]
                ## End: Block for Most Recent or Most Liked board search ##

                ## Start: Block for default search results ##
                else:
                    board_count = Board.objects.filter(id__in=board_ids).count()
                    if page_num in (0, 1):
                        boards = Board.objects.filter(id__in=board_ids)[:per_page]

                    else:
                        boards = Board.objects.filter(id__in=board_ids)[start_index:end_index]
                ## End: Block for default search results ##

                totalPages = int(math.ceil(board_count / float(per_page)))
                if boards:
                    for board in boards:
                        board_list.append(board.name)
                        board_user.append(board.user.username)
                        board_slug.append(board.slug)
                        board_id.append(board.id)
                        try:
                            pic_obj = Picture.objects.filter(board=board, is_primary=True)[0]
                            im = get_thumbnail(pic_obj.image.path, "175x175", crop="175px 175px", quality=99)
                            image_list.append(im.url)
                        except Exception, e:

                            image_list.append("")
                context.update({'page_num': page_num,
                                'board_count': board_count,
                                'per_page': per_page,
                                'previous_label': previous_label,
                                'next_label': next_label,
                                'success': 'true',
                                'boards': board_list,
                                'image_list': image_list,
                                'user': board_user,
                                'id': board_id,
                                'slug': board_slug,
                                'total_pages': totalPages
                                })
            except Exception, e:
                return HttpResponse(json.dumps(
                    {'success': 'false', "msg": "Some internal error occured, request could not be completed."}),
                    content_type="application/json")
            return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({'success': 'false', "msg": "Your session has expired. Please login to post a comment."}),
            content_type="application/json")
