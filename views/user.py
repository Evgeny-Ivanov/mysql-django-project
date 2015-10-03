# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json


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
