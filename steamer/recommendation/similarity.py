#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import json
import re
def calculate_score(game, numberVote):
    reviews = json.loads(game.reviews)
    score = float(reviews["percentage"]) / 100 if reviews["percentage"] != '' else 0
    count = reviews["count"].replace(',','')
    current_vote = float(count) - numberVote.min if bool(re.search(r'\d', count)) else 0
    max_vote = numberVote.max - numberVote.min

    vote_ratio = current_vote / float(max_vote)

    return score * vote_ratio

def calculate_tfidf(game, total_games, genres, tags, game_details):
    game_tfidf = []

    game_genres = game.genres
    for genre in genres:
        tfidf = 0
        if genre.name in game_genres:
            tfidf = np.log(total_games / genre.count)
        game_tfidf.append(tfidf)

    game_popular_tags = game.popular_tags
    for tag in tags:
        tfidf = 0
        if tag.name in game_popular_tags:
            tfidf = np.log(total_games / tag.count)
        game_tfidf.append(tfidf)

    game_game_details = game.game_details
    for gameDetail in game_details:
        tfidf = 0
        if gameDetail.name in game_game_details:
            tfidf = np.log(total_games / gameDetail.count)
        game_tfidf.append(tfidf)

    return np.asarray(game_tfidf)


def calculate_similarities(current_game, games, genres, tags, game_details, tfidf_games):
    tfidf_current_game = calculate_tfidf(current_game, len(games), genres, tags, game_details)

    games_similarity = {}

    for tfidf_game in tfidf_games:
        tfidf = np.asarray(tfidf_game.tfidf)
        cosinus_similarity = games_similarity[tfidf_game.steam_id] = np.dot(tfidf, tfidf_current_game) / (np.linalg.norm(tfidf) * (np.linalg.norm(tfidf_current_game)))

        score = games.get(steam_id=tfidf_game.steam_id).score + 1

        cosinus_similarity = cosinus_similarity if cosinus_similarity is not None else 0
        score = score if score is not None else 0
        games_similarity[tfidf_game.steam_id] = cosinus_similarity * score

    return games_similarity
