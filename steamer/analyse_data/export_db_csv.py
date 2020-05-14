#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
sys.path.append('../')
sys.path.append('./')
import pathlib
from database.db import Game, connect_db
import json
connect_db()

with open(str(pathlib.Path(__file__).parent.absolute()) + '/steamer.csv', 'w', newline='', encoding="utf8") as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='|')
    for game in Game.objects():
        reviews = json.loads(game.reviews)

        labels = ['OS', 'Processor', 'Memory', 'Graphics', 'Storage', 'Additional Notes', 'DirectX', 'Sound Card', 'Network', 'Recommended', 'Minimum']
        minimum_requirements = json.loads(game.minimum_requirements)
        for element in labels:
            if element not in minimum_requirements.keys():
                minimum_requirements[element] = ""

        recommended_requirements = json.loads(game.recommended_requirements)
        for element in labels:
            if element not in recommended_requirements.keys():
                recommended_requirements[element] = ""

        csvwriter.writerow([
            game.steam_id,
            game.url,
            game.name,
            game.desc_snippet,
            reviews["status"],
            reviews["count"],
            reviews["percentage"],
            reviews["desc"],
            game.release_date,
            game.developer,
            game.popular_tags,
            game.game_details,
            game.languages,
            game.genres,
            game.game_description,
            game.mature_content,
            minimum_requirements["OS"],
            minimum_requirements["Processor"],
            minimum_requirements["Memory"],
            minimum_requirements["Graphics"],
            minimum_requirements["Storage"],
            recommended_requirements["Additional Notes"],
            minimum_requirements["DirectX"],
            minimum_requirements["Sound Card"],
            minimum_requirements["Network"],
            minimum_requirements["Minimum"],
            minimum_requirements["Recommended"],
            recommended_requirements["OS"],
            recommended_requirements["Processor"],
            recommended_requirements["Memory"],
            recommended_requirements["Graphics"],
            recommended_requirements["Storage"],
            recommended_requirements["Additional Notes"],
            recommended_requirements["DirectX"],
            recommended_requirements["Sound Card"],
            recommended_requirements["Network"],
            recommended_requirements["Minimum"],
            recommended_requirements["Recommended"],
            game.original_price,
            game.discount_price
        ])
