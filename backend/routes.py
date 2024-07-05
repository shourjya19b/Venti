from flask import render_template,redirect,url_for,request
from flask import current_app as app
from models import db,User,Post,Follow,Like,Comment
from werkzeug.utils import secure_filename
import os
  
@app.route('/login',methods=['GET','POST'])
def login():
  if request.method=='GET':
    return render_template('index.html',title='Login')
  elif request.method=='POST':
    username=request.form['username']
    password=request.form['password']
    
    user=User.query.filter_by(username=username).first()
    if username!='':
      if password!='':
        if user!=None:
          if user.password==password:
            return redirect('feed/'+str(user.user_id))
          else:
            return render_template('login_error.html',title='Login Error',message='Password Incorrect')
        else:
          return render_template('login_error.html',title='Login Error',message='User not found')
      else:
        return render_template('login_error.html',title='Login Error',message='Password must be provided')
    else:
      return render_template('login_error.html',title='Login Error',message='Username must be provided')

@app.route('/register',methods=['GET','POST'])
def register():
  if request.method=='GET':
    return render_template('register.html',title='Register')
  elif request.method=='POST':
    db.session.execute('PRAGMA foreign_keys=ON')
    
    username=request.form['username']
    password=request.form['password']
    
    if username=='':
      return render_template('registration_error.html',title='Registration Error',message='Username must be provided')
    
    if password=='':
      return render_template('registration_error.html',title='Registration Error',message='Password must be provided')

    user=User.query.filter_by(username=username).first()
    if user==None:
      new_user=User(username=username,password=password)
      db.session.add(new_user)
      db.session.commit()
      return redirect('/login')
    else:
      return render_template('registration_error.html',title='Registration Error',message='Username already exists')

@app.route('/feed/<int:user_id>',methods=['GET'])
def feed(user_id):
  user=User.query.filter_by(user_id=user_id).first()
  
  if request.method=='GET':
    followed_ids=[]
    followed=Follow.query.filter_by(follower_id=user_id).all()
    for follow in followed:
      followed_ids.append(follow.user_id)
    
    n_likes=[]
    poster_ids=[]
    n_comments=[]
    posts=Post.query.filter(Post.user_id.in_(followed_ids)).order_by(Post.timestamp)
    
    n_posts=posts.count()
    if n_posts==0:
      message='You have no posts in your feed'
    else:
      message=None
    
    for post in posts:
      poster_ids.append(post.user_id)
      n_likes.append(Like.query.filter_by(post_id=post.post_id).count())
      n_comments.append(Comment.query.filter_by(post_id=post.post_id).count())
    
    posters=[]
    for poster_id in poster_ids:
      poster=User.query.filter_by(user_id=poster_id).first()
      posters.append((poster.username,poster.profile_image))
    return render_template('feed.html',title='Feed',posts=posts,posters=posters,user=user,n_posts=n_posts,n_likes=n_likes,n_comments=n_comments,message=message)
  
@app.route('/search/<int:user_id>',methods=['GET','POST'])
def search(user_id):
  user=User.query.filter_by(user_id=user_id).first()
  
  if request.method=='GET':
    return render_template('search.html',title='Search',user=user,searched_users=None)
  elif request.method=='POST':
    name=request.form['name']
    return redirect('/search/'+str(user_id)+'/'+name)

@app.route('/profile/<string:username>/<int:visitor_id>',methods=['GET'])
def profile(username,visitor_id):
  if request.method=='GET':
    user=User.query.filter_by(username=username).first()
    image=url_for('static',filename='/profile_pics/'+str(user.profile_image))
    visitor=User.query.filter_by(user_id=visitor_id).first()
    posts=Post.query.filter_by(user_id=user.user_id).all()
    n_fol=Follow.query.filter_by(follower_id=user.user_id).count()
    n_fol_by=Follow.query.filter_by(user_id=user.user_id).count()
    n_posts=len(posts)
    return render_template('profile.html',title='Profile',user=user,image=image,visitor=visitor,posts=posts,n_posts=n_posts,n_fol=n_fol,n_fol_by=n_fol_by)

