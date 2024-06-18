from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import random

def create_app():
    app_instance = Flask(__name__, static_folder='static')
    CORS(app_instance, origins=["https://safariguessinggame.online/"], supports_credentials=True)

    @app_instance.route('/')
    def index():
        return app_instance.send_static_file('index.html')

    return app_instance

app = create_app()

word_bank = ['lion', 'leopard', 'giraffe', 'elephant', 'hippo', 'cheetah', 'rhino', 'zebra', 'gorilla', 'baboon', 'monkey', 'gazelle', 'buffalo', 'hyena', 'crane', 'snake', 'warthog']
num_turns = 5

def generate_hint(word, incorrect_letter, correct_guesses):
    hint = ''.join([letter if letter in correct_guesses else '_' for letter in word])
    return hint

def start_new_game():
    global turns_played, incorrect_word, incorrect_letter, word_to_guess, correct_guesses
    turns_played = 0
    incorrect_word = []
    incorrect_letter = []
    word_to_guess = random.choice(word_bank)
    correct_guesses = []

start_new_game()

@app.route('/app/start_game', methods=['GET'])
def start_game():
    start_new_game()
    response = {
        "message": "New game started!",
        "num_turns": num_turns,
        "word_length": len(word_to_guess)
    }
    return jsonify(response)

@app.route('/app/make_guess', methods=['OPTIONS', 'POST'])
@cross_origin(origin='https://safariguessinggame.online/', supports_credentials=True)
def handle_make_guess():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': 'https://safariguessinggame.online/',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Credentials': 'true',
        }
        return '', 200, headers

    elif request.method == 'POST':
        global turns_played, incorrect_word, incorrect_letter, word_to_guess, correct_guesses
        data = request.get_json()
        guess = data.get('guess').lower()

        if guess == word_to_guess:
            correct_guesses.extend(set(guess))
            hint = generate_hint(word_to_guess, incorrect_letter, correct_guesses)
            response = {
                "incorrect_word": incorrect_word,
                "turns_remaining": num_turns - turns_played,
                "game_over": False,
                "correct_guess": True,
                "hint": generate_hint(word_to_guess, incorrect_letter, correct_guesses)
            }
        else:
            incorrect_word.append(guess)
            incorrect_letter.extend(set(guess))
            correct_guesses.extend(set(guess))
            hint = generate_hint(word_to_guess, incorrect_letter, correct_guesses)
            response = {
                "incorrect_letter": ' '.join(incorrect_letter),
                "incorrect_word": ' '.join(incorrect_word),
                "turns_remaining": num_turns - turns_played,
                "game_over": turns_played == num_turns,
                "correct_guess": False,
                "hint": hint,
            }

        turns_played += 1

        response = {
            "incorrect_letter": incorrect_letter,
            "incorrect_word": incorrect_word,
            "turns_remaining": num_turns - turns_played,
            "game_over": turns_played == num_turns,
            "correct_guess": guess == word_to_guess,
            "hint": hint
        }

        return jsonify(response)

if __name__ == '__main__':
    app.run()
