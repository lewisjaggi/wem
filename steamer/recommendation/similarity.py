#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import json
import re
from steamer.steam.user import get_friends_by_user, get_games_by_user
import multiprocessing
import scipy.stats as st
import time


def calculate_score(game, numberVote):
    reviews = json.loads(game.reviews)
    score = float(reviews["percentage"]) / 100 if reviews["percentage"] != '' else 0
    count = reviews["count"].replace(',', '')
    current_vote = float(count) - numberVote.min if bool(re.search(r'\d', count)) else 0
    max_vote = numberVote.max - numberVote.min

    vote_ratio = current_vote / float(max_vote)

    return score * vote_ratio


def calculate_tfidf(game, total_games, genres, tags, game_details):
    game_tfidf = []
    game_genres = json.loads(game.genres)
    total_game_genres = 0
    for name, indexes in game_genres.items():
        total_game_genres += len(indexes)

    for genre in genres.order_by('name'):
        tfidf = 1.0
        if genre.count > 0 and genre.name in game_genres:
            indexes = game_genres[genre.name]
            count = len(indexes)

            ranking = 0.0
            for index in indexes:
                ranking += 1 - index / total_game_genres

            tfidf += count * np.log(total_games / genre.count) * ranking
        game_tfidf.append(tfidf)

    game_tags = json.loads(game.popular_tags)
    total_game_tags = 0
    for name, indexes in game_tags.items():
        total_game_tags += len(indexes)

    for tag in tags.order_by('name'):
        tfidf = 1.0
        if tag.count > 0 and tag.name in game_tags:
            indexes = game_tags[tag.name]
            count = len(indexes)

            ranking = 0.0
            for index in indexes:
                ranking += 1 - index / total_game_tags

            tfidf += count * np.log(total_games / tag.count) * ranking
        game_tfidf.append(tfidf)

    game_game_details = json.loads(game.game_details)
    total_game_game_details = 0
    for name, indexes in game_game_details.items():
        total_game_game_details += len(indexes)

    for game_detail in game_details.order_by('name'):
        tfidf = 1.0
        if game_detail.count > 0 and game_detail.name in game_game_details:
            indexes = game_game_details[game_detail.name]
            count = len(indexes)

            ranking = 0.0
            for index in indexes:
                ranking += 1 - index / total_game_game_details

            tfidf += count * np.log(total_games / game_detail.count) * ranking
        game_tfidf.append(tfidf)

    return np.asarray(game_tfidf)
def init_process(games, tfidf_current_game, library_tfidf, pearson_friends, common_caracteristics_score):
    global games_process, tfidf_current_game_process, pearson_friends_process, common_caracteristics_score_process, library_tfidf_process
    games_process = games
    tfidf_current_game_process = tfidf_current_game
    pearson_friends_process = pearson_friends
    common_caracteristics_score_process = common_caracteristics_score
    library_tfidf_process = library_tfidf


def loop_tfidf(tfidf_game):
    game = [game for game in games_process if game['steam_id'] == tfidf_game['steam_id']]
    if len(game) > 0:
        tfidf = np.asarray(tfidf_game['tfidf'])

        cosinus_similarity = np.dot(tfidf, tfidf_current_game_process) / (
                np.sqrt(np.dot(tfidf, tfidf)) * (np.sqrt(np.dot(tfidf_current_game_process, tfidf_current_game_process))))

        library_score = 1
        if len(library_tfidf_process) == len(tfidf):
            library_score = np.dot(tfidf, library_tfidf_process) / (
                    np.sqrt(np.dot(tfidf, tfidf)) * (np.sqrt(np.dot(library_tfidf_process, library_tfidf_process))))

        score_friends = 1
        if len(pearson_friends_process) > 0:
            score_friends = calculate_friends_game_score(pearson_friends_process, tfidf_game['steam_id'])

        score = game[0]['score'] + 1

        return (tfidf_game['steam_id'],cosinus_similarity * library_score * score_friends * score * \
                                                   common_caracteristics_score_process[tfidf_game['steam_id']])
    else:
        return (-1,-1)

def calculate_similarities(library_tfidf, pearson_friends, current_game, user_games, games, common_caracteristics_score,
                           genres, tags,
                           game_details, tfidf_games):
    tfidf_current_game = calculate_tfidf(current_game, len(games), genres, tags, game_details)

    games_similarity = {}
    print("Start pool")
    start = time.time()
    with multiprocessing.Pool(processes=None, initializer=init_process,
                              initargs=[games, tfidf_current_game, library_tfidf, pearson_friends,
                                        common_caracteristics_score]) as pool:

        results = pool.imap_unordered(loop_tfidf, tfidf_games, 10000)
        for id, tfidf in results:
            if (id != -1):
                games_similarity[id] = tfidf

    end = time.time()
    print(end-start)
    return games_similarity


def calculate_library(games, genres, tags, game_details):
    count_genres = dict((genre.name, 0) for genre in genres.order_by('name'))
    count_tags = dict((tag.name, 0) for tag in tags.order_by('name'))
    count_games_details = dict((game_detail.name, 0) for game_detail in game_details.order_by('name'))

    total_genre = 0
    total_tag = 0
    total_game_detail = 0

    for game in games:
        for name, indexes in json.loads(game['genres']).items():
            count = len(indexes)
            count_genres[name] += count
            total_genre += count

        for name, indexes in json.loads(game['popular_tags']).items():
            count = len(indexes)
            count_tags[name] += count
            total_tag += count

        for name, indexes in json.loads(game['game_details']).items():
            count = len(indexes)
            count_games_details[name] += count
            total_game_detail += count

    vector = []
    for key, value in count_genres.items():
        if total_genre > 0:
            vector.append(float(value / total_genre + 1))
        else:
            vector.append(1.0)

    for key, value in count_tags.items():
        if total_tag > 0:
            vector.append((value / total_tag + 1))
        else:
            vector.append(1.0)

    for key, value in count_games_details.items():
        if total_game_detail > 0:
            vector.append((value / total_game_detail + 1))
        else:
            vector.append(1.0)

    return np.asarray(vector)


def calculate_friends_pearson(user_id, library_tfidf, games, genres, tags, game_details):
    friends_steam_id = get_friends_by_user(user_id)
    games_id_friends = [[app['appid'] for app in get_games_by_user(steam_id)] for steam_id in friends_steam_id]

    pearson_friends = {}
    for games_id_friend in games_id_friends:
        if len(games_id_friend) > 0:
            friend_games = [game for game in games if game['steam_id'] in games_id_friend]
            library_tfidf_friends = calculate_library(friend_games, genres, tags, game_details)
            pearson_friends[st.pearsonr(library_tfidf, library_tfidf_friends)[0]] = games_id_friend

    return pearson_friends


def calculate_friends_game_score(pearson_friends, steam_id):
    count_presence = 0
    for pearson, games_id_friend in pearson_friends.items():
        for game_id in games_id_friend:
            if game_id == steam_id:
                count_presence += pearson

    if len(pearson_friends) > 0:
        return 1 + count_presence / len(pearson_friends)
    return 1
