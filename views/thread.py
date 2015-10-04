# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json


def insertThread(request):#?forum=name&title=Thread With Sufficiently Large Title&isClosed=true&user=example3@mail.ru&date=2014-01-01 00:00:01&message=hey hey hey hey!&slug=Threadwithsufficientlylargetitle&isDeleted=true
    cursor = connection.cursor()

    forum = request.GET["forum"]
    title = request.GET["title"]
    email = request.GET["user"]
    dateThread = request.GET["date"]
    message = request.GET["message"]
    slug = request.GET["slug"]

    isClosed = request.GET["isClosed"]
    if(isClosed=="true"):
        isClosed = True
    else: 
        isClosed = False

    isDeleted = request.GET["isDeleted"]
    if(isDeleted=="true"):
        isDeleted = True
    else: 
        isDeleted = False

    cursor.execute('''SELECT idUser
                      FROM User 
                      WHERE email = '%s';
                   ''' % (email,))
    idUser = cursor.fetchone()[0]

    cursor.execute('''SELECT idForum
                      FROM Forum
                      WHERE name = '%s';
                   ''' % (forum,))
    idForum = cursor.fetchone()[0]

    cursor.execute('''INSERT INTO Thread(idForum,idUser,title,slug,message,dateThread,isClosed,isDeleted) 
                      VALUES ('%d','%d','%s','%s','%s','%s','%d','%d');
                   ''' % (idForum,idUser,title,slug,message,dateThread,isClosed,isDeleted,)) 

    cursor.execute('''SELECT idThread
                      FROM Thread
                      WHERE title = '%s';
                   ''' % (title,))#title - не уникален,нужно поменять
    idThread = cursor.fetchone()[0]

    requestCopy = request.GET.copy()
    requestCopy.__setitem__('id',idThread)#setdefault()
    code = 0
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


def closeThread(request):
    cursor = connection.cursor()

    idThread = request.GET["thread"]
    idThread = int(idThread)
    cursor.execute('''UPDATE Thread
                      SET isClosed = false#возможно надо true
                      WHERE idThread = %d
                   ''' % (idThread,))

    code = 0
    responce = { "code": code, "response": {"thread":idThread,}}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

def openThread(request):
    cursor = connection.cursor()

    idThread = request.GET["thread"]
    idThread = int(idThread)
    
    cursor.execute('''UPDATE Thread
                      SET isClosed = true#возможно надо false
                      WHERE idThread = %d
                   ''' % (idThread,))

    code = 0
    responce = { "code": code, "response": {"thread":idThread,}}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")