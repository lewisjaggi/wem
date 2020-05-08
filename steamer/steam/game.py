import json
import re

import requests

from steamer.database.db import Game


def clean_html(raw_html):
    clean_r = re.compile('<.*?>')
    clean_text = re.sub(clean_r, '', raw_html)
    return clean_text


def get_game_details_by_id(game_id):
    game = Game.objects(steam_id=game_id)
    if len(game) == 0:
        return json.dumps(get_api_game_details_by_id(game_id))
    return game[0].to_json()


def get_api_game_details_by_id(game_id):
    payload = {
        'appids': game_id,
        'cc': 'us'
    }
    r = requests.get('https://store.steampowered.com/api/appdetails', params=payload)
    r_steam_spy = requests.get('https://steamspy.com/api.php', params={'request': 'appdetails', 'appid': game_id})

    if r.status_code != 200 or r_steam_spy.status_code != 200 or not r.json().get(game_id).get('success'):
        return {
            'status_code': 400,
            'error': 'Bad Request'
        }

    steam_game = r.json().get(game_id).get('data')
    steam_spy = r_steam_spy.json()

    return Game(
        steam_id=steam_game.get('steam_appid'),
        url='https://store.steampowered.com/app/' + str(steam_game.get('steam_appid')) + '/',
        name=steam_game.get('name'),
        desc_snippet=steam_game.get('short_description'),
        reviews={'count': 1234567890, 'percentage': '1234567890%'},
        release_date=steam_game.get('release_date').get('date'),
        developer=steam_game.get('developers')[0],
        popular_tags=steam_spy.get('tags').keys(),
        game_details=map(lambda x: x.get('description'), steam_game.get('categories')),
        languages=map(lambda x: x.strip(), steam_game.get('supported_languages').split(',')),
        genres=map(lambda x: x.get('description'), steam_game.get('genres')),
        game_description=clean_html(steam_game.get('detailed_description')),
        mature_content='',
        minimum_requirements=steam_game.get('pc_requirements').get('minimum'),
        recommended_requirements=steam_game.get('pc_requirements').get('recommended'),
        original_price=steam_game.get('price_overview').get('final_formatted'),
        discount_price=''
    )
