import json
from scrapers import get_quote_data, get_song_data
from config import db
import spacy

class MadLib(db.Model):
    __tablename__ = 'madlib'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(30), unique=True, nullable=False)
    type = db.Column(db.String(30), unique=False, nullable=True)
    category = db.Column(db.String(30), unique=False, nullable=True)
    title = db.Column(db.String(100), unique=False, nullable=True)
    creator = db.Column(db.String(100), unique=False, nullable=True)
    content = db.Column(db.String(300), unique=False, nullable=True)
    pos_replace_list = db.Column(db.String(300), unique=False, nullable=True)

    def __init__(self, game_id):
        super(MadLib, self).__init__(game_id=game_id)
        self.nlp = spacy.load('en_core_web_trf')

    def update_game_data(self, type, category):
        self.type = type
        self.category = category
        data = get_quote_data(self.category) if self.type == 'quote' else get_song_data(self.category)
        self.title = data['title']
        self.creator = data['creator']
        pos_replace_dict = {}
        text = ''
        if self.type == 'quote':
            text = self.nlp(data['content'])
            line = str(data['content'])
            print(line)
            for index, token in enumerate(text):
                if (not x in token.text for x in ['PROPN', 'VERB', 'NOUN', 'ADJ', 'ADV', 'NUM']) and token.pos_ in ['PROPN', 'VERB', 'NOUN', 'ADJ', 'ADV', 'NUM']:
                    ending = '_' + str(index)
                    if token.pos_ == 'NOUN' and token.text[len(token.text)-1] == 's':
                        ending = '_PLUR' + ending
                    try:
                        if token.pos_ == 'VERB' and token.text[len(token.text)-1].lower() == 's':
                            ending = '_S' + ending
                        elif token.pos_ == 'VERB' and token.text[len(token.text)-3:len(token.text)].lower() == 'ing':
                            ending = '_ING' + ending
                    except:
                        ending
                    placeholder = token.pos_ + ending
                    pos_replace_dict.update({placeholder : ''})
                    line = line.replace(' ' + token.text + ' ', ' ' + placeholder + ' ')
            self.content = line
            self.pos_replace_list = json.dumps(pos_replace_dict, indent=4)
        if self.type == 'song':
            content = ''
            for index1 in range(0, len(data['content'])):
                text = self.nlp(data['content'][index1])
                line = data['content'][index1]
                for index2, token in enumerate(text):
                    if (not x in token.text for x in ['PROPN', 'VERB', 'NOUN', 'ADJ', 'ADV', 'NUM']) and token.pos_ in ['PROPN', 'VERB', 'NOUN', 'ADJ', 'ADV', 'NUM']:
                        ending = '_' + str(index1) + str(index2)
                        if token.pos_ == 'NOUN' and token.text[len(token.text)-1] == 's':
                            ending = '_PLUR' + ending
                        try:
                            if token.pos_ == 'VERB' and token.text[len(token.text)-1].lower() == 's':
                                ending = '_S' + ending
                            elif token.pos_ == 'VERB' and token.text[len(token.text)-3:len(token.text)].lower() == 'ing':
                                ending = '_ING' + ending
                        except:
                            ending
                        placeholder = token.pos_ + ending
                        pos_replace_dict.update({placeholder : ''})
                        line = line.replace(' ' + token.text + ' ', ' ' + placeholder + ' ')
                    content = content + line
            self.content = content
            self.pos_replace_list = json.dumps(pos_replace_dict, indent=4)

    def as_json(self):
        return {
            'type' : self.type,
            'category' : self.category,
            'title' : self.title,
            'creator' : self.creator,
            'content' : self.content,
            'pos_replace_list' : self.pos_replace_list
        }
    
class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('madlib.id'), nullable = False)
    game = db.relationship('MadLib', backref=db.backref('players', lazy=True))
    display_name = db.Column(db.String(50), unique = True, nullable = False)
    display_color = db.Column(db.String(20), unique = False, nullable = False)


    def as_json(self):
        return json.dumps({
            'type' : self.type,
            'category' : self.category,
            'title' : self.title,
            'creator' : self.creator,
            'content' : self.content,
            'pos_replace_list' : self.pos_replace_list
        }, indent=4)