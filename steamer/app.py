#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, Response
from steamer.database.db import initialize_db, Game, Genre, Tag, GameDetail, TfidfGame, NumberVote
from steamer.steam.game import get_game_details_by_id
from steamer.steam.user import get_games_by_user
from steamer.recommendation.similarity import calculate_similarities, calculate_score
from steamer.recommendation.searchinggame import SearchingGame
import json

app = Flask(__name__, static_url_path='', static_folder='web/static', template_folder='web/templates')
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/steamer'
}
initialize_db(app)


@app.route('/')
def index():
    genres = Genre.objects()
    genres = sorted(genres, key=lambda genre: genre.name)
    tags = Tag.objects()
    tags = sorted(tags, key=lambda tag: tag.name)
    game_details = GameDetail.objects()
    game_details = sorted(game_details, key=lambda game_detail: game_detail.name)
    return render_template('index.html', genres=genres, tags=tags, game_details=game_details)


@app.route('/games')
def get_games():
    games = Game.objects().to_json()

    return Response(games, mimetype="application/json", status=200)


@app.route('/games/<name>')
def get_game(name):
    game = [game for game in Game.objects() if game.id == name]

    return Response(game, mimetype="application/json", status=200)


@app.route('/results', methods=['GET'])
def results():
    error = None
    if request.method == 'POST':

        genres = request.form.getlist('Genres[]')
        tags = request.form.getlist('Tags[]')
        game_details = request.form.getlist('GameDetails[]')
        #algo

        searching_game = SearchingGame()
        searching_game.genres = genres
        searching_game.popular_tags = tags
        searching_game.game_details = game_details

        games = Game.objects()
        total_games = len(games)
        genres = Genre.objects()
        tags = Tag.objects()
        game_details = GameDetail.objects()
        tfidf_games = TfidfGame.objects()
        numberVote = NumberVote.objects()[0]

        similarities = calculate_similarities(searching_game, games, genres, tags, game_details, tfidf_games)

        similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)

        for similar in similarities:
            print(similar)
            print(type(similar))
            print(similar[0])
            print(type(similar[0]))
        prediction = [Game.objects().get(steam_id=similar[0]).name for similar in similarities]
        return json.dumps(prediction)
        return render_template('results.html')
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('index.html')
    game1 = get_game_details_by_id(637090)
    game2 = get_game_details_by_id(221100)
    game3 = get_game_details_by_id(8500)
    game4 = get_game_details_by_id(601150)
    game5 = get_game_details_by_id(477160)
    game6 = get_game_details_by_id(644930)
    return render_template('results.html', games=[game1,game2,game3,game4,game5,game6],name=error)


@app.route('/users/<steam_id>/games')
def get_user(steam_id):
    user = get_games_by_user(steam_id)

    return Response(user, mimetype="application/json", status=200)


@app.route('/game/<game_id>')
def get_game_by_id(game_id):
    r = get_game_details_by_id(game_id)

    return Response(r, mimetype="application/json", status=200)
