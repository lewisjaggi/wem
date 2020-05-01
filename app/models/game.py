from flask import Flask
from flask.ext.mongoalchemy import MongoAlchemy

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'library'
db = MongoAlchemy(app)

class Game(db.Document):
    id
    name = bd.StringField()
    type
    url
    tags
    languages

class