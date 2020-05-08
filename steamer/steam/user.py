import requests

API_KEY = '7F2C968B4DD899E3D99D38201F6AD972'


def get_games_by_user(user_id):
    payload = {
        'key': API_KEY,
        'steamid': user_id,
        'format': 'json',
        'include_appinfo': 1
    }
    r = requests.get('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/', params=payload)
    if r.status_code == 200:
        print('OK')
        print(r.text)
        return r.text
    else:
        print('ERROR')
        print(r.text)
        return r.text


def get_friends_by_user(user_id):
    payload = {
        'key': API_KEY,
        'steamid': user_id,
        'format': 'json',
        'relationship': 'friend'
    }
    return requests.get('http://api.steampowered.com/ISteamUser/GetFriendList/v0001/', params=payload)
