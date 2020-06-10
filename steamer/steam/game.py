import re
import requests
import json
from steamer.database.db import Game, clean_list, update_caracteristics, clean_price, valid_characteristics
from steamer.database.caracteristics import validated_genres, validated_tags, validated_game_details


def clean_html(raw_html):
    clean_r = re.compile('<.*?>')
    clean_text = re.sub(clean_r, '', raw_html)
    return clean_text


def get_game_details_by_id(game_id):
    game = Game.objects(steam_id=game_id)
    if len(game) == 0:
        return get_api_game_details_by_id(str(game_id))
    return game[0]


def get_api_game_details_by_id(game_id):
    payload = {
        'appids': game_id,
        'cc': 'us'
    }
    r = requests.get('https://store.steampowered.com/api/appdetails', params=payload)
    r_steam_spy = requests.get('https://steamspy.com/api.php', params={'request': 'appdetails', 'appid': game_id})

    if r.status_code != 200 or r_steam_spy.status_code != 200 or not r.json()[game_id]['success']:
        return None

    steam_game = r.json().get(game_id).get('data')

    steam_id = steam_game.get('steam_appid')
    game = Game.objects(steam_id=int(steam_id))
    if len(game) == 0:
        steam_spy = r_steam_spy.json()

        total_reviews = steam_spy.get('positive') + steam_spy.get('negative')
        percentage_positive_reviews = '0%' if total_reviews == 0 else str(
            steam_spy.get('positive') / total_reviews * 100)

        url = 'https://store.steampowered.com/app/' + str(steam_game.get('steam_appid')) + '/'
        name = steam_game.get('name')
        desc_snippet = steam_game.get('short_description')
        reviews = '{"count": ' + str(total_reviews) + ', "percentage": ' + percentage_positive_reviews + '}'
        release_date = steam_game.get('release_date').get('date')
        developer = steam_game.get('developers')[0]
        popular_tags = steam_spy.get('tags').keys() if len(steam_spy.get('tags')) > 0 else []
        popular_tags = valid_characteristics(clean_list(list(popular_tags)), validated_tags)
        game_details = map(lambda x: x.get('description'), steam_game.get('categories'))
        game_details = valid_characteristics(clean_list(list(game_details)), validated_game_details)
        languages = map(lambda x: x.strip(), steam_game.get('supported_languages').split(','))
        languages = clean_list(list(languages))
        languages = [language for language in languages if language.isalpha()]
        genres = map(lambda x: x.get('description'), steam_game.get('genres'))
        genres = valid_characteristics(clean_list(list(genres)), validated_genres)
        game_description = clean_html(steam_game.get('detailed_description'))
        mature_content = ''
        minimum_requirements = steam_game.get('pc_requirements').get('minimum')
        recommended_requirements = steam_game.get('pc_requirements').get('recommended')
        original_price = clean_price(steam_game.get('price_overview').get(
            'final_formatted')) if 'price_overview' in steam_game.keys() else 0
        discount_price = 0

        game = Game(
            steam_id=steam_id,
            url=url,
            name=name,
            desc_snippet=desc_snippet,
            reviews=reviews,
            release_date=release_date,
            developer=developer,
            popular_tags=json.dumps(popular_tags),
            game_details=json.dumps(game_details),
            languages=languages,
            genres=json.dumps(genres),
            game_description=game_description,
            mature_content=mature_content,
            minimum_requirements=minimum_requirements,
            recommended_requirements=recommended_requirements,
            original_price=original_price,
            discount_price=discount_price,
            score=0
        ).save()

        update_caracteristics(genres, popular_tags, game_details, languages)

        return game
    return game[0]
