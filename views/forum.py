# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest,JsonResponse
from django.db import connection
import json
from views.user import getIdUser,getBollean

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

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

    idUser = getIdUser(cursor,email)

    cursor.execute('''INSERT INTO Forum(name,shortName,idUser) 
                      VALUES ('%s','%s','%s');
                   ''' % (name,shortName,idUser,))

    cursor.execute('''SELECT idForum
                      FROM Forum
                      WHERE shortName = '%s';
                   ''' % (shortName,))
    idForum = cursor.fetchone()[0]

    requestCopy = request.GET.copy()
    requestCopy.__setitem__('id',idForum)
    code = 0
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")
#######не работает
def listUsersInForum(request):#в Post должен храниться и форум
    cursor = connection.cursor()

    shortName = request.GET["forum"]
    order = request.GET.get("order", 'desc')
    limit = request.GET.get("limit", None)
    since_id = request.GET.get("since_id", None)

    idForum = getIdForum(cursor,shortName)

    cursor.execute('''SELECT DISTINCT User.*,Followers.id#блять как не удобно по id , опять джойнить ? 
                      FROM Thread JOIN Post              #это может быть быстрее ?
                                  ON Thread.idThread = Post.idThread
                                  JOIN User 
                                  ON User.idUser = Post.idUser

                                  JOIN Subscriptions 
                                  ON Subscriptions.idUser = User.idUser
                                  JOIN Followers 
                                  ON Followers.idUser = User.idUser

                      WHERE Thread.idThread = %d
                      ORDER BY User.name %s;
                   ''' % (idForum,order))
    responce = cursor.fetchall()#нужно видимо хранить в Post и idForum
    #получаем массив мыассивов пользователей, теперь надо как то составить ответ 

    code = 0
    responce = { "code": code, "response": responce }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")


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