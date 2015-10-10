# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json


def getIdUser(cursor,email):
    cursor.execute('''SELECT idUser
                      FROM User 
                      WHERE email = '%s'
                   ''' % (email,))
    return cursor.fetchone()[0]

def getBollean(variable):
    if(variable=="true" or variable==1 or variable=='1'):
        return True
    else: 
        return False


def DetailsUserWithoutFollowingAndFollowers(cursor,email):
    idUser = getIdUser(cursor,email)

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
    isAnonymous = getBollean(userInfo[3])

    code = 0
    responce = { "code": code, "response":{'subscriptions': subscriptions,
                                           'username': username,
                                           'about': about,
                                           'name': name,
                                           'isAnonymous': isAnonymous,
                                           'idUser': idUser,
                                           'email': email,

    }}
    return responce

def DetailsUser(cursor,email):

    idUser = getIdUser(cursor,email)

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
    isAnonymous = getBollean(userInfo[3])

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
    return responce


def listFollowers(cursor,email,order,limit,since_id):

    idUser = getIdUser(cursor,email)

    if(order == None and limit == None and since_id == None):
        cursor.execute('''SELECT User.email
                          FROM Followers JOIN User
                                         ON Followers.idFollower = User.idUser
                          WHERE Followers.idUser = '%s'
                       ''' % (idUser,))
        return cursor.fetchall()


    if(order == 'desc' or order==None):
        cursor.execute('''SELECT User.email
                          FROM Followers JOIN User
                                         ON Followers.idFollower=User.idUser
                          WHERE Followers.idUser = %d
                          ORDER BY User.name DESC
                       ''' % (idUser))  
        return cursor.fetchall()

    if(order == 'asc'):
        cursor.execute('''SELECT User.email
                          FROM Followers JOIN User
                                         ON Followers.idFollower=User.idUser
                          WHERE Followers.idUser = %d
                          ORDER BY User.name ASC
                       ''' % (idUser))  
        return cursor.fetchall()


def listFollowing(cursor,email,order,limit,since_id):

    idUser = getIdUser(cursor,email)
    if(order == None and limit == None and since_id == None):
        cursor.execute('''SELECT User.email
                          FROM Followers JOIN User
                                         ON Followers.idUser = User.idUser
                          WHERE Followers.idFollower = '%s'
                       ''' % (idUser,))
        return cursor.fetchall()


################################
###дальше функции обработки url
################################

def insertUser(request):#?username=user1&about=hello im user1&isAnonymous=false&name=John&email=example@mail.ru
    cursor = connection.cursor()

    username = request.GET["username"]
    about = request.GET["about"]
    name = request.GET["name"]
    email = request.GET["email"]
    isAnonymous = request.GET["isAnonymous"]
    isAnonymous =getBollean(isAnonymous)

    cursor.execute('''INSERT INTO User(username,about,name,email,isAnonymous) 
                      VALUES ('%s','%s','%s','%s','%d');
                   ''' % (username,about,name,email,isAnonymous,)) 

    idUser = getIdUser(cursor,email)


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
    return HttpResponse(DetailsUser(cursor,email),content_type="application/json")

def followUser(request):
    cursor = connection.cursor()

    followerEmail = request.GET["follower"]
    followeeEmail = request.GET['followee']

    idFollower = getIdUser(cursor,followerEmail)
    idFollowee = getIdUser(cursor,followeeEmail)

    cursor.execute('''INSERT INTO Followers
                      VALUES ('%d','%d')
                   ''' % (idFollowee,idFollower))#не наоборот ли нужно?

    email = followeeEmail
    responce = DetailsUser(cursor,email)

    return HttpResponse(responce,content_type="application/json")

def updateProfile(request):
    cursor = connection.cursor()

    about = request.GET["about"]
    name = request.GET["name"]
    email = request.GET["user"]

    idUser = getIdUser(cursor,email)

    cursor.execute('''UPDATE User
                      SET about = '%s',
                          name = '%s'
                      WHERE email = '%s';
                   ''' % (about,name,email,)) 

    responce = DetailsUser(cursor,email)
    return HttpResponse(responce,content_type="application/json")

def unfollowUser(request):#все скорее всего напутано
    cursor = connection.cursor()

    followerEmail = request.GET["follower"]
    followeeEmail = request.GET['followee']

    idFollower = getIdUser(cursor,followerEmail)
    idFollowee = getIdUser(cursor,followeeEmail)

    cursor.execute('''DELETE FROM Followers
                      WHERE idUser= '%d' AND idFollower = '%d';
                   ''' % (idFollowee,idFollower))

    responce = DetailsUser(cursor,followerEmail)
    return HttpResponse(responce,content_type="application/json")

def listFollowersUser(request):#список подпищиков
    cursor = connection.cursor()
    #вроде как эта штука работает 
    email = request.GET["user"]
    order = request.GET.get("order", None)
    limit = request.GET.get("limit", None)
    since_id = request.GET.get("since_id", None)

    responce = DetailsUserWithoutFollowingAndFollowers(cursor,email)
    followers = listFollowers(cursor,email,order,limit,since_id)
    following = listFollowing(cursor,email,None,None,None)
    responce["response"].setdefault("followers",followers)
    responce["response"].setdefault("following",following)

    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

def listFollowingUser(request):
    cursor = connection.cursor()

    email = request.GET["user"]
    order = request.GET.get("order", None)
    limit = request.GET.get("limit", None)
    since_id = request.GET.get("since_id", None)

    responce = DetailsUserWithoutFollowingAndFollowers(cursor,email)
    followers = listFollowers(cursor,email,None,None,None)#все аналогично как и listFollowersUser кроме этих
    following = listFollowing(cursor,email,order,limit,since_id)#двух строк
    responce["response"].setdefault("followers",followers)
    responce["response"].setdefault("following",following)

    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


