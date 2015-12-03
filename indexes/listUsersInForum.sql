LE
#listUsersInForum
SELECT DISTINCT User.email,User.about,User.idUser AS id,User.isAnonymous,User.name,User.username
FROM User JOIN Post
        ON User.email = Post.user
WHERE Post.forum = 'uke8'
ORDER BY User.name desc  LIMIT 25;
#User(name) - ICP Post(forum,user) - для JOIN 

SELECT User.email,User.about,User.idUser AS id,User.isAnonymous,User.name,User.username
FROM User JOIN Post
        ON User.email = Post.user
WHERE Post.forum = 'uke8'
GROUP BY idUser
ORDER BY User.name desc  LIMIT 25;
#User(name) - ICP Post(forum,user) - для JOIN 






