"""MySQLProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin


#Ancillary
from views.ancillary import status
from views.ancillary import clear
from views.ancillary import createdb

#User
from views.user import insertUser
from views.user import detailsUser
from views.user import followUser
from views.user import updateProfile
from views.user import unfollowUser
from views.user import listFollowersUser
from views.user import listFollowingUser
from views.user import listPostsUser

#Forum
from views.forum import insertForum
from views.forum import listUsersInForum
from views.forum import listThreadsInForum
from views.forum import detailsForum
from views.forum import listPostsInForum

#Thread
from views.thread import insertThread
from views.thread import closeThread
from views.thread import openThread 
from views.thread import detailsThread
from views.thread import voteThread
from views.thread import updateThread
from views.thread import subscribeThread,unsubscribeThread
from views.thread import listThread
from views.thread import removeThread,restoreThread
from views.thread import listPosts

#Post
from views.post import insertPost
from views.post import detailsPost
from views.post import removePost,restorePost
from views.post import updatePost
from views.post import votePost
from views.post import listPost



urlpatterns = [
    #User
    url('^db/api/user/create/$',insertUser),
    url('^db/api/user/details/$',detailsUser),
    url('^db/api/user/follow/$',followUser),
    url('^db/api/user/updateProfile/$',updateProfile),
    url('^db/api/user/unfollow/$',unfollowUser),
    url('^db/api/user/listFollowers/$',listFollowersUser),
    url('^db/api/user/listFollowing/$',listFollowingUser),
    url('^db/api/user/listPosts/$',listPostsUser),

    #Forum
    url('^db/api/forum/create/$',insertForum),
    url('^db/api/forum/details/$',detailsForum),
    url('^db/api/forum/listUsers/$',listUsersInForum),
    url('^db/api/forum/listThreads/$',listThreadsInForum),
    url('^db/api/forum/listPosts/$',listPostsInForum),

    #Thread
    url('^db/api/thread/create/$',insertThread),
    url('^db/api/thread/close/$',closeThread), 
    url('^db/api/thread/open/$',openThread),
    url('^db/api/thread/details/$',detailsThread),
    url('^db/api/thread/vote/$',voteThread),
    url('^db/api/thread/update/$',updateThread),
    url('^db/api/thread/subscribe/$',subscribeThread),
    url('^db/api/thread/unsubscribe/$',unsubscribeThread),
    url('^db/api/thread/list/$',listThread),
    url('^db/api/thread/remove/$',removeThread),
    url('^db/api/thread/restore/$',restoreThread),
    url('^db/api/thread/listPosts/$',listPosts),

    #Post
    url('^db/api/post/create/$',insertPost),
    url('^db/api/post/details/$',detailsPost),
    url('^db/api/post/remove/$',removePost),
    url('^db/api/post/restore/$',restorePost),
    url('^db/api/post/update/$',updatePost),
    url('^db/api/post/vote/$',votePost),
    url('^db/api/post/list/$',listPost),

    #Ancillary
    url('^db/api/status/$',status),
    url('^db/api/clear/$',clear),
    url('^createdb/$',createdb),
    
    url(r'^admin/', include(admin.site.urls)),

]
