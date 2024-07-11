import random
from config import app, db, request, jsonify
from lists import adj_list, animal_list, color_list
from databases import MadLib, Player
from pprint import pprint

@app.route("/create-game", methods=['POST']) 
def create_game():
    code = request.json.get('game_code')
    open_games = MadLib.query.all()
    for open_game in open_games:
        if open_game.game_id == code:
            return jsonify({'error' : 403})
    game = MadLib(code)
    player = Player(game_id=game.id, display_name=random.choice(adj_list).capitalize() + random.choice(animal_list), display_color= random.choice(color_list))
    db.session.add(game)
    db.session.add(player)
    db.session.commit()
    return jsonify({})
    
@app.route("/join-game", methods=['POST']) 
def join_game():
    code = request.json.get('game_code')
    open_games = MadLib.query.all()
    for open_game in open_games:
        if open_game.game_id == code:
            player = Player(game_id=open_game.id, display_name=random.choice(adj_list).capitalize() + random.choice(animal_list), display_color= random.choice(color_list))
            db.session.add(player)
            db.session.commit()
            return jsonify({'users' : open_game.players})
    return jsonify({'error' : 403})

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    # app.run(debug=True, port=5000)
    game = MadLib('')
    game.update_game_data('quote', 'death')
    pprint(game.as_json())

