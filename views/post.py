# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json


def insertPost(request):
    cursor = connection.cursor()

    message = request.GET["message"]
    datePost = request.GET["date"]
    email = request.GET["user"]
    idThread = request.GET["thread"]#что то с этим не так 
    forum = request.GET["forum"]#нужно будет с этим что то сделать

    isApproved = request.GET["isApproved"]
    if(isApproved=="true"):
        isApproved = True
    else: 
        isApproved = False

    isDeleted = request.GET["isDeleted"]
    if(isDeleted=="true"):
        isDeleted = True
    else: 
        isDeleted = False  

    isEdited = request.GET["isEdited"]
    if(isEdited=="true"):
        isEdited = True
    else: 
        isEdited = False

    isHighlighted = request.GET["isHighlighted"]
    if(isHighlighted=="true"):
        isHighlighted = True
    else: 
        isHighlighted = False

    isSpam = request.GET["isSpam"]
    if(isSpam=="true"):
        isSpam = True
    else:
        isSpam = False

    cursor.execute('''SELECT idUser
                      FROM User 
                      WHERE email = '%s'
                   ''' % (email,))
    idUser = cursor.fetchone()[0]

    #пока не вставляем parent = 'NULL'
    cursor.execute('''INSERT INTO Post(idThread,idUser,datePost,message,isEdited,isDeleted,isSpam,isHighlighted,isApproved) 
                      VALUES          ( '%s',    '%s',  '%s'    ,'%s'   ,'%d'      ,'%d'   ,'%d'   ,'%d',          '%d');
                   ''' % (idThread,idUser,datePost,message,
                    isEdited,isDeleted,
                    isSpam,
                    isHighlighted,
                    isApproved

                    ,)) 

    requestCopy = request.GET.copy()
    requestCopy.__setitem__('id',idUser)#setdefault()
    requestCopy.__setitem__('parent','null')#setdefault()
    code = 0
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")