@app.route('/update_profile/<int:user_id>',methods=['GET','POST'])
def update_profile(user_id):
  user=User.query.filter_by(user_id=user_id).first()
  
  if request.method=='GET':
    return render_template('update_profile.html',title='Update',user=user)
  elif request.method=='POST':
    image=request.files['image']
    if image.filename!=None and image.filename!='':
      image_file=secure_filename(image.filename)
      image.save(os.path.join(app.config['UPLOAD_FOLDER'],'profile_pics/'+image_file))
      user.profile_image=image_file
      db.session.add(user)
      db.session.commit()
    return redirect('/profile/'+user.username+'/'+str(user.user_id))

@app.route('/search/<int:user_id>/<string:key>',methods=['GET','POST'])
def search_with_key(user_id,key):
  user=User.query.filter_by(user_id=user_id).first()
  query="%"+key+"%"
  
  searched_users=User.query.filter(User.username.like(query)).all()
  searched_user_ids=[]
  for searched_user in searched_users:
    searched_user_ids.append(searched_user.user_id)
  
  followed_users=Follow.query.filter(Follow.follower_id==user.user_id,Follow.user_id.in_(searched_user_ids)).all()
  followed_user_ids=[]
  for followed_user in followed_users:
    followed_user_ids.append(followed_user.user_id)
  
  if request.method=='GET':
    return render_template('search.html',title='Follow',searched_users=searched_users,user=user,key=key,followed=followed_user_ids)
  elif request.method=='POST':
    db.session.execute('PRAGMA foreign_keys=ON')
    
    follow_checked=list(map(int,request.form.getlist('Follow_Users')))
    for searched_user_id in searched_user_ids:
      if (searched_user_id in follow_checked) and (searched_user_id not in followed_user_ids):
        follow_add=Follow(user_id=searched_user_id,follower_id=user.user_id)
        db.session.add(follow_add)
        db.session.commit()
      if (searched_user_id not in follow_checked) and (searched_user_id in followed_user_ids):
        follow_delete=Follow.query.filter(Follow.follower_id==user.user_id,Follow.user_id==searched_user_id).first()
        db.session.delete(follow_delete)
        db.session.commit()
    
    return redirect('/feed/'+str(user.user_id))

@app.route('/create_post/<int:user_id>',methods=['GET','POST'])
def create_post(user_id):
  user=User.query.filter_by(user_id=user_id).first()
  
  if request.method=='GET':
    return render_template('create_post.html',title='Post',user=user)
  elif request.method=='POST':
    title=request.form['title']
    content=request.form['content']
    image=request.files['image']
    image_file=secure_filename(image.filename)
    
    if title=='':
      return render_template('post_error.html',title='Post Error',message='Title must be provided',user=user)
    if content=='':
      return render_template('post_error.html',title='Post Error',message='Post content/description must be provided',user=user)
    if image_file!=None and image_file!='':
      image.save(os.path.join(app.config['UPLOAD_FOLDER'],'post_pics/'+image_file))
    
    db.session.execute('PRAGMA foreign_keys=ON')
    new_post=Post(title=title,content=content,image=image_file,user_id=user.user_id)
    db.session.add(new_post)
    db.session.commit()
    
    return redirect('/feed/'+str(user.user_id))

