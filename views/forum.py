# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.db import connection
import json


def insertForum(request):#?name=Forum With Sufficiently Large Name3&short_name=forumwithsufficientlylargename3&user=example3@mail.ru
    cursor = connection.cursor()

    name = request.GET["name"]
    shortName = request.GET["short_name"]
    email = request.GET["user"]#user = email

    cursor.execute('''SELECT idUser
                      FROM User
                      WHERE email = '%s';
                   ''' % (email,))
    idUser = cursor.fetchone()[0]

    cursor.execute('''INSERT INTO Forum(name,shortName,idUser) 
                      VALUES ('%s','%s','%s');
                   ''' % (name,shortName,idUser,))

    cursor.execute('''SELECT idForum
                      FROM Forum
                      WHERE name = '%s';
                   ''' % (name,))
    idForum = cursor.fetchone()[0]

    requestCopy = request.GET.copy()
    requestCopy.__setitem__('id',idForum)
    code = 0
    responce = { "code": code, "response": requestCopy }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")