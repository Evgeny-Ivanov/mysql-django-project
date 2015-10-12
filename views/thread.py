# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json
from views.ancillary import getBollean,dictfetchall

def getThreadById(cursor,idThread):
    cursor.execute('''SELECT CAST(dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,
                             message,slug,title,user,forum,points,likes,dislikes,posts
                      FROM Thread
                      WHERE idThread = %d
                   '''%idThread )
    return dictfetchall(cursor)

def insertThread(request):#?forum=name&title=Thread With Sufficiently Large Title&isClosed=true&user=example3@mail.ru&date=2014-01-01 00:00:01&message=hey hey hey hey!&slug=Threadwithsufficientlylargetitle&isDeleted=true
    cursor = connection.cursor()
    #Тред везде индентефицируется по id => возможно(????)
    #нужно следить что бы не было ошибок во избежание произвольного автоинкементирования
    #возможно нужно вообще убрать автоикремент 

    forum = request.GET["forum"]
    title = request.GET["title"]
    email = request.GET["user"]
    dateThread = request.GET["date"]
    message = request.GET["message"]
    slug = request.GET["slug"]

    isClosed = request.GET.get("isClosed",0)
    isClosed = getBollean(isClosed)

    isDeleted = request.GET.get("isDeleted",0)
    isDeleted = getBollean(isDeleted)

    cursor.execute('''INSERT INTO Thread(forum,user,title,slug,message,dateThread,isClosed,isDeleted) 
                      VALUES ('%s','%s','%s','%s','%s','%s','%d','%d');
                   ''' % (forum,email,title,slug,message,dateThread,isClosed,isDeleted,)) 

    cursor.execute('''SELECT LAST_INSERT_ID();
                   ''')
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
                      SET isClosed = true#возможно надо fasle
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
                      SET isClosed = false#возможно надо true
                      WHERE idThread = %d
                   ''' % (idThread,))

    code = 0
    responce = { "code": code, "response": {"thread":idThread,}}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

