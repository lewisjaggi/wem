#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, Response
from database.db import initialize_db, Game, Genre, Tag, GameDetail, Developer

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/steamer'
}
initialize_db(app)


@app.route('/')
def index():
    genres = Genre.objects()
    tags = Tag.objects()
    game_details = GameDetail.objects()
    developers = Developer.objects()
    return render_template('index.html', genres=genres, tags=tags, game_details = game_details, developers= developers)


@app.route('/games')
def get_games():
    games = Game.objects().to_json()

    return Response(games, mimetype="application/json", status=200)


@app.route('/games/<name>')
def get_game(name):
    game = [game for game in Game.objects() if game.name == name][0].to_json()

    return Response(game, mimetype="application/json", status=200)


@app.route('/results', methods=['POST'])
def results():
    error = None
    if request.method == 'POST':
        return render_template('results.html')
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('index.html', name=error)
