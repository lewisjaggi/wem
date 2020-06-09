#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, Response
from steamer.database.db import initialize_db, Game, Genre, Tag, GameDetail, TfidfGame, NumberVote, update_tfidf, \
    Language
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
    genres = Genre.objects().order_by('name')
    tags = Tag.objects().order_by('name')
    game_details = GameDetail.objects().order_by('name')
    languages = Language.objects().order_by('name')

    return render_template('index.html', genres=genres, tags=tags, game_details=game_details, languages=languages)


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

        total_games = Game.objects().count()

        print("Parse request")
        genres = request.form.getlist('Genres[]')
        tags = request.form.getlist('Tags[]')
        game_details = request.form.getlist('GameDetails[]')
        filter_price = request.form.getlist('filter_price')[0].split(',')
        filter_reviews = request.form.get('filter_reviews')
        filter_languages = request.form.getlist('filter_languages[]')
        steam_user_id = request.form.get('steamUserID').strip()

        if len(genres) > 0 or len(tags) > 0 or len(game_details) > 0:
            print("Generate searching game")
            searching_game = SearchingGame()
            searching_game.genres = json.dumps(dict((genre, [0]) for genre in genres))
            searching_game.popular_tags = json.dumps(dict((tag, [0]) for tag in tags))
            searching_game.game_details = json.dumps(dict((game_detail, [0]) for game_detail in game_details))

            user_games = []
            if steam_user_id != '':
                print("Load user games")
                user_games = [get_game_details_by_id(user_game["appid"]) for user_game in
                              json.loads(get_games_by_user(steam_user_id))["response"]["games"]]
                user_games = [user_game for user_game in user_games if user_game is not None]

                if Game.objects().count() != total_games:
                    print("Update tfidf")
                    update_tfidf()

            print("Filter games")
            games = Game.objects()
            games_filtred = []
            common_caracteristics_score = {}
            for game in games:
                if float(filter_price[0]) <= game.original_price <= float(filter_price[1]):
                    percentage = json.loads(game["reviews"])["percentage"]
                    if percentage != "":
                        if float(percentage) >= float(filter_reviews):
                            language_filtred = True
                            if len(filter_languages) != 0:
                                language_filtred = False
                                for language in filter_languages:
                                    if language in game.languages:
                                        language_filtred = True
                            if language_filtred:
                                common = 0
                                total_caracteriscics = 0
                                for name in json.loads(game.genres):
                                    total_caracteriscics += 1
                                    if name in genres:
                                        common += 1

                                for name in json.loads(game.popular_tags):
                                    total_caracteriscics += 1
                                    if name in tags:
                                        common += 1

                                for name in json.loads(game.game_details):
                                    total_caracteriscics += 1
                                    if name in game_details:
                                        common += 1

                                games_filtred.append(game)
                                common_caracteristics_score[game.steam_id] = 1 + common / total_caracteriscics

            print("Calculate similarities")
            genres = Genre.objects()
            tags = Tag.objects()
            game_details = GameDetail.objects()
            tfidf_games = TfidfGame.objects()

            similarities = calculate_similarities(searching_game, user_games, games_filtred, common_caracteristics_score, genres, tags, game_details,
                                                  tfidf_games)

            print("Sort prediction")
            similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)

            print("Return first results")
            prediction = [Game.objects().get(steam_id=similar[0]) for similar in similarities]
            return render_template('results.html', games=prediction[:10],
                               genres=dict((game.steam_id, [genre for genre, indexes in json.loads(game.genres).items() if len(indexes) > 0]) for game in prediction[:10])
                               )
        return render_template('results.html', games=[], genres=[])
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
