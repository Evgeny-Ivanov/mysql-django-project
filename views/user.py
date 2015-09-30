# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.db import connection
import json


def insertUser(request):

    username = request.GET["username"]
    about = request.GET["about"]
    isAnonymous = request.GET["isAnonymous"]
    if(isAnonymous=="true"):
        isAnonymous = True
    else: 
        isAnonymous = False
    name = request.GET["name"]
    email = request.GET["email"]

    query = '''INSERT INTO User(username,about,name,email,isAnonymous) 
               VALUES ('%s','%s','%s','%s','%d');
            ''' % (username,about,name,email,isAnonymous,)

    cursor = connection.cursor()
    id1 = '''SELECT userId 
            FROM User 
            WHERE email = '%s'
         ''' % (email,)

    cursor.execute(query)
    #row = cursor.fetchall()

    row = request.GET#нужно еще возвращать id 
    row = row['id'].append(id1)
    code = 0
    responce = { "code": code, "response": row }
    responce = json.dumps(responce)

    return HttpResponse(responce,content_type="application/json")

