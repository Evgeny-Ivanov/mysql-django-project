# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json
from views.ancillary import getBollean,dictfetchall
from views.user import getUserByEmail
from views.forum import getForumByShortName

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


def detailsThread(request):
    cursor = connection.cursor()

    idThread = int(request.GET["thread"])
    related = request.GET.getlist("related",[])#Possible values: ['user', 'forum']

    thread = getThreadById(cursor,idThread)[0]

    if 'user' in related:
        user = getUserByEmail(cursor,thread['user'])[0]
        thread.update({'user': user})

    if 'forum' in related:
        forum = getForumByShortName(cursor,thread['forum'])[0]
        thread.update({'forum': forum})

    code = 0
    response = { "code": code, "response": thread}
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

def voteThread(request):
    cursor = connection.cursor()

    idThread = int(request.GET['thread'])
    vote = int(request.GET['vote'])

    if vote == -1:
        cursor.execute('''UPDATE Thread
                          SET dislikes = dislikes+1
                          WHERE idThread = %d
                       ''' %idThread )
    if vote == 1: 
        cursor.execute('''UPDATE Thread
                          SET likes = likes+1
                          WHERE idThread = %d
                       ''' %idThread)

    response = getThreadById(cursor,idThread)[0]
    code = 0
    response = { "code": code, "response": response }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

def updateThread(request):#POST
    cursor = connection.cursor()

    idThread = int(request.GET["thread"])
    message = request.GET["message"]
    slug = request.GET['slug']

    cursor.execute('''UPDATE Thread
                      SET message = '%s',
                          slug = '%s'
                      WHERE idThread = %d
                   ''' % (message,slug,idThread,))

    response = getThreadById(cursor,idThread)[0]
    code = 0
    response = { "code": code, "response": response }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

def subscribeThread(request):#POST
    cursor = connection.cursor()

    user = request.GET['user']
    idThread = int(request.GET['thread'])

    cursor.execute('''INSERT INTO Subscriptions(user,idThread)
                      VALUES ('%s',%d)
                   ''' % (user,idThread,) )
    code = 0
    response = { "code": code, "response": request.GET }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

def unsubscribeThread(request):#POST
    cursor = connection.cursor()

    user = request.GET['user']
    idThread = int(request.GET['thread'])

    cursor.execute('''DELETE FROM Subscriptions
                      WHERE user = '%s' AND idThread = %d
                   ''' % (user,idThread,) )
    code = 0
    response = { "code": code, "response": request.GET }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

def listThread(request):#GET #вроде работает, но на работоспособность особо не проверял (лень)
    cursor = connection.cursor()

    #Requried forum or user
    forum = request.GET.get('forum',None)
    user = request.GET.get('user',None)

    #Optional
    since = request.GET.get('since',None)
    limit = request.GET.get('limit',None)
    if limit is not None:
        limit = int(limit)
    order = request.GET.get('order','DESC')#sort order (by date)

    query = '''SELECT CAST(dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,
                      message,slug,title,user,forum,points,likes,dislikes,posts
               FROM Thread 
            '''

    if forum is not None:
        query += "WHERE forum = '%s'"%forum

    if user is not None:
        query += "WHERE user = '%s' "%user


    if since is not None:
        query += "AND `dateThread` >= '%s' "%since

    if order is not None:
        query += "ORDER BY dateThread %s"%order

    if limit is not None:
        query += " LIMIT %d "%limit

    cursor.execute(query)
    posts = dictfetchall(cursor)

    code = 0
    response = { "code": code, "response": posts }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")


def removeThread(request):#POST
    cursor = connection.cursor()

    idThread = int(request.GET['thread'])

    cursor.execute('''UPDATE Thread JOIN Post 
                                    ON Thread.idThread = Post.idThread
                      SET Thread.isDeleted = true,
                          Post.isDeleted = true
                      WHERE Thread.idThread = %d
                   ''' %idThread )

    code = 0
    response = { "code": code, "response": request.GET }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")

def restoreThread(request):#POST
    cursor = connection.cursor()

    idThread = int(request.GET['thread'])

    cursor.execute('''UPDATE Thread JOIN Post 
                                    ON Thread.idThread = Post.idThread
                      SET Thread.isDeleted = false,
                          Post.isDeleted = false
                      WHERE Thread.idThread = %d 
                   ''' %idThread )

    code = 0
    response = { "code": code, "response": request.GET }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")

    # не реализованы:
    #   listPosts
    #   restore
  