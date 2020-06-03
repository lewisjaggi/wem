import requests

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
        return r.text
    else:
        return r.text


def get_friends_by_user(user_id):
    payload = {
        'key': API_KEY,
        'steamid': user_id,
        'format': 'json',
        'relationship': 'friend'
    }
    return requests.get('http://api.steampowered.com/ISteamUser/GetFriendList/v0001/', params=payload)
