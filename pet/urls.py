from django.conf.urls import url

import pet.views

urlpatterns = [
    url(r'^display/$', pet.views.display, name='display'),
    url(r'^picture/$', pet.views.picture_creator, name='picture_creator'),
    url(r'^board/$', pet.views.board_creator, name='board_creator'),
    url(r'^register/$', pet.views.pet_registration, name='petRegistration'),
    url(r'^login/$', pet.views.login_request, name='login_request'),
    url(r'^logout/$', pet.views.logout_request, name='logout_request'),
    url(r'^profile/(?P<slug>[-\w\d]+)/$', pet.views.profile, name='profile'),
    url(r'^friend/add/(?P<to_username>[\w-]+)/$', pet.views.friendship_add_friend, name='friendship_add_friend'),
    url(r'^follower/add/(?P<followee_username>[\w-]+)/$', pet.views.follower_add, name='follower_add'),
    url(r'^archive/$', pet.views.archive, name='archive'),
    url(r'^board/(?P<slug>[-\w\d]+),(?P<id>\d+)/(?P<picture_id>\d+)$', pet.views.description, name='description'),
    url(r'^following/$', pet.views.follower, name='follower'),
    url(r'^boardfinder/$', pet.views.board_finder, name='board_finder'),
    url(r'^boardeditor/$', pet.views.board_editor, name='board_editor'),
    url(r'^changepicture/(?P<picture_id>\d+)/$', pet.views.change_picture, name='change_picture'),
    url(r'^following/(?P<slug>[-\w\d]+)/cancelfriend/$', pet.views.cancel_friend, name='cancel_friend'),
    url(r'^following/(?P<slug>[-\w\d]+)/addfriend/$', pet.views.add_friend, name='add_friend'),
    url(r'^my_friend/$', pet.views.my_friend, name='my_friend'),
    url(r'^Follow/$', pet.views.following, name='following'),
    url(r'^sparkprofile/$', pet.views.spark_profile, name='spark_profile'),
    url(r'^search_person/$', pet.views.search_person, name='search_person'),
    url(r'^followingall/$', pet.views.following_all, name='following_all'),
    url(r'^whatisparkalight/$', pet.views.whatspark, name='whatspark'),
    url(r'^contact/$', pet.views.contacts, name='contact'),
    url(r'^edit_friend_func/$', pet.views.edit_friend_func, name='edit_friend_func'),
    url(r'^friend_star/(?P<slug>[-\w\d]+)/$', pet.views.friend_star, name='friend_star'),
    url(r'^term-and-condition/$', pet.views.term, name='term'),
    url(r'^privacy-policy/$', pet.views.privacy, name='privacy'),
    url(r'^faq/$', pet.views.faq, name='faq'),
    url(r'^car/like$', pet.views.like, name='like'),
    url(r'^car/postComment$', pet.views.post_comment, name='post_comment'),
    url(r'^car/getComment$', pet.views.get_comment, name='get_comment'),
    url(r'^car/deleteComment$', pet.views.delete_comment, name='delete_comment'),
    url(r'^board/(?P<slug>[-\w\d]+),(?P<id>\d+)/$', pet.views.car, name='car'),
    url(r'^car/search$', pet.views.board_finder, name='search'),
    url(r'^car/searchBoards$', pet.views.search_boards, name='search_boards'),
    url(r'^friend/accept/(?P<friendship_request_id>\d+)/$', pet.views.friendship_accept, name='friendship_accept'),
    url(r'^friend/cancelss/(?P<username>[\w-]+)/$', pet.views.friendship_cancel, name='friendship_cancel'),
    url(r'^follower/remove/(?P<followee_username>[\w-]+)/$', pet.views.follower_remove, name='follower_remove'),
    url(r'^friend/remove/(?P<friendship_request_id>\d+)/$', pet.views.friendship_reject, name='friendship_reject'),
]