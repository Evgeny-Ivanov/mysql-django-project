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
from views.user import getSubscriptions


def getForumByShortName(cursor,shortName):
    cursor.execute('''SELECT idForum AS id,name,short_name,user                      
                      FROM Forum
                      WHERE short_name = '%s'
                   '''%(shortName,))
    return dictfetchall(cursor)

@csrf_exempt
def insertForum(request):#insertForum?name=Forum With Sufficiently Large Name3&short_name=forumwithsufficientlylargename3&user=example3@mail.ru
    cursor = connection.cursor()

    POST = json.loads(request.body)

    name = POST["name"]
    shortName = POST["short_name"]
    email = POST["user"]#user = email

    cursor.execute('''INSERT INTO Forum(name,short_name,user) 
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
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")


def detailsForum(request):#GET
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
        responceDetailsUser = DetailsUser(cursor,email)
        user = responceDetailsUser["response"]
        responce.update({'user':user})

    code = 0
    responce = { "code": code, "response":responce }
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")



def listUsersInForum(request):#вроде работает, но вывод followers,following,subscriptions нужно поменять(выводятся как в массиве)
    cursor = connection.cursor()

    shortName = request.GET["forum"]

    order = request.GET.get("order", 'desc')#sort order (by name)
    limit = request.GET.get("limit", None)
    if limit is not None:
        limit = int(limit)
    since_id = request.GET.get("since_id", None)
    if since_id is not None:
        since_id = int(since_id)

    query = '''SELECT DISTINCT User.email,User.about,User.idUser AS id,User.isAnonymous,User.name,User.username
               FROM Post JOIN User
                         ON User.email = Post.user
               WHERE Post.forum = '%s'
            ''' % (shortName)

    if since_id is not None:
        query += " AND User.idUser >= %d "%(since_id)

    query += "ORDER BY User.name %s "%order

    if limit is not None:
        query += " LIMIT %d"%(limit)   

    cursor.execute(query)
    users = dictfetchall(cursor)

    for user in users:
        followers = getFollowers(cursor,user['email'])
        user.update({'followers': followers})

        following = getFollowing(cursor,user['email'])
        user.update({'following': following})

        subscriptions = getSubscriptions(cursor,user['email'])
        user.update({'subscriptions': subscriptions})        

    #нужно видимо хранить в Post и idForum
    #получаем массив мыассивов пользователей, теперь надо как то составить ответ 

    code = 0
    response = { "code": code, "response": users }
    response = json.dumps(response)

    return HttpResponse(response,content_type="application/json")


def listThreadsInForum(request):
    cursor = connection.cursor()

    shortName = request.GET['forum']
    since = request.GET.get('since',None)#дата треды старше которой нам нужны
    #import datetime
    #if since is not None:
    #   since = datetime.datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    limit = request.GET.get('limit',None)
    if limit is not None:
        limit = int(limit)
    order = request.GET.get('order','DESC')
    related = request.GET.getlist('related',[])#массив Possible values: ['user', 'forum']. Default: []

    #что такое posts и points?
    query = '''SELECT CAST(Thread.dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,
                      message,slug,title,Thread.user,Thread.forum,points,likes,dislikes,posts
               FROM Forum JOIN Thread
                          ON Forum.short_name = Thread.forum
               WHERE Forum.short_name = '%s'
            '''%(shortName,)

    if since is not None:#удивительно но работает
        query += "AND `dateThread` >= '%s' "%since

    if order is not None:
        query += "ORDER BY dateThread %s"%order

    if limit is not None:
        query += " LIMIT %d "%limit

    cursor.execute(query)
    threads = dictfetchall(cursor)

    for thread in threads:
        if 'user' in related:
            cursor.execute('''SELECT * 
                              FROM User
                              WHERE email = '%s'
                          '''%(thread['user'],))
            user = dictfetchall(cursor)
            thread.update({'user': user[0]})

        if 'forum' in related:
            cursor.execute('''SELECT * 
                              FROM Forum
                              WHERE short_name = '%s'
                           '''%(thread['forum'],))
            forum = dictfetchall(cursor)
            thread.update({'forum': forum[0]})

    code = 0
    responce = { "code": code, "response": threads }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")

def listPostsInForum(request):
    cursor = connection.cursor()

    shortName = request.GET['forum']
    since = request.GET.get('since',None)
    limit = request.GET.get('limit',None)
    if limit is not None:
        limit = int(limit)
    order = request.GET.get('order','DESC')#sort order (by date)
    related = request.GET.getlist('related',[])#Possible values: ['thread', 'forum', 'user']. Default: []

    #datetime.datetime(2014, 1, 1, 0, 0, 1, tzinfo=<UTC>) is not JSON serializable - костыль - перечисление всех полей
    query = '''SELECT  idPost AS id,forum,idThread AS thread,Post.user,parent,CAST(datePost AS CHAR) AS `date`,message,
                       isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes,points
               FROM Forum JOIN Post
                          ON Forum.short_name = Post.forum
               WHERE Forum.short_name = '%s'
            '''%(shortName,)

    if since is not None:
        query += "AND `datePost` >= '%s' "%since

    if order is not None:
        query += "ORDER BY datePost %s"%order

    if limit is not None:
        query += " LIMIT %d "%limit

    cursor.execute(query)
    posts = dictfetchall(cursor)

    for post in posts:
        if 'user' in related:
            cursor.execute('''SELECT * 
                              FROM User
                              WHERE email = '%s'
                          '''%(post['user'],))
            user = dictfetchall(cursor)
            post.update({'user': user[0]})

        if 'forum' in related:
            cursor.execute('''SELECT * 
                              FROM Forum
                              WHERE short_name = '%s'
                           '''%(post['forum'],))
            forum = dictfetchall(cursor)
            post.update({'forum': forum[0]})

        if 'thread' in related:
            cursor.execute('''SELECT CAST(dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,
                                     message,slug,title,user,forum,points,likes,dislikes,posts
                              FROM Thread
                              WHERE idThread = %d
                           '''%(post['thread'],))
            thread = dictfetchall(cursor)
            post.update({'thread': thread[0]})


    code = 0
    responce = { "code": code, "response": posts }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")