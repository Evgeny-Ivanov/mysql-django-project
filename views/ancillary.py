# -*- coding: utf-8 -*-
from django.http import HttpResponse,HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.db import connection
import json

def status(request):
    cursor = connection.cursor()

    cursor.execute('''SELECT COUNT(*)
    	              FROM User
                   ''')
    countUser = cursor.fetchone()[0]

    cursor.execute('''SELECT COUNT(*)
    	              FROM Thread
                   ''')
    countThread = cursor.fetchone()[0]

    cursor.execute('''SELECT COUNT(*)
    	              FROM Post
                   ''')
    countPost = cursor.fetchone()[0]

    cursor.execute('''SELECT COUNT(*)
    	              FROM Forum
    	           ''')
    countForum = cursor.fetchone()[0]

    code = 0
    responce = { "code": code, "response": {"user": countUser, 
                                            "thread": countThread, 
                                            "forum": countForum, 
                                            "post": countPost}}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


def clear(request):
    cursor = connection.cursor()

    #нужно будет еще добавить таблицу лайков
    cursor.execute('''DELETE FROM Post
                   ''')

    cursor.execute('''DELETE FROM Subscriptions
                   ''')

    cursor.execute('''DELETE FROM Thread
                   ''')

    cursor.execute('''DELETE FROM Forum
                   ''')

    cursor.execute('''DELETE FROM Followers
                   ''')

    cursor.execute('''DELETE FROM User
    	           ''')

    code = 0
    responce = { "code": code, "response": "OK"}
    responce = json.dumps(responce)
    return HttpResponse(responce,content_type="application/json")


def hello(request):
    cursor = connection.cursor() #Для использования подключения к базе данных
    
    #cursor.execute("CREATE TABLE buf (name VARCHAR(10) PRIMARY KEY)")
    #cursor.execute("INSERT INTO buf VALUES ('Evgeny')")
    username = request.GET["username"]
    query = '''SELECT username
               FROM User
               WHERE username = '%s';
            ''' % username

    cursor.execute(query) #для выполнения SQL
    #cursor.execute("DROP TABLE buf")
    #row = cursor.fetchone() #для получения результата
    row = cursor.fetchall()
    #row = json.dumps(row)

    code = 0
    responce = { "code": code, "response": row }
    responce = json.dumps(responce)

    #if request.method == 'POST':
    #    return request.body  

    return HttpResponse(responce,content_type="application/json")

def createdb(request):
    createUser()
    createForum()
    createThread()
    createPost()
    return HttpResponse("OK")


def createForum():
    cursor = connection.cursor() 
    query = '''CREATE TABLE Forum (forumId INT PRIMARY KEY AUTO_INCREMENT,
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
    query = '''CREATE TABLE User  (userId INT PRIMARY KEY AUTO_INCREMENT,
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


def dropdb(request):
    dropPost()
    dropThread()
    dropForum()
    dropUser()
    return HttpResponse("OK")

def dropUser():
    cursor = connection.cursor() 
    query = '''DROP TABLE User;
            '''
    cursor.execute(query)
    row = cursor.fetchall()

def dropForum():
    cursor = connection.cursor() 
    query = '''DROP TABLE Forum;
            '''
    cursor.execute(query)
    row = cursor.fetchall()

def dropThread():
    cursor = connection.cursor() 
    query = '''DROP TABLE Thread;
            '''
    cursor.execute(query)
    row = cursor.fetchall()

def dropPost():
    cursor = connection.cursor() 
    query = '''DROP TABLE Post;
            '''
    cursor.execute(query)
    row = cursor.fetchall()


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]



def getBollean(variable):
    if(variable=="true" or variable==1 or variable=='1'):
        return True
    else: 
        return False