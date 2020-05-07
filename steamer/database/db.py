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
    url = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    desc_snippet = db.StringField(required=True)
    reviews = db.StringField()
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

                reviews = {"status": status_reviews,
                           "count": number_reviews,
                           "percentage": percentage_reviews,
                           "desc": desc_reviews}

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

                minimum_requirements_data = row[16].split(",")
                minimum_requirements = {}
                for i in range(0, len(minimum_requirements_data) - 2, 1):
                    value = minimum_requirements_data[i+1]

                    if value[:-1] not in ['OS', 'Processor', 'Memory', 'Graphics', 'Storage', 'Additional Notes']:
                        key = minimum_requirements_data[i][:-1]
                        minimum_requirements[key] = value
                        i += 1

                recommended_requirements_data = row[17].split(",")
                recommended_requirements = {}
                for i in range(1, len(recommended_requirements_data) - 2, 1):
                    value = recommended_requirements_data[i + 1]

                    if value[:-1] not in ['OS', 'Processor', 'Memory', 'Graphics', 'Storage', 'Additional Notes']:
                        key = recommended_requirements_data[i][:-1]
                        recommended_requirements[key] = value
                        i += 1

                original_price = row[18]
                discount_price = row[19]

                Game(
                    url=url,
                    name=name,
                    desc_snippet=desc_snippet,
                    reviews=json.dumps(reviews),
                    release_date=release_date,
                    developer=developer,
                    popular_tags=popular_tags,
                    game_details=game_details,
                    languages=languages,
                    genre=genre,
                    game_description=game_description,
                    mature_content=mature_content,
                    minimum_requirements=json.dumps(minimum_requirements),
                    recommended_requirements=json.dumps(recommended_requirements),
                    original_price=original_price,
                    discount_price=discount_price
                ).save()


if __name__ == "__main__":
    populate_db()
