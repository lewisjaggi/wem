#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mongoengine as me
from flask_mongoengine import MongoEngine
import csv
import pathlib
import json
import re

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
    popular_tags = db.ListField()
    game_details = db.ListField()
    languages = db.ListField()
    genres = db.ListField()
    game_description = db.StringField()
    mature_content = db.StringField()
    minimum_requirements = db.StringField()
    recommended_requirements = db.StringField()
    original_price = db.StringField()
    discount_price = db.StringField()


class Genre(db.Document):
    name = db.StringField(required=True, unique=True)


class Tag(db.Document):
    name = db.StringField(required=True, unique=True)


class GameDetail(db.Document):
    name = db.StringField(required=True, unique=True)


class Developer(db.Document):
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
                    requirements[key] = ", ".join(value) if len(value) else ""
                    value = []
                key = requirements_data[i][:-1]
                key = key if key != 'Hard Drive' else 'Storage'
                key = key if key != 'Sound' else 'Sound Card'
            else:
                if str(value) != "NaN":
                    value.append(requirements_data[i])
        else:
            value.append(requirements_data[i])
            requirements[key] = ", ".join(value) if len(value) else ""
    return requirements


def populate_db():
    db_config = Config.MONGODB_SETTINGS
    connection = me.connect(**db_config)
    me.connection.get_db()
    connection.drop_database(db_config['db'])
    is_header = True

    with open(str(pathlib.Path(__file__).parent.absolute()) + '/steam_games.csv', newline='',
              encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")

        table_genres = []
        table_tags = []
        table_games_details = []
        table_languages = []
        table_developers = []

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
                i_reviews += 1

                p = re.compile(r' \d+%')
                percentage = p.search(all_reviews[i_reviews]) if len(all_reviews) > i_reviews else ""
                percentage_reviews = percentage.group(0)[1:] if percentage != "" and percentage is not None else ""
                i_reviews += 1

                desc_reviews = all_reviews[i_reviews] if len(all_reviews) > i_reviews else ""

                reviews = {"status": str(status_reviews) if str(status_reviews) != "NaN" else "",
                           "count": str(number_reviews) if str(number_reviews) != "NaN" else "",
                           "percentage": str(percentage_reviews) if str(percentage_reviews) != "NaN" else "",
                           "desc": str(desc_reviews) if str(desc_reviews) != "NaN" else ""}

                release_date = row[6] if row[6] != "NaN" else ""

                developer = row[7] if row[7] != "NaN" else ""

                publisher = row[8] if row[8] != "NaN" else ""

                popular_tags = row[9].split(',')
                if "NaN" in popular_tags:
                    popular_tags.remove("NaN")

                game_details = row[10].split(',')
                if "NaN" in game_details:
                    game_details.remove("NaN")

                languages = row[11].split(',')

                if "NaN" in languages:
                    languages.remove("NaN")

                achievements = row[12] if row[12] != "NaN" else ""

                genres = row[13].split(',')
                if "NaN" in genres:
                    genres.remove("NaN")

                game_description = row[14] if row[14] != "NaN" else ""

                mature_content = row[15][77:] if row[15] != "" else "" if row[15] != "NaN" else ""

                minimum_requirements = format_requirement(row[16].split(","))

                recommended_requirements = format_requirement(row[17].split(","))

                original_price = row[18] if row[18] != "NaN" else ""

                discount_price = row[19] if row[19] != "NaN" else ""

                try:
                    Game(
                        steam_id=steam_id,
                        url=url,
                        name=name,
                        desc_snippet=desc_snippet,
                        reviews=json.dumps(reviews),
                        release_date=release_date,
                        developer=developer,
                        popular_tags=popular_tags,
                        game_details=game_details,
                        languages=languages,
                        genres=genres,
                        game_description=game_description,
                        mature_content=mature_content,
                        minimum_requirements=json.dumps(minimum_requirements),
                        recommended_requirements=json.dumps(recommended_requirements),
                        original_price=original_price,
                        discount_price=discount_price
                    ).save()
                except:
                    print("The id : " + steam_id + " is duplicated")


                for genre in genres:
                    if genre not in table_genres:
                        table_genres.append(genre)

                for tag in popular_tags:
                    if tag not in table_tags:
                        table_tags.append(tag)

                for detail in game_details:
                    if detail not in table_games_details:
                        table_games_details.append(detail)

                for language in languages:
                    if language not in table_languages:
                        table_languages.append(language)

                if developer not in table_developers:
                    table_developers.append(developer)

        for genre in table_genres:
            Genre(name=genre).save()

        for tag in table_tags:
            Tag(name=tag).save()

        for detail in table_games_details:
            GameDetail(name=detail).save()

        for developer in table_developers:
            Developer(name=developer).save()


if __name__ == "__main__":
    populate_db()
