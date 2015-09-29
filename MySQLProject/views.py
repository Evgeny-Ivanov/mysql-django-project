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


def createdb(request):
	createUser()
	createForum()
	createThread()
	createPost()
	return HttpResponse("OK")


def createForum():
    cursor = connection.cursor() 
    query = '''CREATE TABLE Forum (forumId INT PRIMARY KEY,
    	                           name VARCHAR(50) ,
    	                           shortName VARCHAR(20),
    	                           userId INT ,/*email*/
    	                           UNIQUE (name),
    	                           UNIQUE (shortName),
    	                           FOREIGN KEY (userId) REFERENCES User(userId)
    	                           );
            '''

    cursor.execute(query)
    row = cursor.fetchall()


def createPost():
    cursor = connection.cursor() 
    query = '''CREATE TABLE Post  (postId INT PRIMARY KEY,
    	                           threadId INT,
    	                           userId INT,
    	                           parent INT,
    	                           datePost DATE,
    	                           message TEXT,
    	                           isEdited BOOLEAN,
    	                           isDeleted BOOLEAN,
    	                           isSpam BOOLEAN,
    	                           isHighlighted BOOLEAN,
    	                           isApproved BOOLEAN,
    	                           FOREIGN KEY (userId) REFERENCES User(userId),
    	                           FOREIGN KEY (threadId) REFERENCES Thread(threadId)
    	                           );
            '''

    cursor.execute(query)
    row = cursor.fetchall()

def createUser():
    cursor = connection.cursor() 
    query = '''CREATE TABLE User  (userId INT PRIMARY KEY,
    	                           username VARCHAR(50),
    	                           about VARCHAR(100),
    	                           name VARCHAR(50),
    	                           email VARCHAR(50),
    	                           isAnonymous BOOLEAN,
    	                           UNIQUE (email)
    	                           );
            '''

    cursor.execute(query)
    row = cursor.fetchall()


def createThread():
    cursor = connection.cursor() 
    query = '''CREATE TABLE Thread (threadId INT PRIMARY KEY,
    	                            forumId INT,
    	                            userId INT,
    	                            title VARCHAR(50),
    	                            slug VARCHAR(50),
    	                            message TEXT,
    	                            dateThread DATE,
    	                            isClosed BOOLEAN,
    	                            isDeleted BOOLEAN,
    	                            FOREIGN KEY (userId) REFERENCES User(userId),
    	                            FOREIGN KEY (forumId) REFERENCES Forum(forumId)
    	                           );
            '''

    cursor.execute(query)
    row = cursor.fetchall()





