from flask_restful import Resource,fields,marshal_with,reqparse
from models import db,User,Post
from validation import NotFoundError,BusinessValidationError

user_output_fields={"user_id":fields.Integer,"username":fields.String}
post_output_fields={"post_id":fields.Integer,"title":fields.String,"user_id":fields.Integer,"timestamp":fields.String}

create_user_parser=reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('password')

update_user_parser=reqparse.RequestParser()
update_user_parser.add_argument('password')

create_post_parser=reqparse.RequestParser()
create_post_parser.add_argument('title')
create_post_parser.add_argument('content')
create_post_parser.add_argument('image')
create_post_parser.add_argument('user_id')

update_post_parser=reqparse.RequestParser()
update_post_parser.add_argument('title')
update_post_parser.add_argument('image')

class UserAPI(Resource):
  @marshal_with(user_output_fields)
  def get(self,username):
    user=User.query.filter_by(username=username).first()
    if user!=None:
      return (user,200)
    else:
      raise NotFoundError(status_code=404)
  
  @marshal_with(user_output_fields)
  def post(self):
    args=create_user_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    
    if username is None or username=='':
      raise BusinessValidationError(status_code=400,error_code='U101',error_message='username is required')
    if password is None or password=='':
      raise BusinessValidationError(status_code=400,error_code='U102',error_message='password is required')
    if (len(User.query.filter_by(username=username).all())>0):
      raise BusinessValidationError(status_code=400,error_code='U103',error_message='Duplicate user')

    db.session.execute('PRAGMA foreign_keys=ON')
    user=User(username=username,password=password)
    db.session.add(user)
    db.session.commit()
    return (user,201)

  @marshal_with(user_output_fields)
  def put(self,username):
    args=update_user_parser.parse_args()
    password=args.get('password',None)
    user=User.query.filter_by(username=username).first()
    if user is None:
      raise NotFoundError(status_code=404)
    
    if password is None or password=='':
      raise BusinessValidationError(status_code=400,error_code='U102',error_message='password is required')
    
    user.password=password
    db.session.add(user)
    db.session.commit()
    return (user,200)

  def delete(self,username):
    user=User.query.filter_by(username=username).first()
    if user is None:
      raise NotFoundError(status_code=404)
    posts=Post.query.filter_by(user_id=user.user_id).count()
    if posts>0:
      raise BusinessValidationError(status_code=400,error_code='U104',error_message='Can\'t delete user as user has posted blog(s)')

    db.session.execute('PRAGMA foreign_keys=ON')
    db.session.delete(user)
    db.session.commit()
    return ('',200)  

class PostAPI(Resource):
  @marshal_with(post_output_fields)
  def get(self,post_id):
    post=Post.query.filter_by(post_id=post_id).first()
    if post!=None:
      return (post,200)
    else:
      raise NotFoundError(status_code=404)

  @marshal_with(post_output_fields)
  def post(self):
    args=create_post_parser.parse_args()
    title=args.get('title',None)
    content=args.get('content',None)
    image=args.get('image',None)
    user_id=args.get('user_id',None)
    
    if title is None or title=='':
      raise BusinessValidationError(status_code=400,error_code='P101',error_message='title is required')
    if content is None or content=='':
      raise BusinessValidationError(status_code=400,error_code='P102',error_message='content is required')
    if user_id is None:
      raise BusinessValidationError(status_code=400,error_code='P103',error_message='user_id is required')
    
    user=User.query.filter_by(user_id=user_id).first()
    if user is None:
      raise NotFoundError(status_code=404)

    db.session.execute('PRAGMA foreign_keys=ON')
    post=Post(title=title,content=content,image=image,user_id=user_id)
    db.session.add(post)
    db.session.commit()
    return (post,201)

  @marshal_with(post_output_fields)
  def put(self,post_id):
    args=update_post_parser.parse_args()
    title=args.get('title',None)
    image=args.get('image',None)

    post=Post.query.filter_by(post_id=post_id).first()
    if post is None:
      raise NotFoundError(status_code=404)

    if title is None or title=='':
      raise BusinessValidationError(status_code=400,error_code='P101',error_message='title is required')

    post.title=title
    if image!=None:
      post.image=image
    db.session.add(post)
    db.session.commit()
    return (post,200)


  def delete(self,post_id):
    post=Post.query.filter_by(post_id=post_id).first()
    if post is None:
      raise NotFoundError(status_code=404)
    
    db.session.execute('PRAGMA foreign_keys=ON')
    db.session.delete(post)
    db.session.commit()
    return ('',200)