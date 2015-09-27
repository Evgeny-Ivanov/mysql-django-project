# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.db import connection
import json


def hello(request):
    cursor = connection.cursor() #Для использования подключения к базе данных
    
    #cursor.execute("CREATE TABLE buf (name VARCHAR(10) PRIMARY KEY)")
    #cursor.execute("INSERT INTO buf VALUES ('Evgeny')")
    cursor.execute("SELECT * FROM buf") #для выполнения SQL
    #cursor.execute("DROP TABLE buf")
    #row = cursor.fetchone() #для получения результата
    row = cursor.fetchall()
    #row = json.dumps(row)

    code = 0
    responce = { "code": code, "response": row }
    responce = json.dumps(responce)

    if request.method == 'POST':
        return request.body  

    return HttpResponse(responce,content_type="application/json")

def createForum():
    cursor = connection.cursor() 
    query = '''CREATE TABLE forum (id INT(5) PRIMARY KEY,
    	                           name VARCHAR(50) ,
    	                           short_name VARCHAR(20),
    	                           user VARCHAR(50),/*email*/
    	                           UNIQUE (name),
    	                           UNIQUE (short_name)
    	                           );
            '''

    cursor.execute(query)
    row = cursor.fetchall()

    return 

def createPost():
    cursor = connection.cursor() 
    query = '''CREATE TABLE post  (id INT(5) PRIMARY KEY,
    	                           date VARCHAR(50) ,
    	                           thread INT(5),/*id*/
    	                           message TEXT,
    	                           user VARCHAR(50),/*email*/
    	                           forum VARCHAR(20),/*short_name*/
    	                           parent INT(5),
    	                           isApproved
    	                           UNIQUE (name)
    	                           );
            '''

    cursor.execute(query)
    row = cursor.fetchall()

