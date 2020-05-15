#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, Response
from steamer.database.db import initialize_db, Game, Genre, Tag, GameDetail, Developer
from steamer.steam.game import get_game_details_by_id
from steamer.steam.user import get_games_by_user

app = Flask(__name__, static_url_path='', static_folder='web/static', template_folder='web/templates')
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/steamer'
}
initialize_db(app)


@app.route('/t')
def index():
    genres = Genre.objects()
    tags = Tag.objects()
    game_details = GameDetail.objects()
    developers = Developer.objects()
    return render_template('index.html', genres=genres, tags=tags, game_details=game_details, developers=developers)


@app.route('/games')
def get_games():
    games = Game.objects().to_json()

    return Response(games, mimetype="application/json", status=200)


@app.route('/games/<name>')
def get_game(name):
    game = [game for game in Game.objects() if game.id == name]

    return Response(game, mimetype="application/json", status=200)


@app.route('/results', methods=['POST'])
def results():
    error = None
    if request.method == 'POST':
        return render_template('results.html')
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('index.html', name=error)


@app.route('/users/<steam_id>/games')
def get_user(steam_id):
    user = get_games_by_user(steam_id)

    return Response(user, mimetype="application/json", status=200)


@app.route('/game/<game_id>')
def get_game_by_id(game_id):
    r = get_game_details_by_id(game_id)

    return Response(r, mimetype="application/json", status=200)
