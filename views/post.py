# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json
from views.ancillary import getBollean,dictfetchall,responseErrorCode
from views.user import getUserByEmail
from views.thread import getThreadById
from views.forum import getForumByShortName
#вроде все сделано - но надо проверить вызывается ли insertPost

def updateCountPost(cursor,forum,idThread,value):#Forum(short_name) Thread(idThread)
    cursor.execute('''UPDATE Forum
                      SET posts = posts + %d
                      WHERE short_name = "%s" 
                   ''' % (value,forum) )

    cursor.execute('''UPDATE Thread
                      SET posts = posts + %d
                      WHERE idThread = %d
                   ''' % (value,idThread) ) #нужно еще будет добавить posts в схему


@csrf_exempt
def insertPost(request):#Post(level,parent)
    cursor = connection.cursor()


    POST = json.loads(request.body)

    message = POST["message"]
    datePost = POST["date"]
    email = POST["user"]
    idThread = int(POST["thread"])
    forum = POST["forum"]
    parent = POST.get("parent",None)#None == NULL ?
    if parent is not None:
        parent = int(parent)

    isApproved = POST.get("isApproved",0)
    isApproved = getBollean(isApproved)

    isDeleted = POST.get("isDeleted",0)
    isDeleted = getBollean(isDeleted)

    isEdited = POST.get("isEdited",0)
    isEdited = getBollean(isEdited)

    isHighlighted = POST.get("isHighlighted",0)
    isHighlighted = getBollean(isHighlighted)

    isSpam = POST.get("isSpam",0)
    isSpam = getBollean(isSpam)

    ###########
    #if parent is None:
    #    level = 1
    #    cursor.execute('''SELECT COUNT(*) + 1
    #                      FROM Post 
    #                      WHERE level = %d
    #                   ''' %level )
    #    number = cursor.fetchone()[0]
    #    path = str(number)
    #else:
    #    cursor.execute('''SELECT `path`,level
    #                      FROM Post
    #                      WHERE idPost = %d
    #                  ''' %parent )
    #    pathResponse = cursor.fetchall()[0]
    #    pathParent = pathResponse[0]
    #    level = int(pathResponse[1])+1
    #    cursor.execute('''SELECT COUNT(*)
    #                      FROM Post
    #                      WHERE level = %d AND parent = %d
    #                   ''' %(level,parent))
    #    countThisLevelPost = cursor.fetchone()[0]
    #    countThisLevelPost = int(countThisLevelPost)
    #    path = pathParent + '.' + str(countThisLevelPost+1)
    ##вроде работает но слишком много запросов 
    ########### path и level получены,но надо в десятичной системе -
    ########### максимум сколько можно коментариев на коментарий - 10 
    ########### нужно перевести в другую

    level = 1
    path = "1"

    if parent is None:
        cursor.execute('''INSERT INTO Post(forum, idThread, user, datePost, message,  isEdited, isDeleted, isSpam,  isHighlighted, isApproved , `path`,level) 
                          VALUES          ( '%s',    '%d',  '%s',    '%s'  ,  '%s'     ,'%d'      ,'%d'  , '%d'   ,   '%d'       ,    '%d'    , '%s', %d  );
                       '''              % (forum, idThread, email, datePost, message, isEdited, isDeleted, isSpam,  isHighlighted,  isApproved, path, level  )) 
    else:
        cursor.execute('''INSERT INTO Post(forum, idThread, user, datePost, message,  isEdited, isDeleted, isSpam,  isHighlighted, isApproved, parent  , `path`,level) 
                          VALUES          ( '%s',    '%d',  '%s',    '%s'  ,  '%s'     ,'%d'      ,'%d'  , '%d'   ,   '%d'       ,    '%d'    , '%s'   , '%s',   %d );
                       '''              % (forum, idThread, email, datePost, message, isEdited, isDeleted, isSpam,  isHighlighted,  isApproved, parent , path ,  level ))

    #обновляю количество постов в форуме и в теме
    updateCountPost(cursor,forum,idThread,1)

    cursor.execute('''SELECT LAST_INSERT_ID();
                   ''')
    idPost = cursor.fetchone()[0]

    requestCopy = request.GET.copy()

    requestCopy.__setitem__('id',idPost)
    requestCopy.__setitem__('parent',parent)


    code = 0
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)
    cursor.close()
    return HttpResponse(responce,content_type="application/json")

def getPostById(cursor,idPost):#Post(idPost)
    cursor.execute('''SELECT idPost AS id,forum,idThread AS thread,Post.user,parent,CAST(datePost AS CHAR) AS `date`,
                             message,isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes,likes-dislikes AS points
                      FROM Post
                      WHERE Post.idPost = %d
                   '''%(idPost,))
    return dictfetchall(cursor)