@app.route('/view_post/<int:post_id>/<int:user_id>',methods=['GET','POST'])
def view_post(post_id,user_id):
  post=Post.query.filter_by(post_id=post_id).first()
  user=User.query.filter_by(user_id=user_id).first()
  poster=User.query.filter_by(user_id=post.user_id).first()
  
  liked=False
  like=Like.query.filter(Like.post_id==post_id,Like.user_id==user_id).count()
  if like!=0:
    liked=True
  n_likes=Like.query.filter_by(post_id=post_id).count()
  
  comments=Comment.query.filter_by(post_id=post_id).all()
  commenter_ids=[]
  for comment in comments:
    commenter_ids.append(comment.user_id)
  n_comments=len(commenter_ids)
  
  commenters=[]
  for commenter_id in commenter_ids:
    commenter=User.query.filter_by(user_id=commenter_id).first()
    commenters.append((commenter.username,commenter.profile_image))
  
  image=url_for('static',filename='/post_pics/'+str(post.image))
  
  if request.method=='GET':
    return render_template('view_post.html',title='View',post=post,poster=poster,user=user,image=image,commenters=commenters,comments=comments,n_likes=n_likes,n_comments=n_comments,liked=liked)
  elif request.method=='POST':
    db.session.execute('PRAGMA foreign_keys=ON')
    
    if (len(request.form.getlist('Like_Post'))==1) and (liked==False):
      add_like=Like(post_id=post.post_id,user_id=user.user_id)
      db.session.add(add_like)
      db.session.commit()
    elif (len(request.form.getlist('Like_Post'))==0) and (liked==True):
      remove_like=Like.query.filter(Like.post_id==post.post_id,Like.user_id==user.user_id).first()
      db.session.delete(remove_like)
      db.session.commit()
    
    comment_text=request.form['comment_text']
    if comment_text!='':
      comment=Comment(post_id=post_id,user_id=user_id,comment_text=comment_text)
      db.session.add(comment)
      db.session.commit()
    return redirect('/view_post/'+str(post_id)+'/'+str(user_id))

@app.route('/edit_post/<int:post_id>',methods=['GET','POST'])
def edit_post(post_id):
  post=Post.query.filter_by(post_id=post_id).first()
  user=User.query.filter_by(user_id=post.user_id).first()
  
  if request.method=='GET':
    return render_template('edit_post.html',title='Edit',post=post,user=user)
  elif request.method=='POST':
    title=request.form['title']
    content=request.form['content']
    image=request.files['image']
    image_file=secure_filename(image.filename)
    
    if title=='':
      return render_template('post_error.html',title='Post Error',message='Title must be provided',user=user)
    if content=='':
      return render_template('post_error.html',title='Post Error',message='Post content/description must be provided',user=user)
    if image_file!=None and image_file!='':
      image.save(os.path.join(app.config['UPLOAD_FOLDER'],'post_pics/'+image_file))
    
    post.title=title
    post.content=content
    post.image=image_file
    
    db.session.add(post)
    db.session.commit()
    return redirect('/profile/'+user.username+'/'+str(user.user_id))

@app.route('/delete_post/<int:post_id>',methods=['GET','POST'])
def delete_post(post_id):
  post=Post.query.filter_by(post_id=post_id).first()
  user=User.query.filter_by(user_id=post.user_id).first()
  if request.method=='GET':
    message='Are you sure you want to remove this blog?'
    return render_template('delete_post.html',title='Delete',message=message,post_id=post_id)
  
  elif request.method=='POST':  
    option=request.form['options']
    if option=='1':
      db.session.execute('PRAGMA foreign_keys=ON')
      db.session.delete(post)
      db.session.commit()
    return redirect('/profile/'+user.username+'/'+str(user.user_id))

@app.route('/delete_user/<int:user_id>',methods=['GET','POST'])
def delete_user(user_id):
  user=User.query.filter_by(user_id=user_id).first()
  if request.method=='GET':
    message='Are you sure you want to remove your profile?'
    return render_template('delete_user.html',title='Delete',message=message,user_id=user_id)
  
  elif request.method=='POST':  
    option=request.form['options']
    if option=='1':
      db.session.execute('PRAGMA foreign_keys=ON')
      db.session.delete(user)
      db.session.commit()
      return redirect('/login')
    else:
      return redirect('/profile/'+user.username+'/'+str(user.user_id))
