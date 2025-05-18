import json
import pickle

def read_letters_from_file(file_path):

    try:
        with open(file_path, 'r') as file:
            content = file.read()
            abc = ''.join(char for char in content if char.isalpha())
            return abc
    except :
        print(f"Error: File {file_path} not found.")

def open_pickle_file(file_path : str) -> list:
    """
    input: the file name
    output: list of the words in the file
    The function try to open the file and if it is not exists if print an error
    """
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        exit()

def shift_letter(letter, K, abc ):
    """
    input: letter and number K
    output: shifted letter
    The function shift the letter by K in a cycle in the abc
    """
    if letter == ' ':
        return letter

    index = abc.index(letter)
    new_index = (index + K) % len(abc)

    return abc[new_index]

def decipher_phrase(phrase, lexicon_filename, abc_filename):
    """
    input: phrase, lexicon_filename, abc_filename
    output: phrase after decryption, code if it's decrypted write, and the K it's decrypted
    The function
    #################################################################################
    """
    print(f'starting deciphering using {lexicon_filename} and {abc_filename}')
    if len(phrase) == 0:
        return {"status": 0, "orig_phrase": phrase, "K": -1}
    abc = read_letters_from_file(abc_filename)
    data = open_pickle_file(lexicon_filename)

    for K in range(26):  # 0 - 25
        shifted_phrase = ""
        first_time = True
        for word in phrase.split():
            shifted_word = "".join(shift_letter(letter, K, abc) for letter in word)
            if shifted_word not in data:
                break

            if first_time:
                shifted_phrase += shifted_word
                first_time = False
            else:
                shifted_phrase += " " + shifted_word

        if len(shifted_phrase) == len(phrase):
            return {"status": 1, "orig_phrase": shifted_phrase, "K": K}

    return {"status": -1, "orig_phrase": phrase, "K": -1}

    # todo: due to possible difference in file encodings between operating systems, make sure to add
    #  utf8 encoding type when opening a file, as an example: with open(<file name>, 'r', encoding='utf8') as fin
    #  python developers plan to make utf8 a default at 3.15 - https://peps.python.org/pep-0686/

    result = {"status": 0, "orig_phrase": '', "K": -1}
    return result


# todo: fill in your student ids
students = {'id1': '314654484'}

if __name__ == '__main__':
    with open('config-decipher.json', 'r') as json_file:
        config = json.load(json_file)

    # note that lexicon.pkl is a serialized list of 10,000 most common English words
    result = decipher_phrase(config['secret_phrase'],
                             config['lexicon_filename'],
                             config['abc_filename'])

    assert result["status"] in {1, -1, 0}

    if result["status"] == 1:
        print(f'deciphered phrase: {result["orig_phrase"]}, K: {result["K"]}')
    elif result["status"] == -1:
        print("cannot decipher the phrase!")
    else:  # result["status"] == 0:
        print("empty phrase")
