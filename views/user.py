# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json
from views.ancillary import dictfetchall
from views.ancillary import getBollean,helperQuotes


def getUserByEmail(cursor,email):
    cursor.execute('''SELECT about,email,idUser AS id,isAnonymous,name,username
                      FROM User
                      WHERE email = '%s'
                   '''%email )
    return dictfetchall(cursor)

def getFollowing(cursor,email):
    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.follower = User.email
                      WHERE Followers.user = '%s'
                   ''' % (email,))
    return cursor.fetchall()

def getFollowers(cursor,email):
    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.user = User.email
                      WHERE Followers.follower = '%s'
                   ''' % (email,))
    return cursor.fetchall()

def getSubscriptions(cursor,email):
    cursor.execute('''SELECT idThread
                      FROM Subscriptions
                      WHERE user = '%s'
                   ''' % (email,))
    return cursor.fetchall()


def DetailsUserWithoutFollowingAndFollowers(cursor,email):

    cursor.execute('''SELECT idThread
                      FROM Subscriptions
                      WHERE user = '%s'
                   ''' % (email,))
    subscriptions = [item[0] for item in cursor.fetchall()]

    cursor.execute('''SELECT username,about,name,isAnonymous,idUser 
                      FROM User
                      WHERE email = '%s'
                   ''' % (email,))
    userInfo = cursor.fetchone()

    username = userInfo[0]
    about = userInfo[1]
    name = userInfo[2]
    isAnonymous = getBollean(userInfo[3])
    idUser = userInfo[4]

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

