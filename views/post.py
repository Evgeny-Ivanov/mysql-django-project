# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json
from views.user import getBollean

def insertPost(request):#работает, но нужно разобраться с path
    cursor = connection.cursor()

    message = request.GET["message"]
    datePost = request.GET["date"]
    email = request.GET["user"]
    idThread = int(request.GET["thread"])
    forum = request.GET["forum"]
    parent = request.GET.get("parent",None)#None == NULL ?
    if parent is not None:
        parent = int(parent)

    isApproved = request.GET.get("isApproved",0)
    isApproved = getBollean(isApproved)

    isDeleted = request.GET.get("isDeleted",0)
    isDeleted = getBollean(isDeleted)

    isEdited = request.GET.get("isEdited",0)
    isEdited = getBollean(isEdited)

    isHighlighted = request.GET.get("isHighlighted",0)
    isHighlighted = getBollean(isHighlighted)

    isSpam = request.GET.get("isSpam",0)
    isSpam = getBollean(isSpam)


    path = ' '#эту штуку видимо надо генерить исходя из path родителя 
              #нужно будет для сортировки

    #костыль чтоб записать в Parent NULL
    if parent is None:
        cursor.execute('''INSERT INTO Post(forum, idThread, user, datePost, message,  isEdited, isDeleted, isSpam,  isHighlighted, isApproved , `path`) 
                          VALUES          ( '%s',    '%d',  '%s',    '%s'  ,  '%s'     ,'%d'      ,'%d'  , '%d'   ,   '%d'       ,    '%d'    , '%s'  );
                       '''              % (forum, idThread, email, datePost, message, isEdited, isDeleted, isSpam,  isHighlighted,  isApproved, path  )) 
    else:
        cursor.execute('''INSERT INTO Post(forum, idThread, user, datePost, message,  isEdited, isDeleted, isSpam,  isHighlighted, isApproved, parent  , `path`) 
                          VALUES          ( '%s',    '%d',  '%s',    '%s'  ,  '%s'     ,'%d'      ,'%d'  , '%d'   ,   '%d'       ,    '%d'    , '%s'   , '%s'  );
                       '''              % (forum, idThread, email, datePost, message, isEdited, isDeleted, isSpam,  isHighlighted,  isApproved, parent , path  ))

    requestCopy = request.GET.copy()

    cursor.execute('''SELECT LAST_INSERT_ID();
                   ''')
    idPost = cursor.fetchone()[0]

    requestCopy.__setitem__('id',idPost)
    requestCopy.__setitem__('parent',parent)


    code = 0
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")

