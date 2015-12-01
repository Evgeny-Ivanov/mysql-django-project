#User
DROP INDEX follower_user ON Followers;
DROP INDEX name_idUser ON User;
DROP INDEX user_datePost ON Post;

#Post
DROP INDEX level_parent ON Post;
DROP INDEX forum_datePost ON Post;
DROP INDEX idThread_datePost ON Post;

#Thread
DROP INDEX forum_dateThread ON Thread;
DROP INDEX user_dateThread ON Thread;

#Forum
DROP INDEX forum_user ON Post;