# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest,JsonResponse
from django.db import connection
import json
from views.user import getBollean
from views.ancillary import dictfetchall
from views.user import DetailsUser
from views.user import getFollowers
from views.user import getFollowing
from views.user import getSubscriptions


def getIdForum(cursor,shortName):
    cursor.execute('''SELECT idForum
                      FROM Forum
                      WHERE shortName = '%s'
                   ''' % (shortName,))
    return cursor.fetchone()[0]

def insertForum(request):#insertForum?name=Forum With Sufficiently Large Name3&short_name=forumwithsufficientlylargename3&user=example3@mail.ru
    cursor = connection.cursor()

    name = request.GET["name"]
    shortName = request.GET["short_name"]
    email = request.GET["user"]#user = email

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


def detailsForum(request):
    cursor = connection.cursor()

    shortName = request.GET['short_name']
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
               ORDER BY User.name %s
            ''' % (shortName,order)
  
    if limit is not None:
        query += " LIMIT %d"%(limit)   
        #########            могут ли limit и since_id сочетаться? 
    if since_id is not None:
        query += " LIMIT %d,100000000"%(since_id)#костыль

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

    import time

    shortName = request.GET['forum']
    since = request.GET.get('since',None)#дата треды старше которой нам нужны
    since = time.strptime(since, "%Y-%m-%d %H:%M:%S")
    limit = int(request.GET.get('limit',None))
    order = request.GET.get('order','DESC')
    related = request.GET.getlist('related',[])#массив Possible values: ['user', 'forum']. Default: []

    idForum = getIdForum(cursor,shortName)

    #dislikes,likes,points,posts
    query = '''SELECT CAST(Thread.dateThread AS CHAR) AS `date`,idThread AS id,isClosed,isDeleted,message,slug,title,Thread.idUser AS user,Thread.idForum AS forum
               FROM Forum JOIN Thread
                          ON Forum.idForum = Thread.idForum
               WHERE Forum.shortName = '%s'
            '''%(shortName,)

    if since is not None:
        query += "AND `dateThread` >= %s "%since

    if limit is not None:
        query += "LIMIT %d "%limit

    cursor.execute(query)
    threads = dictfetchall(cursor)

    for thread in threads:
        if 'user' in related:
            cursor.execute('''SELECT * 
                              FROM User
                              WHERE idUser = %d;
                          '''%(thread['user'],))
            user = dictfetchall(cursor)
            thread.update({'user': user[0]})

        if 'forum' in related:
            cursor.execute('''SELECT * 
                              FROM Forum
                              WHERE idForum = %d;
                           '''%(thread['forum'],))
            forum = dictfetchall(cursor)
            thread.update({'forum': forum[0]})

    code = 0
    responce = { "code": code, "response": threads }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")