def detailsPost(request):
    cursor = connection.cursor()
    idPost = int(request.GET["post"])
    related = request.GET.getlist("related",[])#['user', 'thread', 'forum']
    post = getPostById(cursor,idPost)
    if not post:
        return HttpResponse(responseErrorCode(1,"error id is not exist"),content_type="application/json")
    post = post[0]

    if 'user' in related:
        user = getUserByEmail(cursor,post['user'])
        post.update({'user':user[0]})
    
    if 'thread' in related:
        thread = getThreadById(cursor,post['thread'])
        post.update({'thread':thread[0]})

    if 'forum' in related:
        forum = getForumByShortName(cursor,post['forum'])
        post.update({'forum':forum[0]})

    code = 0
    response = { "code": code, "response": post }
    response = json.dumps(response)
    cursor.close()
    return HttpResponse(response,content_type="application/json")

@csrf_exempt#POST
def removePost(request):#Update - Post(idPost)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idPost = int(POST["post"])
    
    cursor.execute('''UPDATE Post
                      SET isDeleted = true
                      WHERE idPost = %d
                   ''' % idPost )

    cursor.execute('''SELECT forum,idThread
                      FROM Post
                      WHERE idPost = %d
                   ''' % idPost )
    values = cursor.fetchone()
    forum = values[0]
    idThread = values[1]

    updateCountPost(cursor,forum,idThread,-1)

    code = 0
    response = { "code": code, "response": {"post":idPost} }
    response = json.dumps(response)
    cursor.close()
    return HttpResponse(response,content_type="application/json")

@csrf_exempt#POST
def restorePost(request):#Update - Post(idPost)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idPost = int(POST["post"])

    cursor.execute('''UPDATE Post
                      SET isDeleted = false
                      WHERE idPost = %d
                   ''' % idPost )

    cursor.execute('''SELECT forum,idThread
                      FROM Post
                      WHERE idPost = %d
                   ''' % idPost )
    values = cursor.fetchone()
    forum = values[0]
    idThread = values[1]

    updateCountPost(cursor,forum,idThread,1)

    code = 0
    response = { "code": code, "response": {"post":idPost} }
    response = json.dumps(response)
    cursor.close()
    return HttpResponse(response,content_type="application/json")

@csrf_exempt#POST
def updatePost(request):#Update - Post(idPost)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idPost = int(POST["post"])
    message = POST["message"]

    cursor.execute('''UPDATE Post
                      SET message = '%s'
                      WHERE idPost = %d
                   ''' % (message,idPost,))

    response = getPostById(cursor,idPost)[0]
    code = 0
    response = { "code": code, "response": response }
    response = json.dumps(response)
    cursor.close()
    return HttpResponse(response,content_type="application/json")

@csrf_exempt#POST
def votePost(request):#Update - Post(idPost)
    cursor = connection.cursor()

    POST = json.loads(request.body)
    idPost = int(POST['post'])
    vote = int(POST['vote'])

    if vote == -1:
        cursor.execute('''UPDATE Post
                          SET dislikes = dislikes+1
                          WHERE idPost = %d
                       ''' %idPost )
    if vote == 1: 
        cursor.execute('''UPDATE Post
                          SET likes = likes+1
                          WHERE idPost = %d
                       ''' %idPost)

    response = getPostById(cursor,idPost)[0]
    code = 0
    response = { "code": code, "response": response }
    response = json.dumps(response)
    cursor.close()
    return HttpResponse(response,content_type="application/json")

#GET
def listPost(request):#Post(forum,datePost) Post(idThread,datePost) #шикарные индексы
    cursor = connection.cursor()

    forum = request.GET.get('forum',None)#приходит или форум или тема
    thread = request.GET.get('thread',None)
    if thread is not None:
        thread = int(thread)

    since = request.GET.get('since',None)
    limit = request.GET.get('limit',None)
    if limit is not None:
        limit = int(limit)
    order = request.GET.get('order','DESC')#sort order (by date)

    query = '''SELECT  idPost AS id,forum,idThread AS thread,Post.user,parent,CAST(datePost AS CHAR) AS `date`,message,
                       isEdited,isDeleted,isSpam,isHighlighted,isApproved,likes,dislikes,points
               FROM Post 
            '''
    # что делать с тем что у нас параметры опциональные и они могут поломать индекс?
    if forum is not None:
        query += "WHERE forum = '%s'"%forum

    if thread is not None:
        query += "WHERE idThread = %d "%thread

    if since is not None:
        query += "AND `datePost` >= '%s' "%since

    if order is not None:
        query += "ORDER BY datePost %s"%order

    if limit is not None:
        query += " LIMIT %d "%limit

    cursor.execute(query)
    posts = dictfetchall(cursor)

    code = 0
    response = { "code": code, "response": posts }
    response = json.dumps(response)
    cursor.close()
    return HttpResponse(response,content_type="application/json")