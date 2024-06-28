import os
from flask import Flask
from flask_restful import Resource,Api
from models import db

app=Flask(__name__)

current_dir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(current_dir,'blogdb.sqlite3')

upload_folder='static/'
app.config['UPLOAD_FOLDER']=upload_folder

db.init_app(app)
api=Api(app)
app.app_context().push()

with app.app_context():
  db.create_all()

from controllers import *
from api import UserAPI,PostAPI

api.add_resource(UserAPI,'/api/user','/api/user/<string:username>')
api.add_resource(PostAPI,'/api/post','/api/post/<int:post_id>')

if __name__=='__main__':
  app.run(debug=True)