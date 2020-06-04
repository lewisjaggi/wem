#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import json
import re
from steamer.database.caracteristics import validated_genres, validated_tags, validated_game_details
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

    validated_genres_count = dict((validated_genre, [0, 0]) for validated_genre in validated_genres)
    total_genres = len(game.genres)
    for genre in game.genres:
        for validated_genre in validated_genres:
            if validated_genre in genre:
                validated_genres_count[validated_genre][0] += 1 - game.genres.index(genre) / total_genres
                validated_genres_count[validated_genre][1] += 1

    validated_tags_count = dict((validated_tag, [0, 0]) for validated_tag in validated_tags)
    total_tags = len(game.popular_tags)
    for tag in game.popular_tags:
        for validated_tag in validated_tags:
            if validated_tag in tag:
                validated_tags_count[validated_tag][0] += 1 - game.popular_tags.index(tag) / total_tags
                validated_tags_count[validated_tag][1] += 1

    validated_game_details_count = dict((validated_game_detail, [0, 0]) for validated_game_detail in validated_game_details)
    total_game_details = len(game.game_details)
    for game_detail in game.game_details:
        for validated_game_detail in validated_game_details:
            if validated_game_detail in game_detail:
                validated_game_details_count[validated_game_detail][0] += 1 - game.game_details.index(game_detail) / total_game_details
                validated_game_details_count[validated_game_detail][1] += 1

    for genre in genres.order_by('name'):
        tfidf = 1.0
        if genre.count > 0:
            validated_genre_count = validated_genres_count[genre.name]
            ranking = validated_genre_count[0]
            count = validated_genre_count[1]
            tfidf += count * np.log(total_games / genre.count) * ranking
            game_tfidf.append(tfidf)

    for tag in tags.order_by('name'):
        tfidf = 1.0
        if tag.count > 0:
            validated_tag_count = validated_tags_count[tag.name]
            ranking = validated_tag_count[0]
            count = validated_tag_count[1]
            tfidf += count * np.log(total_games / tag.count) * ranking
            game_tfidf.append(tfidf)

    for game_detail in game_details.order_by('name'):
        tfidf = 1.0
        if game_detail.count > 0:
            validated_game_detail_count = validated_game_details_count[game_detail.name]
            ranking = validated_game_detail_count[0]
            count = validated_game_detail_count[1]
            tfidf += count * np.log(total_games / game_detail.count) * ranking
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
            for validated_genre in validated_genres:
                if validated_genre in genre:
                    count_genres[validated_genre] += 1
                    total_genre += 1

        for tag in game.popular_tags:
            for validated_tag in validated_tags:
                if validated_tag in tag:
                    count_tags[validated_tag] += 1
                    total_tag += 1

        for game_detail in game.game_details:
            for validated_game_detail in validated_game_details:
                if validated_game_detail in game_detail:
                    count_games_details[validated_game_detail] += 1
                    total_game_detail += 1

    vector = []
    for key, value in count_genres.items():
        vector.append(float(value / total_tag + 1))

    for key, value in count_tags.items():
        vector.append((value / total_tag + 1))

    for key, value in count_games_details.items():
        vector.append((value / total_game_detail + 1))

    return np.asarray(vector)
