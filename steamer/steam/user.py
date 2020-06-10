import requests
import json

API_KEY = '22F49C23A2F2EE53D628F6DB3228515E'


def get_games_by_user(user_id):
    payload = {
        'key': API_KEY,
        'steamid': user_id,
        'format': 'json',
        'include_appinfo': 1
    }
    r = requests.get('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/', params=payload)
    if r.status_code == 200:
        text = r.text
        text_json = json.loads(text)
        if "games" in text_json["response"].keys():
            return text_json["response"]["games"]

    return []


def get_friends_by_user(user_id):
    payload = {
        'key': API_KEY,
        'steamid': user_id,
        'format': 'json',
        'relationship': 'friend'
    }
    resp = requests.get('http://api.steampowered.com/ISteamUser/GetFriendList/v0001/', params=payload)
    users_list = resp.json()["friendslist"]["friends"]
    return [user["steamid"] for user in users_list]

