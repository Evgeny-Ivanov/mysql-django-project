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

from views.ancillary import hello
from views.ancillary import createdb
from views.ancillary import dropdb

from views.ancillary import status
from views.ancillary import clear

from views.user import insertUser
from views.user import detailsUser
from views.user import followUser
from views.user import updateProfile
from views.user import unfollowUser
from views.user import listFollowersUser
from views.user import listFollowingUser
from views.user import listPostsUser

from views.forum import insertForum
from views.forum import listUsersInForum
from views.forum import listThreadsInForum

from views.thread import insertThread
from views.thread import closeThread
from views.thread import openThread 


from views.post import insertPost

urlpatterns = [
    url('^hello/$',hello),
    url('^createdb/$',createdb),
    url('^dropdb/$',dropdb),
    url('^insertUser/$',insertUser),
    url('^insertForum/$',insertForum),
    url('^insertThread/$',insertThread),
    url('^insertPost/$',insertPost),
    url('^db/api/user/details/$',detailsUser),
    url('^db/api/user/follow/$',followUser),
    url('^db/api/thread/close/$',closeThread), 
    url('^db/api/user/updateProfile/$',updateProfile),
    url('^db/api/user/unfollow/$',unfollowUser),
    url('^listFollowersUser/$',listFollowersUser),
    url('^listThreadsInForum/$',listThreadsInForum),
    url('^db/api/user/listFollowing/$',listFollowingUser),
    url('^db/api/user/listPosts/$',listPostsUser),
    url('^db/api/thread/open/$',openThread),
    url('^db/api/status/$',status),
    url('^db/api/clear/$',clear),
    url('^db/api/forum/listUsers/$',listUsersInForum),
    url(r'^admin/', include(admin.site.urls)),

]
