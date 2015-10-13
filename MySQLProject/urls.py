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

#Post
from views.post import insertPost
from views.post import detailsPost
from views.post import removePost,restorePost
from views.post import updatePost
from views.post import votePost
from views.post import listPost



urlpatterns = [
    #User
    url('^insertUser/$',insertUser),
    url('^db/api/user/details/$',detailsUser),
    url('^db/api/user/follow/$',followUser),
    url('^db/api/user/updateProfile/$',updateProfile),
    url('^db/api/user/unfollow/$',unfollowUser),
    url('^listFollowersUser/$',listFollowersUser),
    url('^db/api/user/listFollowing/$',listFollowingUser),
    url('^db/api/user/listPosts/$',listPostsUser),

    #Forum
    url('^insertForum/$',insertForum),
    url('^detailsForum/$',detailsForum),
    url('^db/api/forum/listUsers/$',listUsersInForum),
    url('^listThreadsInForum/$',listThreadsInForum),
    url('^listPostsInForum/$',listPostsInForum),

    #Thread
    url('^insertThread/$',insertThread),
    url('^db/api/thread/close/$',closeThread), 
    url('^db/api/thread/open/$',openThread),
    url('^detailsThread/$',detailsThread),
    url('^voteThread/$',voteThread),
    url('^updateThread/$',updateThread),
    url('^subscribeThread/$',subscribeThread),
    url('^unsubscribeThread/$',unsubscribeThread),
    url('^listThread/$',listThread),
    url('^removeThread/$',removeThread),
    url('^restoreThread/$',restoreThread),

    #Post
    url('^insertPost/$',insertPost),
    url('^detailsPost/$',detailsPost),
    url('^removePost/$',removePost),
    url('^restorePost/$',restorePost),
    url('^updatePost/$',updatePost),
    url('^votePost/$',votePost),
    url('^listPost/$',listPost),

    #Ancillary
    url('^db/api/status/$',status),
    url('^db/api/clear/$',clear),
    url('^createdb/$',createdb),
    
    url(r'^admin/', include(admin.site.urls)),

]
