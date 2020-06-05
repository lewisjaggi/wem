#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from steamer.recommendation.similarity import calculate_tfidf, calculate_score
import mongoengine as me
from flask_mongoengine import MongoEngine
import csv
import pathlib
import json
import re
import math
from steamer.database.caracteristics import validated_genres, validated_tags, validated_game_details

db = MongoEngine()


def initialize_db(app):
    db.init_app(app)


class Config(object):
    MONGODB_SETTINGS = {
        'alias': 'default',
        'db': 'steamer',
        'host': 'localhost',
        'port': 27017,
    }


class Game(db.Document):
    steam_id = db.IntField(required=True, unique=True)
    url = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    desc_snippet = db.StringField()
    reviews = db.StringField()
    release_date = db.StringField()
    developer = db.StringField()
    popular_tags = db.StringField()
    game_details = db.StringField()
    languages = db.ListField()
    genres = db.StringField()
    game_description = db.StringField()
    mature_content = db.StringField()
    minimum_requirements = db.StringField()
    recommended_requirements = db.StringField()
    original_price = db.FloatField()
    discount_price = db.FloatField()
    score = db.FloatField()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects(steam_id=id)


class Genre(db.Document):
    name = db.StringField(required=True, unique=True)
    count = db.IntField(required=True)


class Tag(db.Document):
    name = db.StringField(required=True, unique=True)
    count = db.IntField(required=True)


class GameDetail(db.Document):
    name = db.StringField(required=True, unique=True)
    count = db.IntField(required=True)


class TfidfGame(db.Document):
    steam_id = db.IntField(required=True, unique=True)
    tfidf = db.ListField(required=True)


class NumberVote(db.Document):
    min = db.IntField(required=True)
    max = db.IntField(required=True)


class Language(db.Document):
    name = db.StringField(required=True, unique=True)


def connect_db():
    # Connect using MongoEngine
    # no Flask app created
    db_config = Config.MONGODB_SETTINGS
    connection = me.connect(**db_config)
    me.connection.get_db()


def format_requirement(data):
    requirements_data = data
    requirements = {}
    labels = ['OS', 'Processor', 'Memory', 'Graphics', 'Storage', 'Additional Notes', 'DirectX', 'Sound Card',
              'Network', 'Recommended', 'Minimum', 'Hard Drive', 'Sound']
    key = ""
    value = []
    for i in range(1, len(requirements_data) - 1, 1):
        if i != len(requirements_data) - 1:
            if requirements_data[i][:-1] in labels:
                if i != 1:
                    requirements[key] = ", ".join(value) if len(value) > 1 else value if len(value) else ""
                    value = []
                key = requirements_data[i][:-1]
                key = key if key != 'Hard Drive' else 'Storage'
                key = key if key != 'Sound' else 'Sound Card'
            else:
                if str(value) != "NaN":
                    value.append(requirements_data[i])
        else:
            value.append(requirements_data[i])
            requirements[key] = ", ".join(value) if len(value) > 1 else value if len(value) else ""
    return requirements


def clean_list(list):
    if "NaN" in list:
        list.remove("NaN")

    if "" in list:
        list.remove("")

    for i in range(0, len(list)):
        list[i] = list[i].replace("\xa0\r\n\t\t\t\t\t\t\t\t\t", "").replace('\\xa0\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t',
                                                                            '').strip()

    return list


def clean_price(price):
    price = price.replace('$', '').strip().lower()
    try:
        return float(price)
    except (ValueError, Exception):
        return 0.0


