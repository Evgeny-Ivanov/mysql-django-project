# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpRequest,JsonResponse
from django.db import connection
import json
from views.user import getBollean
from views.ancillary import dictfetchall
from views.user import DetailsUser
from views.user import getFollowers
from views.user import getFollowing
from views.user import getSubscriptions,getUserByEmail,getFFS
#вроде все сделано кроме listUsersInForum 


def countPostInThread(cursor,idThread):#Post(idThread,isDeleted)
    cursor.execute('''SELECT COUNT(idPost)
                      FROM Post
                      WHERE idThread = %d AND isDeleted = false
                   ''' % idThread)
    return cursor.fetchone()[0]  


def countPostInForum(cursor,forum):#Post(forum,isDeleted)
    cursor.execute('''SELECT COUNT(idPost)
                      FROM Post
                      WHERE forum = '%s' AND isDeleted = false
                   ''' % forum)
    return cursor.fetchone()[0]  


def getForumByShortName(cursor,shortName):#Forum(short_name)
    cursor.execute('''SELECT idForum AS id,name,short_name,user                      
                      FROM Forum
                      WHERE short_name = '%s'
                   '''%(shortName,))
    return dictfetchall(cursor)

@csrf_exempt
def insertForum(request):#Forum(short_name,idForum) - покрывающий
    cursor = connection.cursor()

    POST = json.loads(request.body)

    name = POST["name"]
    shortName = POST["short_name"]
    email = POST["user"]#user = email

    cursor.execute('''INSERT IGNORE INTO Forum(name,short_name,user) 
                      VALUES ('%s','%s','%s');
                   ''' % (name,shortName,email,))

    cursor.execute('''SELECT idForum
                      FROM Forum
                      WHERE short_name = '%s';
                   ''' % (shortName,))
    idForum = cursor.fetchone()[0]

    requestCopy = request.GET.copy()
    requestCopy.__setitem__('id',idForum)
    code = 0
    responce = { "code": code, "response": getForumByShortName(cursor,shortName)[0] }#если в responce подавать requestCopy то нагрузочный тест не проходит
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


def detailsForum(request):#Forum(short_name)
    cursor = connection.cursor()

    shortName = request.GET['forum']
    related = request.GET.getlist('related',[])


    cursor.execute('''SELECT short_name,name,idForum AS id,user
                      FROM Forum
                      WHERE short_name = '%s';
                   ''' % (shortName,))
    responce = dictfetchall(cursor)[0]

    if 'user' in related:
        email = responce.get('user','')
        user = DetailsUser(cursor,email)
        responce.update({'user':user})

    code = 0
    responce = { "code": code, "response":responce }
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


#?????????????????????????
#User(name,idUser) - ICP Post(forum,user) - для JOIN 
#возможно нужно добавить STRAIGHT_JOIN
def listUsersInForum(request):
    cursor = connection.cursor()

    shortName = request.GET["forum"]

    order = request.GET.get("order", 'desc')#sort order (by name)
    limit = request.GET.get("limit", None)
    if limit is not None:
        limit = int(limit)
    since_id = request.GET.get("since_id", None)
    if since_id is not None:
        since_id = int(since_id)

    #оптимизация mysql - DISTINCT преобразовывается к GROUP BY 
    #можно убрать DISTINCT - за место него Group By только по email
    query = '''SELECT DISTINCT User.email,User.about,User.idUser AS id,User.isAnonymous,User.name,User.username
               FROM User JOIN Post
                         ON User.email = Post.user
               WHERE Post.forum = '%s'
            ''' % (shortName)
#EXPLAIN SELECT User.email,User.about,User.idUser AS id,User.isAnonymous,User.name,User.username  FROM User JOIN Post  ON User.email = Post.user WHERE Post.forum = 'zdfdfxcv' AND User.idUser >= 10  GROUP BY User.email  ORDER BY User.name LIMIT 5;

    if since_id is not None:
        query += " AND User.idUser >= %d "%(since_id)

    query += "ORDER BY User.name %s "%order

    if limit is not None:
        query += " LIMIT %d"%(limit)   

    cursor.execute(query)
    users = dictfetchall(cursor)

    for user in users:
        user.update(getFFS(cursor,user['email']))     

    #нужно видимо хранить в Post и idForum
    #получаем массив мыассивов пользователей, теперь надо как то составить ответ 

    code = 0
    response = { "code": code, "response": users }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")


