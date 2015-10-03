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
from views.user import insertUser
from views.forum import insertForum
from views.thread import insertThread
from views.post import insertPost

urlpatterns = [
    url('^hello/$',hello),
    url('^createdb/$',createdb),
    url('^dropdb/$',dropdb),
    url('^insertUser/$',insertUser),
    url('^insertForum/$',insertForum),
    url('^insertThread/$',insertThread),
    url('^insertPost/$',insertPost),
    url(r'^admin/', include(admin.site.urls)),

]
