import requests
import re
from steamer.database.db import Game


def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


def get_game_details_by_id(game_id):
    game = Game.objects(steam_id='app/'+game_id)
    if len(game) == 0:
        game = get_api_game_details_by_id(game_id)
        return '{"toto": "toto"}'
    else:
        game = get_api_game_details_by_id(game_id)
        return game[0].to_json()


def get_api_game_details_by_id(game_id):
    payload = {
        'appids': game_id,
        'cc': 'us'
    }
    r = requests.get('https://store.steampowered.com/api/appdetails', params=payload)
    r_steam_spy = requests.get('https://steamspy.com/api.php', params={'request': 'appdetails', 'appid': game_id})

    if r.status_code != 200 or r_steam_spy.status_code != 200:
        return {
            'status_code': r.status_code,
            'error': r.text
        }

    steam_game = r.json().get(game_id).get('data')
    steam_spy = r_steam_spy.json()

    game = Game(
        steam_id='app/' + str(steam_game.get('steam_appid')),
        url='https://store.steampowered.com/app/' + str(steam_game.get('steam_appid')) + '/',
        name=steam_game.get('name'),
        desc_snippet=steam_game.get('short_description'),
        # reviews=steam_game.get(''),
        release_date=steam_game.get('release_date').get('date'),
        developer=steam_game.get('developers')[0],
        # popular_tags=steam_game.get(''),
        game_details=map(lambda x: x.get('description'), steam_game.get('categories')),
        languages=map(lambda x: x.strip(), steam_game.get('supported_languages').split(',')),
        genres=map(lambda x: x.get('description'), steam_game.get('genres')),
        game_description=cleanhtml(steam_game.get('detailed_description')),
        mature_content='',
        minimum_requirements=steam_game.get('pc_requirements').get('minimum'),
        recommended_requirements=steam_game.get('pc_requirements').get('recommended'),
        original_price=steam_game.get('price_overview').get('final_formatted'),
        discount_price=''
    )
    # game.save()

    return [game]
