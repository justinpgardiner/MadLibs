import json
import requests
import random
from bs4 import BeautifulSoup, Tag, NavigableString

custom_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9'
}

def get_song_data_json():
    temp_song_data = {}
    unformatted = list(map(lambda x: x.strip(), list(open('unformatted-song-data.txt', 'r'))))
    iterator = iter(unformatted)
    genre = ''
    adder = -100
    while True:
        line = next(iterator, None)
        if line is None:
            break
        if line in ['Pop', 'Rap', 'Rock', 'Country']:
            genre = line
            adder = adder + 100
            continue
        try: 
            id = int(line) + adder
        except:
            id = int(next(iterator)) + adder
        title = next(iterator)
        trash = next(iterator)
        artist = next(iterator)
        trash = next(iterator)
        link_back = artist.replace(' ', '-').replace('&', 'and').replace('.', '').capitalize() + '-' + title.replace(' ', '-').replace('&', 'and').replace('.', '').lower() + '-lyrics'
        temp_song_data.update({str(id) : {'genre': genre, 'title': title, 'artist': artist, 'link': 'https://genius.com/' + link_back}})
    final_song_data = {}
    index_valid_links = 0
    print('making requests...')
    for i in range(1, 401):
        req = requests.get(temp_song_data[str(i)]["link"])
        if req.status_code == 200:
            print(temp_song_data[str(i)])
            final_song_data.update({str(index_valid_links) : temp_song_data[str(i)]})
            index_valid_links = index_valid_links + 1 
        else :
            continue
    with open('song-data.json', 'w', encoding='utf-8') as f:
        json.dump(final_song_data, f, ensure_ascii=False, indent=4)

def get_song_data(genre):
    index = -1
    if genre == 'Pop':
        index = random.randint(0, 69)
    elif genre == 'Rap':  
        index = random.randint(69, 142)
    elif genre == 'Rock':  
        index = random.randint(142, 218)
    else:
        index = random.randint(218, 285)
    song_data = {}
    with open('song-data.json', 'r') as f:
        fjson = json.load(f)
        song_data = fjson[str(index)]
    req = requests.get(song_data['link'], headers=custom_headers)
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, 'html.parser')
        lyrics = ''
        for div in soup.find_all(class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL'):
            for tag in div.descendants:
                if type(tag) == NavigableString:
                    lyrics = lyrics + tag
                elif tag.name == 'br':
                    lyrics = lyrics + '\n'
        lyrics_list = lyrics.split('\n')
        section_starting_indecies = []
        for i in range(0, len(lyrics_list) - 1):
            if '[' in lyrics_list[i]:
                section_starting_indecies.append(i)
        section = []
        while len(section) == 0:
            start_index = random.choice(range(0, len(section_starting_indecies)))
            for i in range(section_starting_indecies[start_index], len(lyrics_list) - 1 if section_starting_indecies[start_index + 1] >= len(lyrics_list) else section_starting_indecies[start_index + 1]):
                if not lyrics_list[i] == '':
                    section.append(lyrics_list[i]) 
        # print(lyrics_list)
        song_data.update({'content': section[1:], 'title': song_data['title'] + ' (' + section[0].replace('[', '').replace(']', '') + ')'})
        return song_data
    else:
        return {'Error' : req.status_code}


def get_quote_data(cat):
    url = 'https://www.goodreads.com/quotes/tag/'+ cat + '?page=' + str(random.randint(1, 51))
    req = requests.get(url=url, headers=custom_headers)
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, 'html.parser')
        quote_children = list(random.choice(soup.find_all(class_='quoteText')).descendants)
        content = quote_children[0].text.strip()
        author = 'Anonymous' if quote_children[3].text.strip() == '' else quote_children[3].text.strip()
        category = cat.capitalize()
        title = category + ' Quote'
        return {'title': title, 'category': category, 'creator': author, 'content': content, 'link': url}
    else:
        return {'Error' : req.status_code}
