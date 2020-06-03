#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, Response
from steamer.database.db import initialize_db, Game, Genre, Tag, GameDetail, TfidfGame, NumberVote, update_tfidf
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
    genres = [genre for genre in Genre.objects() if genre.count > 1]
    genres = sorted(genres, key=lambda genre: genre.name)
    tags = [tag for tag in Tag.objects() if tag.count > 1]
    tags = sorted(tags, key=lambda tag: tag.name)
    game_details = [game_detail for game_detail in GameDetail.objects() if game_detail.count > 1]
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


@app.route('/results', methods=['POST'])
def results():
    error = None
    if request.method == 'POST':

        total_games = len(Game.objects())

        print("Parse request")
        genres = request.form.getlist('Genres[]')
        tags = request.form.getlist('Tags[]')
        game_details = request.form.getlist('GameDetails[]')
        filter_price = request.form.getlist('filter_price')[0].split(',')
        filter_reviews = request.form.get('filter_reviews')

        print("Generate searching game")
        searching_game = SearchingGame()
        searching_game.genres = genres
        searching_game.popular_tags = tags
        searching_game.game_details = game_details

        print("Load user games")
        user_games = [get_game_details_by_id(user_game["appid"]) for user_game in
                      json.loads(get_games_by_user(76561197992131568))["response"]["games"]]
        user_games = [user_game for user_game in user_games if user_game is not None]

        if len(Game.objects()) != total_games:
            print("Update tfidf")
            update_tfidf()

        print("Filter games")
        games = Game.objects()
        games_filtred = []
        for game in games:
            if float(filter_price[0]) <= game.original_price <= float(filter_price[1]):
                percentage = json.loads(game["reviews"])["percentage"]
                if percentage != "":
                    if float(percentage) >= float(filter_reviews):
                        games_filtred.append(game)

        print("Calculate similarities")
        genres = Genre.objects()
        tags = Tag.objects()
        game_details = GameDetail.objects()
        tfidf_games = TfidfGame.objects()

        similarities = calculate_similarities(searching_game, user_games, games_filtred, genres, tags, game_details, tfidf_games)

        print("Sort prediction")
        similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)

        print("Return first result")
        prediction = [Game.objects().get(steam_id=similar[0]) for similar in similarities]
        return render_template('results.html', games=prediction[:10])
    # the code below is executed if the request method
    # was GET or the credentials were invalid


@app.route('/users/<steam_id>/games')
def get_user(steam_id):
    user = get_games_by_user(steam_id)

    return Response(user, mimetype="application/json", status=200)


@app.route('/game/<game_id>')
def get_game_by_id(game_id):
    r = get_game_details_by_id(game_id)

    return Response(r, mimetype="application/json", status=200)