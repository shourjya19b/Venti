from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User(db.Model):
  user_id=db.Column(db.Integer,primary_key=True)
  username=db.Column(db.String(50),unique=True,nullable=False)
  password=db.Column(db.String(50),nullable=False)
  profile_image=db.Column(db.String(200))

class Post(db.Model):
  post_id=db.Column(db.Integer,primary_key=True)
  title=db.Column(db.String(50),nullable=False)
  content=db.Column(db.Text,nullable=False)
  image=db.Column(db.String(200),default='/static/default-profile-picture.png')
  user_id=db.Column(db.Integer,db.ForeignKey('user.user_id',ondelete='CASCADE'))
  timestamp=db.Column(db.DateTime,server_default=db.func.now())

class Follow(db.Model):
  user_id=db.Column(db.Integer,db.ForeignKey('user.user_id',ondelete='CASCADE'),primary_key=True)
  follower_id=db.Column(db.Integer,db.ForeignKey('user.user_id',ondelete='CASCADE'),primary_key=True)

class Like(db.Model):
  post_id=db.Column(db.Integer,db.ForeignKey('post.post_id',ondelete='CASCADE'),primary_key=True)
  user_id=db.Column(db.Integer,db.ForeignKey('user.user_id',ondelete='CASCADE'),primary_key=True)

class Comment(db.Model):
  post_id=db.Column(db.Integer,db.ForeignKey('post.post_id',ondelete='CASCADE'),primary_key=True)
  user_id=db.Column(db.Integer,db.ForeignKey('user.user_id',ondelete='CASCADE'),primary_key=True)
  comment_text=db.Column(db.Text,nullable=False)
