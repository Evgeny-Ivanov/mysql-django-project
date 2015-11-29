# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json
from views.ancillary import getBollean,dictfetchall,responseErrorCode
from views.user import getUserByEmail
from views.forum import getForumByShortName


def countPostInThread(cursor,idThread):#Post(idThread,isDeleted)
    cursor.execute('''SELECT COUNT(idPost)
                      FROM Post
                      WHERE idThread = %d AND isDeleted = 0
                   ''' % idThread)
    return cursor.fetchone()[0]  

def getThreadById(cursor,idThread):#Thread(idThread)
    countPost = countPostInThread(cursor,idThread)

    cursor.execute('''SELECT CAST(dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,
                             message,slug,title,user,forum,likes,dislikes,likes-dislikes AS points
                      FROM Thread
                      WHERE idThread = %d
                   '''%idThread )
    response = dictfetchall(cursor)
    response[0].setdefault('posts',countPost)
    return response

#{"forum": "forum1", "title": "Thread With Sufficiently Large Title", "isClosed": true, "user": "example3@mail.ru", "date": "2014-01-01 00:00:01", "message": "hey hey hey hey!", "slug": "Threadwithsufficientlylargetitle", "isDeleted": true}

@csrf_exempt#что быстрее - AST_INSERT_ID() или SELECT id WHERE ?
def insertThread(request):
    cursor = connection.cursor()

    POST = json.loads(request.body)
    forum = POST["forum"]
    title = POST["title"]
    email = POST["user"]
    dateThread = POST["date"]
    message = POST["message"]
    slug = POST["slug"]

    isClosed = POST.get("isClosed",0)
    isClosed = getBollean(isClosed)

    isDeleted = POST.get("isDeleted",0)
    isDeleted = getBollean(isDeleted)

    cursor.execute('''INSERT IGNORE INTO Thread(forum,user,title,slug,message,dateThread,isClosed,isDeleted) 
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

@csrf_exempt
def closeThread(request):#Thread(idThread)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idThread = POST["thread"]
    idThread = int(idThread)
    cursor.execute('''UPDATE Thread
                      SET isClosed = true
                      WHERE idThread = %d
                   ''' % (idThread,))

    code = 0
    responce = { "code": code, "response": {"thread":idThread,}}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

@csrf_exempt
def openThread(request):#Thread(idThread)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idThread = POST["thread"]
    idThread = int(idThread)
    
    cursor.execute('''UPDATE Thread
                      SET isClosed = false
                      WHERE idThread = %d
                   ''' % (idThread,))

    code = 0
    responce = { "code": code, "response": {"thread":idThread,}}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


def detailsThread(request):#GET
    cursor = connection.cursor()

    idThread = int(request.GET["thread"])
    related = request.GET.getlist("related",[])#Possible values: ['user', 'forum']

    thread = getThreadById(cursor,idThread)[0]

    checking3 = set(related)-set(['user', 'forum'])
    if checking3:
        return HttpResponse(responseErrorCode(3,"thread can not be in related"),content_type="application/json")

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

@csrf_exempt
def voteThread(request):#Thread(idThread)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idThread = int(POST['thread'])
    vote = int(POST['vote'])

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

@csrf_exempt
def updateThread(request):#Thread(idThread)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idThread = int(POST["thread"])
    message = POST["message"]
    slug = POST['slug']

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

@csrf_exempt
def subscribeThread(request):#POST
    cursor = connection.cursor()

    POST = json.loads(request.body)
    user = POST['user']
    idThread = int(POST['thread'])

    cursor.execute('''INSERT IGNORE INTO Subscriptions(user,idThread)
                      VALUES ('%s',%d)
                   ''' % (user,idThread,) )
    code = 0
    response = { "code": code, "response": POST }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

@csrf_exempt
def unsubscribeThread(request):#Subscriptions(idThread,user)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    user = POST['user']
    idThread = int(POST['thread'])

    cursor.execute('''DELETE FROM Subscriptions
                      WHERE user = '%s' AND idThread = %d
                   ''' % (user,idThread,) )
    code = 0
    response = { "code": code, "response": POST }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

#Thread(forum,dateThread) и Thread(user,dateThread) - шикарные индексы
def listThread(request):#GET 
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
                      message,slug,title,user,forum,likes - dislikes AS points,likes,dislikes,posts
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

    for post in posts:
        post.update({"posts": countPostInThread(cursor,post['id'])})

    code = 0
    response = { "code": code, "response": posts }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")

@csrf_exempt
def removeThread(request):#POST #удалил JOIN к POST  - надо исправить
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idThread = int(POST['thread'])

    cursor.execute('''UPDATE Thread
                      SET isDeleted = 1
                      WHERE idThread = %d
                   ''' %idThread )

    cursor.execute('''UPDATE Post
                      SET isDeleted = 1
                      WHERE idThread = %d
                   ''' %idThread )

    code = 0
    response = { "code": code, "response": POST }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")

@csrf_exempt
def restoreThread(request):#POST
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idThread = int(POST['thread'])

    cursor.execute('''UPDATE Thread
                      SET isDeleted = 0
                      WHERE idThread = %d
                   ''' %idThread )

    cursor.execute('''UPDATE Post
                      SET isDeleted = 0
                      WHERE idThread = %d
                   ''' %idThread )
    code = 0
    response = { "code": code, "response": POST }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")

#Post(idThread,datePost)
def listPosts(request):#не реализован parent_tree
    cursor = connection.cursor()
    #Requried
    thread = int(request.GET.get('thread',None))
    #Optional
    since = request.GET.get('since',None)
    limit = request.GET.get('limit',None)
    if limit is not None:
        limit = int(limit)
    order = request.GET.get('order','DESC')#sort order (by date)
    sort = request.GET.get('sort','flat')

    query = '''SELECT  idPost AS id,forum,idThread AS thread,Post.user,parent,CAST(datePost AS CHAR) AS `date`,message,
                       isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes,likes - dislikes AS points
               FROM Post 
               WHERE idThread = %d
            ''' %thread

    if since is not None:
        query += "AND `datePost` >= '%s' "%since

    if sort is not None:
        if sort == 'flat':
            query += "ORDER BY datePost %s"%order
        if sort == 'tree':#видими 2 нижних метода не вызываются
            query += "ORDER BY `path` %s"%order
        if sort == 'parent_tree':#тут надо доработать
            query += ''' AND CAST( LEFT( `path`, INSTR(`path`,".")-1 ) AS INT ) > %d
                         ORDER BY `path` %s''' % (limit,order)

    if limit is not None and not sort ==  'parent_tree':
        query += " LIMIT %d "%limit

    cursor.execute(query)
    posts = dictfetchall(cursor)

    code = 0
    response = { "code": code, "response": posts }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")
  