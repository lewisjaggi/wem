#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import json
import re
from sklearn.metrics.pairwise import cosine_similarity


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

    game_genres = game.genres
    generator_genres = [genre for genre in genres.order_by('name') if genre.count > 10]
    for genre in generator_genres:
        tfidf = 1.0
        if genre.name in game_genres:
            rank = [game.genres.index(name) if name == genre.name else -1 for name in game.genres][0]
            total_rank = len(game.genres)
            ratio_ranking = (total_rank - rank) / total_rank
            tfidf += np.log(total_games / genre.count) * ratio_ranking
        game_tfidf.append(tfidf)

    game_popular_tags = game.popular_tags
    generator_tags = [tag for tag in tags.order_by('name') if tag.count > 10]
    for tag in generator_tags:
        tfidf = 1.0
        if tag.name in game_popular_tags:
            rank = [game.popular_tags.index(name) if name == tag.name else -1 for name in game.popular_tags][0]
            total_rank = len(game.popular_tags)
            ratio_ranking = (total_rank - rank) / total_rank
            tfidf += np.log(total_games / tag.count) * ratio_ranking
        game_tfidf.append(tfidf)

    game_game_details = game.game_details
    generator_game_details = [game_detail for game_detail in game_details.order_by('name') if game_detail.count > 10]
    for gameDetail in generator_game_details:
        tfidf = 1.0
        if gameDetail.name in game_game_details:
            rank = [game.game_details.index(name) if name == gameDetail.name else -1 for name in game.game_details][0]
            total_rank = len(game.game_details)
            ratio_ranking = (total_rank - rank) / total_rank
            tfidf += np.log(total_games / gameDetail.count) * ratio_ranking
        game_tfidf.append(tfidf)

    return np.asarray(game_tfidf)


def calculate_similarities(current_game, user_games, games, genres, tags, game_details, tfidf_games):
    tfidf_current_game = calculate_tfidf(current_game, len(games), genres, tags, game_details)

    games_similarity = {}

    for tfidf_game in tfidf_games:
        game = [game for game in games if game.steam_id == tfidf_game.steam_id]
        if len(game) > 0:
            tfidf = np.asarray(tfidf_game.tfidf)

            library_tfidf = calculate_library(user_games, genres, tags, game_details)

            cosinus_similarity = np.dot(tfidf, tfidf_current_game) / (
                    np.sqrt(np.dot(tfidf,tfidf)) * (np.sqrt(np.dot(tfidf_current_game, tfidf_current_game))))

            library_score = np.dot(tfidf, library_tfidf) / (
                    np.sqrt(np.dot(tfidf, tfidf)) * (np.sqrt(np.dot(library_tfidf, library_tfidf))))

            cosinus_similarity = cosinus_similarity * library_score

            score = game[0].score + 1

            games_similarity[tfidf_game.steam_id] = cosinus_similarity * score

    return games_similarity


def calculate_library(games, genres, tags, game_details):
    count_genres = dict((genre.name, 0.0) for genre in genres.order_by('name') if genre.count > 10)
    count_tags = dict((tag.name, 0.0) for tag in tags.order_by('name') if tag.count > 10)
    count_games_details = dict((game_detail.name, 0.0) for game_detail in game_details.order_by('name') if game_detail.count > 10)

    total_genre = 0.0
    total_tag = 0.0
    total_game_detail = 0.0

    for game in games:
        for genre in game.genres:
            if genres.get(name=genre).count > 10:
                current = genre.strip()
                count_genres[current] += 1
                total_genre += 1

        for tag in game.popular_tags:
            if tags.get(name=tag).count > 10:
                current = tag.strip()
                count_tags[current] += 1
                total_tag += 1

        for detail in game.game_details:
            if game_details.get(name=detail).count > 10:
                current = detail.strip()
                count_games_details[current] += 1
                total_game_detail += 1

    vector = []
    for key, value in count_genres.items():
        vector.append(float(value / total_tag + 1))

    for key, value in count_tags.items():
        vector.append((value / total_tag + 1))

    for key, value in count_games_details.items():
        vector.append((value / total_game_detail + 1))

    return np.asarray(vector)