#Thread(forum,dateThread) - великолепный индекс
def listThreadsInForum(request):
    cursor = connection.cursor()

    shortName = request.GET['forum']
    since = request.GET.get('since',None)#дата треды старше которой нам нужны
    limit = request.GET.get('limit',None)
    if limit is not None:
        limit = int(limit)
    order = request.GET.get('order','DESC')
    related = request.GET.getlist('related',[])#массив Possible values: ['user', 'forum']. Default: []

    query = '''SELECT CAST(dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,
                      message,slug,title,user,forum,likes - dislikes AS points,likes,dislikes
               FROM Thread
               WHERE forum = '%s'
            '''%(shortName,)

    if since is not None:
        query += "AND `dateThread` >= '%s' "%since

    if order is not None:
        query += "ORDER BY dateThread %s"%order

    if limit is not None:
        query += " LIMIT %d "%limit

    cursor.execute(query)
    threads = dictfetchall(cursor)

    for thread in threads:
        if 'user' in related:
            user = DetailsUser(cursor,thread['user'])
            thread.update({'user': user})

        if 'forum' in related:
            forum = getForumByShortName(cursor,thread['forum'])[0]
            forum.update({"posts": countPostInForum(cursor,forum['short_name'])})
            thread.update({'forum': forum})

        thread.update({"posts": countPostInThread(cursor,thread['id'])})

    code = 0
    response = { "code": code, "response": threads }
    response = json.dumps(response,ensure_ascii=False, encoding='utf8')
    return HttpResponse(response,content_type="application/json")

#Post(forum,datePost) - великолепный индекс Thread(idThread)
def listPostsInForum(request):
    cursor = connection.cursor()

    shortName = request.GET['forum']
    since = request.GET.get('since',None)
    limit = request.GET.get('limit',None)
    order = request.GET.get('order','DESC')#sort order (by date)
    related = request.GET.getlist('related',[])#Possible values: ['thread', 'forum', 'user']. Default: []

    query = '''SELECT  idPost AS id,forum,idThread AS thread,user,parent,CAST(datePost AS CHAR) AS `date`,message,
                       isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes, likes - dislikes AS points
               FROM Post
               WHERE forum = '%s'
            '''%(shortName,)

    if since is not None:
        query += "AND `datePost` >= '%s' "%since

    if order is not None:
        query += "ORDER BY datePost %s"%order

    if limit is not None:
        query += " LIMIT %d "%int(limit)

    cursor.execute(query)
    posts = dictfetchall(cursor)

    for post in posts:
        if 'user' in related:
            user = DetailsUser(cursor,post['user'])
            post.update({'user': user})

        if 'forum' in related:
            forum = getForumByShortName(cursor,post["forum"])[0]
            forum.update({"posts": countPostInForum(cursor,forum['short_name'])})
            post.update({'forum': forum})

        if 'thread' in related:
            cursor.execute('''SELECT CAST(dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,
                                     message,slug,title,user,forum,likes,dislikes,posts,likes - dislikes AS points
                              FROM Thread
                              WHERE idThread = %d
                           '''%(post['thread'],))
            thread = dictfetchall(cursor)[0]
            thread.update({"posts": countPostInThread(cursor,thread['id'])})
            post.update({'thread': thread})


    code = 0
    response = { "code": code, "response": posts }
    response = json.dumps(response,ensure_ascii=False, encoding='utf8')
    return HttpResponse(response,content_type="application/json")


               #SELECT  idPost AS id,forum,idThread AS thread,user,parent,CAST(datePost AS CHAR) AS `date`,message,
               #        isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes, likes - dislikes AS points
               #FROM Post
               #WHERE forum = "sdfsdfasdf"
               #AND `datePost` >= 2014-01-01+00%3A00%3A00
               #ORDER BY datePost 
               #LIMIT 10