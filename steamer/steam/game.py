from steamer.database.db import Game


def get_game_details_by_id(game_id):
    game = [game for game in Game.objects() if game.id == game_id]
    if len(game) == 0:
        return '{"toto": "toto"}'
    else:
        return game[0].json()
