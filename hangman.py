import json
import random
import requests
import string
import time

class Game:
    def __init__(self, answer, hangmen):
        self.answer = answer
        self.guesses = set()
        self.hangmen = hangmen

    def status(self):
        if set(self.answer).issubset(self.guesses):
            return 'won'
        elif len(self.guesses - set(self.answer)) >= len(self.hangmen) - 1:
            return 'lost'
        else:
            return 'ongoing'

    def draw(self, fancy = False):
        correct = self.guesses & set(self.answer)
        incorrect = self.guesses - set(self.answer)

        out = self.hangmen[len(incorrect)]
        out += '\n\n\033[30;47m'

        for letter in string.ascii_lowercase:
            if letter in correct:
                out += '\033[102m'
            elif letter in incorrect: 
                out += '\033[101m'

            out += f' {letter} \033[47m'
            out += '\n' if letter == 'm' else ''

        out += '\033[0m\n\n'
        out += ' '.join([letter if letter in self.guesses else '_' for letter in self.answer])

        clear_screen()
        if not fancy:
            print(f'{out}\n')
        else:
            for line in out.split('\n'):
                print(line)
                time.sleep(0.05)

def get_entry(word):
    return json.loads(requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}').text)

def has_definition(entry):
    return not ('title' in entry and entry['title'] == 'No Definitions Found')
                
def draw_entry(entry):
    out = f'\033[1m{entry["word"].capitalize()}\033[0m\n'
    if 'phonetic' in entry:
        out += f'\033[37m{entry["phonetic"]}\033[0m\n'
    out += '\n'

    for index_a, meaning_a in enumerate(entry['meanings']):
        for relative_index, meaning_b in enumerate(entry['meanings'][index_a + 1:]):
            if meaning_a['partOfSpeech'] == meaning_b['partOfSpeech']:
                entry['meanings'].pop(index_a + relative_index + 1)

    for meaning in entry['meanings']:
        out += f'\033[4m{meaning["partOfSpeech"].capitalize()}\033[0m\n\n'
        for definition in meaning['definitions']:
            out += f'     - {definition["definition"].capitalize()}\n'
            if 'example' in definition:
                out += f'\n      \033[3m\033[37m"{definition["example"].capitalize()}"\033[0m\n'
            if definition['synonyms']:
                out += '\n      Synonyms\n'

                for synonym in definition['synonyms']:
                    out += f'          \033[37m- "{synonym}"\033[0m\n' 
            if definition['antonyms']:
                out += '\n      Antonyms\n'

                for antonym in definition['antonyms']:
                    out += f'          \033[37m- "{antonym}"\033[0m\n'
            out += '\n'

    out += f'\033[4mSources\033[0m\n\n'
    for source in entry['sourceUrls']:
        out += f'    \033[37m  {source}\033[0m\n'

    print(out)

def clear_screen():
    print('\033[1J\033[H', end = '')

def main():
    words = set(open('words.txt', 'r').read().splitlines())
    hangmen = open('hangmen.txt', 'r').read().split('\n\n')
    end_text = open('endtext.txt', 'r').read().split('\n\n')

    clear_screen()
    single_player = input('Have the computer pick a random word? [Y/n] ').lower() != 'n'

    if single_player:
        answer = list(words)[random.randrange(len(words))]
        entry = get_entry(answer)

        while not has_definition(entry):
            answer = list(words)[random.randrange(len(words))]
            entry = get_entry(answer)
    else:
        clear_screen()
        answer = input('Target word: ').lower()
        entry = get_entry(answer)
    
        while answer not in words or not has_definition(entry):
            clear_screen()
            input('Please enter a valid English word\n\n\033[37mPress Enter to continue...\033[0m')

            clear_screen()
            answer = input('Target word: ')
            entry = get_entry(answer)
     
    entry = entry[0]

    game = Game(answer, hangmen)
    game.draw(fancy = True)

    while game.status() == 'ongoing':
        guess = input('\nNext guess: ').lower()

        while len(guess) != 1 or guess not in string.ascii_lowercase or guess in game.guesses:
            clear_screen()
            input('Please enter a single unguessed character (a-z)\n\n\033[37mPress Enter to continue...\033[0m')

            game.draw()
            guess = input('Next guess: ').lower()

        game.guesses.add(guess)
        game.draw(fancy = True)

    time.sleep(2)
    clear_screen()

    if game.status() == 'won':
        print(end_text[0])
    elif game.status() == 'lost':
        print(end_text[1])

    time.sleep(2)
    clear_screen()

    draw_entry(entry)
     
    input('\033[37mPress Enter to exit...\033[0m')
    clear_screen()

if __name__ == '__main__':
    main()