def DetailsUser(cursor,email):#GET

    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.follower = User.email
                      WHERE Followers.user = '%s'
                   ''' % (email,))
    following = [item[0] for item in cursor.fetchall()]

    cursor.execute('''SELECT User.email
                      FROM Followers JOIN User
                                     ON Followers.user = User.email
                      WHERE Followers.follower = '%s'
                   ''' % (email,))
    followers = [item[0] for item in cursor.fetchall()]

    cursor.execute('''SELECT idThread
                      FROM Subscriptions
                      WHERE user = '%s'
                   ''' % (email,))
    subscriptions = [item[0] for item in cursor.fetchall()]#как это работает ?

    cursor.execute('''SELECT username,about,name,isAnonymous,idUser
                      FROM User
                      WHERE email = '%s'
                   ''' % (email,))
    userInfo = cursor.fetchone()

    username = userInfo[0]
    about = userInfo[1]
    name = userInfo[2]
    isAnonymous = getBollean(userInfo[3])
    idUser = userInfo[4]

    code = 0
    responce = { "code": code, "response":{'following': following,#в ответе выводится [[],[],[]] а надо [,,,]
                                           'followers': followers,
                                           'subscriptions': subscriptions,
                                           'username': username,
                                           'about': about,
                                           'name': name,
                                           'isAnonymous': isAnonymous,
                                           'id': idUser,
                                           'email': email,

    }}
    return responce


################################
###дальше функции обработки url
################################
###curl -H "Content-Type: application/json" -X POST -d ' {"username": "user1", "about": "hello im user1", "isAnonymous": false, "name": "John", "email": "example@mail.ru"}' http://localhost:8888/db/api/user/create/
################################


@csrf_exempt
def insertUser(request):#?username=user1&about=hello im user1&isAnonymous=false&name=John&email=example@mail.ru
    cursor = connection.cursor()

    POST = json.loads(request.body)
    username = POST.get('username',None)
    about = POST.get('about',None)
    name = POST.get('name',None)
    email = POST['email']
    isAnonymous = POST.get('isAnonymous',False)
    isAnonymous =getBollean(isAnonymous)

    cursor.execute('''SELECT *
                      FROM User
                      WHERE email = '%s'
                   ''' %email)
    user =  cursor.fetchone()
    if user:
        code = 5
        responce = { "code": code, "response": "user exist" }
        responce = json.dumps(responce)
        return HttpResponse(responce,content_type="application/json")

    cursor.execute('''INSERT INTO User(email,username,about,name,isAnonymous) 
                      VALUES ('%s',%s,%s,%s,%d);
                   ''' % (email,helperQuotes(username),helperQuotes(about),helperQuotes(name),isAnonymous,)) 

    cursor.execute('''SELECT idUser
                      FROM User
                      WHERE email = '%s'
                   ''' %email)
    idUser =  cursor.fetchone()[0]

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
    responce = json.dumps(DetailsUser(cursor,email))
    return HttpResponse(responce,content_type="application/json")

@csrf_exempt
def followUser(request):#POST
    cursor = connection.cursor()

    POST = json.loads(request.body)
    followerEmail = POST["follower"]
    followeeEmail = POST['followee']


    cursor.execute('''INSERT INTO Followers
                      VALUES ('%s','%s')
                   ''' % (followerEmail,followeeEmail))#не наоборот ли нужно?

    responce = DetailsUser(cursor,followeeEmail)
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

@csrf_exempt
def updateProfile(request):#POST
    cursor = connection.cursor()

    POST = json.loads(request.body)

    about = POST["about"]
    name = POST["name"]
    email = POST["user"]

    cursor.execute('''UPDATE User
                      SET about = '%s',
                          name = '%s'
                      WHERE email = '%s';
                   ''' % (about,name,email,)) 

    responce = DetailsUser(cursor,email)
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

@csrf_exempt
def unfollowUser(request):#все скорее всего напутано
    cursor = connection.cursor()

    POST = json.loads(request.body)
    followerEmail = POST["follower"]
    followeeEmail = POST['followee']

    cursor.execute('''DELETE FROM Followers
                      WHERE user = '%s' AND follower = '%s';
                   ''' % (followeeEmail,followerEmail))

    responce = DetailsUser(cursor,followeeEmail)
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

def listFollowersUser(request):#список подпищиков
    cursor = connection.cursor()
    #вроде как эта штука работает 
    email = request.GET["user"]
    order = request.GET.get("order", 'DESC')
    limit = request.GET.get("limit", None)
    since_id = request.GET.get("since_id", None)

    responce = DetailsUserWithoutFollowingAndFollowers(cursor,email)

    #видимо надо перестроить запрос так как нам нужны id-шники
    query = '''SELECT follower
               FROM Followers
               WHERE user = '%s'
               ORDER BY follower %s
            ''' % (email,order)

    if limit is not None:
        query += "LIMIT %d "%limit

    if since_id is not None:#????????????? надо узнать чей это id 
        query += " %s "%since_id

    cursor.execute(query)
    followers = cursor.fetchall()

    cursor.execute('''SELECT user
                      FROM Followers
                      WHERE follower = '%s'
                   '''%(email,))
    following = cursor.fetchall()

    responce["response"].setdefault("followers",followers)
    responce["response"].setdefault("following",following)

    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

def listFollowingUser(request):
    #копипаста прошлого
    cursor = connection.cursor()

    email = request.GET["user"]
    order = request.GET.get("order", 'DESC')
    limit = request.GET.get("limit", None)
    since_id = request.GET.get("since_id", None)

    responce = DetailsUserWithoutFollowingAndFollowers(cursor,email)

    query = '''SELECT user
               FROM Followers
               WHERE follower = '%s'
               ORDER BY user %s
            ''' % (email,order)

    if limit is not None:
        query += "LIMIT %d "%limit

    if since_id is not None:#?????????????
        query += " %s "%since_id

    cursor.execute(query)
    followers = cursor.fetchall()

    cursor.execute('''SELECT follower
                      FROM Followers
                      WHERE user = '%s'
                   '''%(email,))
    following = cursor.fetchall()

    responce["response"].setdefault("followers",followers)
    responce["response"].setdefault("following",following)

    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

def listPostsUser(request):
    cursor = connection.cursor()

    email = request.GET["user"]
    order = request.GET.get("order", 'DESC')
    limit = request.GET.get("limit", None)
    since = request.GET.get("since", None)#дата посты старше которых нужно вывести

    query = '''SELECT idPost AS id,forum,idThread AS thread,Post.user,parent,CAST(datePost AS CHAR) AS `date`,
                      message,isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes,likes-dislikes AS points
               FROM Post 
               WHERE user = '%s'
            ''' % email

    if since is not None:
        query += " AND `datePost` >= '%s' "%since

    query +=" ORDER BY user %s " %order

    if limit is not None:
        query += " LIMIT %d "%int(limit)

    cursor.execute(query)
    response = dictfetchall(cursor)

    code = 0
    response = { "code": code, "response":response }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")


