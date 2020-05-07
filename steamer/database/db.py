#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mongoengine as me
from flask_mongoengine import MongoEngine
import csv
import os
import pathlib

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
    url = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    desc_snippet = db.StringField(required=True)
    all_reviews = db.StringField(required=True)
    release_date = db.StringField()
    developer = db.StringField(required=True)
    popular_tags = db.ListField(required=True)
    game_details = db.ListField(required=True)
    languages = db.ListField(required=True)
    genre = db.ListField(required=True)
    game_description = db.StringField(required=True)
    mature_content = db.StringField(required=True)
    minimum_requirements = db.StringField(required=True)
    recommended_requirements = db.StringField(required=True)
    original_price = db.StringField(required=True)
    discount_price = db.StringField(required=True)


def populate_db():
    # Connect using MongoEngine
    # no Flask app created
    db_config = Config.MONGODB_SETTINGS
    connection = me.connect(**db_config)
    me.connection.get_db()
    connection.drop_database(db_config['db'])
    is_header = True

    with open(str(pathlib.Path(__file__).parent.absolute()) + '/steam_games.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            if is_header:
                is_header = False
            else:
                url = row[0]
                types = row[1]
                name = row[2]
                desc_snippet = row[3]
                recent_reviews = row[4]
                all_reviews = row[5]
                release_date = row[6] if row[6] != "NaN" else ""
                developer = row[7]
                publisher = row[8]
                popular_tags = row[9].split(',')
                game_details = row[10].split(',')
                languages = row[11].split(',')
                achievements = row[12]
                genre = row[13].split(',')
                game_description = row[14]
                mature_content = row[15]
                minimum_requirements = row[16]
                recommended_requirements = row[17]
                original_price = row[18]
                discount_price = row[19]

                Game(
                    url=url,
                    name=name,
                    desc_snippet=desc_snippet,
                    all_reviews=all_reviews,
                    release_date=release_date,
                    developer=developer,
                    popular_tags=popular_tags,
                    game_details=game_details,
                    languages=languages,
                    genre=genre,
                    game_description=game_description,
                    mature_content=mature_content,
                    minimum_requirements=minimum_requirements,
                    recommended_requirements=recommended_requirements,
                    original_price=original_price,
                    discount_price=discount_price
                ).save()
        print(Game.objects())


if __name__ == "__main__":
    populate_db()
