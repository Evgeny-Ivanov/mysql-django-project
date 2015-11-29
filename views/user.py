# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json
from views.ancillary import dictfetchall
from views.ancillary import getBollean,helperQuotes
from django.http import JsonResponse
#вроде все сделано - но ICP ?


def getFFS(cursor,email):

    following = getFollowing(cursor,email)
    followers = getFollowers(cursor,email)
    subscriptions = getSubscriptions(cursor,email)

    return {
        'following': following,
        'followers': followers,
        'subscriptions': subscriptions
    }


def getUserByEmail(cursor,email):#User(email)
    cursor.execute('''SELECT about,email,idUser AS id,isAnonymous,name,username
                      FROM User
                      WHERE email = '%s'
                   '''%email )
    return dictfetchall(cursor)

def getFollowing(cursor,email):#Followers(user,follower) - покрывающий 
    cursor.execute('''SELECT follower
                      FROM Followers
                      WHERE user = '%s'
                   ''' % (email,))
    return [item[0] for item in cursor.fetchall()]

def getFollowers(cursor,email):#Followers(follower,user) - покрывающий 
    cursor.execute('''SELECT user
                      FROM Followers
                      WHERE follower = '%s'
                   ''' % (email,))
    return [item[0] for item in cursor.fetchall()]

def getSubscriptions(cursor,email):#Subscriptions(user,idThread) - покрывающий
    cursor.execute('''SELECT idThread
                      FROM Subscriptions
                      WHERE user = '%s'
                   ''' % (email,))
    return [item[0] for item in cursor.fetchall()]


def DetailsUserWithoutFollowingAndFollowers(cursor,email):
    subscriptions = getSubscriptions(cursor,email)

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

    responce = {'subscriptions': subscriptions,
                'username': username,
                'about': about,
                'name': name,
                'isAnonymous': isAnonymous,
                'id': idUser,
                'email': email,
               }
    return responce

def DetailsUser(cursor,email):#GET

    following = getFollowing(cursor,email)
    followers = getFollowers(cursor,email)
    subscriptions = getSubscriptions(cursor,email)

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
    responce = {'following': following,
                 'followers': followers,
                 'subscriptions': subscriptions,
                 'username': username,
                 'about': about,
                 'name': name,
                 'isAnonymous': isAnonymous,
                 'id': idUser,
                 'email': email,
    }
    return responce


################################
###дальше функции обработки url
################################
###curl -H "Content-Type: application/json" -X POST -d ' {"username": "user1", "about": "hello im user1", "isAnonymous": false, "name": "John", "email": "example@mail.ru"}' http://localhost:8888/db/api/user/create/
################################


@csrf_exempt#User(email) User(email,idUser) - покрывающий
def insertUser(request):#Insert User
    cursor = connection.cursor()

    POST = json.loads(request.body)
    username = POST.get('username',None)
    about = POST.get('about',None)
    name = POST.get('name',None)
    email = POST['email']
    isAnonymous = POST.get('isAnonymous',False)
    isAnonymous =getBollean(isAnonymous)

    cursor.execute('''SELECT email
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
    response = DetailsUser(cursor,email)
    response = { "code": 0,
                 "response": response
    }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

@csrf_exempt
def followUser(request):#Insert Followers
    #выскочило 4 пятисотки 
    cursor = connection.cursor()

    POST = json.loads(request.body)
    followerEmail = POST["follower"]
    followeeEmail = POST['followee']

    cursor.execute('''INSERT IGNORE INTO Followers
                      VALUES ('%s','%s')
                   ''' % (followerEmail,followeeEmail))#не наоборот ли нужно?

    response = DetailsUser(cursor,followeeEmail)
    response = { "code": 0,
                 "response": response
    }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

@csrf_exempt
def updateProfile(request):# Update User
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

    response = DetailsUser(cursor,email)
    response = { "code": 0,
                 "response": response
    }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")

@csrf_exempt
def unfollowUser(request):#Delete Followers
    cursor = connection.cursor()

    POST = json.loads(request.body)
    followerEmail = POST["follower"]
    followeeEmail = POST['followee']

    cursor.execute('''DELETE FROM Followers
                      WHERE user = '%s' AND follower = '%s';
                   ''' % (followerEmail,followeeEmail))

    response = DetailsUser(cursor,followeeEmail)
    response = { "code": 0,
                 "response": response
    }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")


#SELECT follower as email
#FROM Followers JOIN User 
#              ON Followers.follower = User.email
#WHERE user = '%s' 
#AND User.idUser >= %d ORDER BY name %s 
#LIMIT %d 

#User(name,idUser) -?(ICP) Followers(user,follower)
def listFollowersUser(request):#список подпищиков
    cursor = connection.cursor()
    #вроде как эта штука работает 
    email = request.GET["user"]
    order = request.GET.get("order", 'DESC')
    limit = request.GET.get("limit", None)
    since_id = request.GET.get("since_id", None)

    query = '''SELECT about,email,idUser AS id,isAnonymous,name,username
               FROM User JOIN Followers
                              ON Followers.follower = User.email
               WHERE user = '%s' 
            ''' %email

    if since_id is not None:
        query += " AND User.idUser >= %d "% int(since_id)

    query += " ORDER BY name %s " % order

    if limit is not None:
        query += " LIMIT %d "%int(limit)

    cursor.execute(query)

    users = dictfetchall(cursor)

    for user in users:
        user.update(getFFS(cursor,user["email"]))


    code = 0
    responce = { "code": code, "response":users }
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

#User(name,idUser) -?(ICP) Followers(follower,user)
def listFollowingUser(request):
    #копипаста прошлого
    cursor = connection.cursor()

    email = request.GET["user"]
    order = request.GET.get("order", 'DESC')
    limit = request.GET.get("limit", None)
    since_id = request.GET.get("since_id", None)

    query = '''SELECT about,email,idUser AS id,isAnonymous,name,username
               FROM Followers JOIN User
                              ON Followers.user = User.email
               WHERE follower = '%s'
            ''' % email

    if since_id is not None:#????????????? надо узнать чей это id 
        query += " AND User.idUser >= %d "% int(since_id)

    query += " ORDER BY name %s" % order

    if limit is not None:
        query += " LIMIT %d "%int(limit)


    cursor.execute(query)
    #following = [item[0] for item in cursor.fetchall()]
    users = dictfetchall(cursor)

    for user in users:
        user.update(getFFS(cursor,user["email"]))

    code = 0
    response = { "code": code, "response":users }
    response = json.dumps(response)
    return HttpResponse(response,content_type="application/json")



#SELECT idPost AS id,forum,idThread AS thread,Post.user,parent,CAST(datePost AS CHAR) AS `date`,
#      message,isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes,likes-dislikes AS points
#FROM Post 
#WHERE user = 'l0yw73d@mail.ru'
#AND `datePost` >= '%s' desc
#ORDER BY datePost 
#LIMIT 85

#Post(user,datePost)
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

    query +=" ORDER BY datePost %s " %order

    if limit is not None:
        query += " LIMIT %d "%int(limit)

    cursor.execute(query)
    response = dictfetchall(cursor)

    code = 0
    response = { "code": code, "response":response }
    response = json.dumps(response,ensure_ascii=False, encoding='utf8')
    return HttpResponse(response,content_type="application/json")
