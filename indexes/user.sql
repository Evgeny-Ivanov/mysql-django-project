CREATE INDEX user_datePost ON Post (user,datePost);#в listPostsUser идеальный индекс

CREATE INDEX name_idUser ON User (name,idUser);#(ICP)

#CREATE INDEX email_idUser ON User (email,idUser);#получить id по email - покрывающий #только в isertUser

CREATE INDEX follower_user ON Followers (follower,user);#join + как покрывающий #обратный индекс - primary
