#User
CREATE INDEX follower_user ON Followers(follower,user);
CREATE INDEX name_idUser ON User(name,idUser);
CREATE INDEX user_datePost ON Post(user,datePost);

#Post
CREATE INDEX level_parent ON Post(level,parent);
CREATE INDEX forum_datePost ON Post(forum,datePost);
CREATE INDEX idThread_datePost ON Post(idThread,datePost);

#Thread
CREATE INDEX forum_dateThread ON Thread(forum,dateThread);
CREATE INDEX user_dateThread ON Thread(user,dateThread);

#Forum
CREATE INDEX forum_user ON Post(forum,user);
