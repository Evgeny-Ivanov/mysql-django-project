ALTER TABLE Forum ADD posts INT;

UPDATE Forum
SET posts = (SELECT COUNT(*) 
	         FROM Post 
	         WHERE forum = Forum.short_name
	         );

UPDATE Thread
SET posts = (SELECT COUNT(*) 
	         FROM Post 
	         WHERE Post.idThread = Thread.idThread
	         );