def populate_db():
    print("")
    print("The process will take several minutes")
    print("Start connection to MongoDB")
    db_config = Config.MONGODB_SETTINGS
    connection = me.connect(**db_config)
    me.connection.get_db()
    print("Connected")
    connection.drop_database(db_config['db'])
    print("Database cleaned")
    is_header = True
    print("Start importing games")

    table_genres = dict((validated_genre, 0) for validated_genre in validated_genres)
    table_tags = dict((validated_tag, 0) for validated_tag in validated_tags)
    table_game_details = dict((validated_game_detail, 0) for validated_game_detail in validated_game_details)
    max_vote = 0
    min_vote = math.inf
    table_languages = []

    with open(str(pathlib.Path(__file__).parent.absolute()) + '/steam_games.csv', newline='',
              encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")

        for row in reader:
            if is_header:
                is_header = False
            else:
                split_url = row[0].split('/')
                if len(split_url) < 5:
                    continue

                if split_url[3] != 'app':
                    continue

                steam_id = split_url[4]

                url = row[0] if row[0] != "NaN" else ""

                types = row[1] if row[1] != "NaN" else ""

                name = row[2] if row[2] != "NaN" else ""

                desc_snippet = row[3] if row[3] != "NaN" else ""

                recent_reviews = row[4] if row[4] != "NaN" else ""

                all_reviews = row[5].split(',')

                i_reviews = 0
                status_reviews = all_reviews[i_reviews] if len(all_reviews) > i_reviews else ""
                i_reviews += 1

                number_reviews = ""
                if len(all_reviews) > i_reviews:
                    number_reviews = all_reviews[i_reviews][1:]
                    if ")" in all_reviews[i_reviews]:
                        number_reviews = number_reviews[:-1]
                    elif len(all_reviews) > i_reviews + 1:
                        i_reviews += 1
                        number_reviews += "," + all_reviews[i_reviews][:-1]

                current_vote = 0

                if number_reviews.replace(',', '').isdigit():
                    current_vote = int(number_reviews.replace(',', ''))

                max_vote = current_vote if current_vote > max_vote else max_vote
                min_vote = current_vote if current_vote < min_vote else min_vote

                i_reviews += 1

                p = re.compile(r' \d+%')
                percentage = p.search(all_reviews[i_reviews]) if len(all_reviews) > i_reviews else ""
                percentage_reviews = percentage.group(0)[1:-1] if percentage != "" and percentage is not None else ""

                desc_reviews = all_reviews[i_reviews].split('%')[1] if percentage_reviews != "" else ""
                i_reviews += 1

                desc_reviews += "," + all_reviews[i_reviews] if len(all_reviews) > i_reviews else ""

                reviews = {"status": str(status_reviews) if str(status_reviews) != "NaN" else "",
                           "count": str(number_reviews) if str(number_reviews) != "NaN" else "",
                           "percentage": str(percentage_reviews) if str(percentage_reviews) != "NaN" else "",
                           "desc": str(desc_reviews) if str(desc_reviews) != "NaN" else ""}

                release_date = row[6] if row[6] != "NaN" else ""

                developer = row[7] if row[7] != "NaN" else ""

                publisher = row[8] if row[8] != "NaN" else ""

                popular_tags = valid_caracteristic(clean_list(row[9].split(',')), validated_tags)
                game_details = valid_caracteristic(clean_list(row[10].split(',')), validated_game_details)

                languages = clean_list(row[11].split(','))
                languages = [language for language in languages if language.isalpha()]

                achievements = row[12] if row[12] != "NaN" else ""

                genres = valid_caracteristic(clean_list(row[13].split(',')), validated_genres)

                game_description = row[14] if row[14] != "NaN" else ""

                mature_content = row[15][77:] if row[15] != "" else "" if row[15] != "NaN" else ""

                minimum_requirements = format_requirement(row[16].split(","))

                recommended_requirements = format_requirement(row[17].split(","))

                original_price = clean_price(row[18])

                discount_price = clean_price(row[19])

                try:
                    game = Game(
                        steam_id=steam_id,
                        url=url,
                        name=name,
                        desc_snippet=desc_snippet,
                        reviews=json.dumps(reviews),
                        release_date=release_date,
                        developer=developer,
                        popular_tags=json.dumps(popular_tags),
                        game_details=json.dumps(game_details),
                        languages=languages,
                        genres=json.dumps(genres),
                        game_description=game_description,
                        mature_content=mature_content,
                        minimum_requirements=json.dumps(minimum_requirements),
                        recommended_requirements=json.dumps(recommended_requirements),
                        original_price=original_price,
                        discount_price=discount_price,
                        score=0
                    ).save()

                    for name, indexes in genres.items():
                        table_genres[name] += len(indexes)

                    for name, indexes in popular_tags.items():
                        table_tags[name] += len(indexes)

                    for name, indexes in game_details.items():
                        table_game_details[name] += len(indexes)

                    for language in languages:
                        if language not in table_languages:
                            table_languages.append(language)
                except:
                    print("The id : " + steam_id + " is duplicated")

    print("Games imported")
    print("Start importing genres")
    for name, count in table_genres.items():
        Genre(name=name, count=count).save()

    print("Genres imported")
    print("Start importing popular tags")
    for name, count in table_tags.items():
        Tag(name=name, count=count).save()

    print("Popular tags imported")
    print("Start importing game details")
    for name, count in table_game_details.items():
        GameDetail(name=name, count=count).save()
    print("Game details imported")

    print("Start importing languages")
    for language in table_languages:
        Language(name=language).save()
    print("Languages imported")

    print("Start calculation tfidf")
    total_games = len(Game.objects())
    genres = Genre.objects()
    tags = Tag.objects()
    game_details = GameDetail.objects()
    tfidf_games = {game.steam_id: calculate_tfidf(game, total_games, genres, tags, game_details) for game in
                   Game.objects()}

    for steam_id, tfidf in tfidf_games.items():
        TfidfGame(
            steam_id=steam_id,
            tfidf=tfidf.tolist()
        ).save()
    print("Tfidf calculated")
    print("Start calculation scores")
    NumberVote(min=min_vote, max=max_vote).save()
    for game in Game.objects():
        score = calculate_score(game, NumberVote.objects()[0])
        game.update(score=score)
    print("Scores calculated")
    print("Database Ready")
    print("")


def update_caracteristics(genres, tags, game_details, languages):
    for name, indexes in genres.items():
        genre = Genre.objects(name=name)[0]
        genre.update(count=genre.count + len(indexes))

    for name, indexes in tags.items():
        tag = Tag.objects(name=name)[0]
        tag.update(count=tag.count + len(indexes))

    for name, indexes in game_details.items():
        game_detail = GameDetail.objects(name=name)[0]
        game_detail.update(count=game_detail.count + len(indexes))

    for language in languages:
        db_language = Language.objects(name=language)
        if len(db_language) == 0:
            Language(name=language).save()


def update_tfidf():
    all_games = Game.objects()

    for game in all_games:
        tfidf = TfidfGame.objects(steam_id=game.steam_id)
        if len(tfidf) == 0:
            TfidfGame(steam_id=game.steam_id, tfidf=calculate_tfidf(game, len(all_games), Genre.objects(),
                                                                    Tag.objects(), GameDetail.objects())).save()
        else:
            tfidf[0].update(
                tfidf=calculate_tfidf(game, len(all_games), Genre.objects(),
                                      Tag.objects(), GameDetail.objects()))


def valid_caracteristic(caracteristics, validated_caracteristics):
    caracteristics_valided = dict((validated_caracteristic, []) for validated_caracteristic in validated_caracteristics)

    for caracteristic in caracteristics:
        for validated_caracteristic in validated_caracteristics:
            if validated_caracteristic in caracteristic:
                caracteristics_valided[validated_caracteristic].append(caracteristics.index(caracteristic))

    return caracteristics_valided


if __name__ == "__main__":
    populate_db()
