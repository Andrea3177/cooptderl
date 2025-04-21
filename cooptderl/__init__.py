from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager
from datetime import timedelta



db = SQLAlchemy()

from flask import Flask
app = Flask(__name__)
engine = create_engine('mysql+pymysql://root:Mandarina#33@localhost/cooptderl')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Mandarina#33@localhost/cooptderl'
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'supersecretkey' 
app.testing = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

db.init_app(app)
Session = sessionmaker(bind=engine)
ses = Session()


login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login' 


import cooptderl.views
