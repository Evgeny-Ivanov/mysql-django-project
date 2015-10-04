# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def insertUser(request):#?username=user1&about=hello im user1&isAnonymous=false&name=John&email=example@mail.ru
    cursor = connection.cursor()

    username = request.GET["username"]
    about = request.GET["about"]
    name = request.GET["name"]
    email = request.GET["email"]
    isAnonymous = request.GET["isAnonymous"]
    if(isAnonymous=="true"):
        isAnonymous = True
    else: 
        isAnonymous = False

    cursor.execute('''INSERT INTO User(username,about,name,email,isAnonymous) 
                      VALUES ('%s','%s','%s','%s','%d');
                   ''' % (username,about,name,email,isAnonymous,)) 

    cursor.execute('''SELECT idUser
                      FROM User 
                      WHERE email = '%s'
                   ''' % (email,))
    idUser = cursor.fetchone()[0]


    requestCopy = request.GET.copy()
    requestCopy.__setitem__('id',idUser)#setdefault()
    code = 0
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


def detailsUser(request):
    cursor = connection.cursor()
    #Following – ваши подписки или люди, которых вы читаете
    #Followers – это ваши читатели

    email = request.GET["user"]
    cursor.execute('''SELECT idUser
                      FROM User 
                      WHERE email = '%s'
                   ''' % (email,))
    idUser = cursor.fetchone()[0]

    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.idFollower = User.idUser
                      WHERE Followers.idUser = '%s'
                   ''' % (idUser,))
    following = cursor.fetchall()

    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.idUser = User.idUser
                      WHERE Followers.idFollower = '%s'
                   ''' % (idUser,))
    followers = cursor.fetchall()

    cursor.execute('''SELECT idThread
                      FROM Subscriptions
                      WHERE idUser = '%s'
                   ''' % (idUser,))
    subscriptions = cursor.fetchall()

    cursor.execute('''SELECT username,about,name,isAnonymous
                      FROM User
                      WHERE idUser = '%s'
                   ''' % (idUser,))
    userInfo = cursor.fetchone()

    username = userInfo[0]
    about = userInfo[1]
    name = userInfo[2]
    isAnonymous = userInfo[3]
    if(isAnonymous=="true"):
        isAnonymous = True
    else: 
        isAnonymous = False

    code = 0
    responce = { "code": code, "response":{'following': following,#в ответе выводится [[],[],[]] а надо [,,,]
                                           'followers': followers,
                                           'subscriptions': subscriptions,
                                           'username': username,
                                           'about': about,
                                           'name': name,
                                           'isAnonymous': isAnonymous,
                                           'idUser': idUser,
                                           'email': email,

    }}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

#insert into Followers(idUser,idFollower) values(4,1);
#insert into Subscriptions(idUser,idThread) values(4,1);

def followUser(request):
    cursor = connection.cursor()

    followerEmail = request.GET["follower"]
    followeeEmail = request.GET['followee']

    cursor.execute('''SELECT idUser
                      FROM User 
                      WHERE email = '%s'
                   ''' % (followerEmail,))
    idFollower = cursor.fetchone()[0]

    cursor.execute('''SELECT idUser
                      FROM User 
                      WHERE email = '%s'
                   ''' % (followeeEmail,))
    idFollowee = cursor.fetchone()[0]

    cursor.execute('''INSERT INTO Followers
                      VALUES ('%d','%d')
                   ''' % (idFollowee,idFollower))#не наоборот ли нужно?

    #основная логика закончилась
    #дальше тоже самое что и в detailsUser
    idUser = idFollowee
    email = followeeEmail

    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.idFollower = User.idUser
                      WHERE Followers.idUser = '%s'
                   ''' % (idUser,))
    following = cursor.fetchall()

    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.idUser = User.idUser
                      WHERE Followers.idFollower = '%s'
                   ''' % (idUser,))
    followers = cursor.fetchall()

    cursor.execute('''SELECT idThread
                      FROM Subscriptions
                      WHERE idUser = '%s'
                   ''' % (idUser,))
    subscriptions = cursor.fetchall()

    cursor.execute('''SELECT username,about,name,isAnonymous
                      FROM User
                      WHERE idUser = '%s'
                   ''' % (idUser,))
    userInfo = cursor.fetchone()

    username = userInfo[0]
    about = userInfo[1]
    name = userInfo[2]
    isAnonymous = userInfo[3]
    if(isAnonymous=="true"):
        isAnonymous = True
    else: 
        isAnonymous = False

    code = 0
    responce = { "code": code, "response":{'following': following,#в ответе выводится [[],[],[]] а надо [,,,]
                                           'followers': followers,
                                           'subscriptions': subscriptions,
                                           'username': username,
                                           'about': about,
                                           'name': name,
                                           'isAnonymous': isAnonymous,
                                           'idUser': idUser,
                                           'email': email,

    }}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")
