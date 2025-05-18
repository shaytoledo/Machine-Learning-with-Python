import json
def open_file(filename):
    """
    input: the file name
    output: the lines of the file
    The function try to open the file and if it is not exists if print an error
    """
    try:
        with open(filename, 'r', encoding='utf8') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        exit()

def final_winner(result):
    """
    input: the dic with the result of all the games
    output: the winner of the game or tie
    the function check in the dictionary how is the winner of the game
    """
    best_player = max(result, key=result.get)
    best_player_res = result[best_player]
    del result[best_player]
    second_best_player = max(result, key=result.get)
    second_best_player_res = result[second_best_player]

    if second_best_player_res == best_player_res: return "tie"
    else: return best_player

def how_win(name1, res1, name2, res2):
    """
    input: the names of the players in the current position and what they chose
    output: the winner of the game or none for tie
    The function returns the winner of the current position according to the rules of the game
    """
    rules = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

    if res1 == res2:
        return None

    if rules[res1] == res2:
        return name1
    else:
        return name2

def check_names_in_dict(name1, name2, results):
    """
    input: the names of the players in the current position
    output: the dictionary with the names
    check if the names already exist in the dictionary and if they are not lucrative them in
      """
    if name1 not in results:
        results[name1] = 0

    if name2 not in results:
        results[name2] = 0

def game(results_filename):
    """
    input: the file of the results of all the games
    output: the winner of the game or none for tie
    The function open the file and read line by line and check how the winner in each game, lucrative the result in dictionary
    and after the lines down it gets the final winner of the game or a tie
    """

    print(f'starting the game with {results_filename}')

    lines = open_file(results_filename)
    result = dict()

    for index, line in enumerate(lines):
        if index == 0: continue

        words = line.split()
        player1, player1_res, player2, player2_res = words[0], words[1], words[2], words[3]
        winner = how_win(player1, player1_res, player2, player2_res)
        check_names_in_dict(player1, player2, result)
        if winner is not None: result[winner] += 1

    return final_winner(result)




    #  todo: due to possible difference in file encodings between operating systems, you may need to add
    #  utf8 encoding type when opening a file, as an example: with open(<file name>, 'r', encoding='utf8') as fin
    #  python developers plan to make utf8 a default at 3.15 - https://peps.python.org/pep-0686/


students = {'id1': '314654484'}

if __name__ == '__main__':
    with open('config-rps.json', 'r') as json_file:
        config = json.load(json_file)

    winner = game(config['results_filename'])
    print(f'the winner is: {winner}')