import datetime
import requests

WORDS_LIST_LINK = 'https://raw.githubusercontent.com/tabatkins/wordle-list/main/words'


class WordleGame:
    def __init__(self, gray_key="_", yellow_key="Y", green_key="G"):
        self.gray_key = gray_key
        self.yellow_key = yellow_key
        self.green_key = green_key

        self.green_chars = {1: None, 2: None, 3: None, 4: None, 5: None}
        self.yellow_chars = {1: "", 2: "", 3: "", 4: "", 5: ""}
        self.gray_chars = ""
        self.solution = None

    def add_try(self, word_tried: str, result: str) -> None:
        if len(word_tried) != len(result) or len(word_tried) != 5:
            raise Exception("Word length must be 5 and the result has to be the same length.")
        
        word_tried = word_tried.lower()

        if set(result) == self.green_key:
            self.solution = word_tried
            return

        i = 0
        for c, t in zip(word_tried, result):
            i += 1
            match t:
                case self.gray_key:
                    if word_tried.count(c) == 1:
                        self.gray_chars += c
                    else: self.yellow_chars[i] += c
                case self.yellow_key:
                    self.yellow_chars[i] += c
                case self.green_key:
                    self.green_chars[i] = c
                case _:
                    raise Exception("Invalid result character found.")


class WordleSimulation():
    def __init__(self, winning_word, gray_key="_", yellow_key="Y", green_key="G"):
        self.gray_key = gray_key
        self.yellow_key = yellow_key
        self.green_key = green_key

        self.winning_word = winning_word.lower()
    
    def result(self, word):
        word = list(word.lower())
        winner = list(self.winning_word)
        res = [self.gray_key for _ in range(5)]

        for i, c in enumerate(word):
            if c == winner[i]:
                res[i] = self.green_key
                word[i] = winner[i] = self.gray_key
        
        for i, c in enumerate(word):
            if c != self.gray_key and c in winner:
                res[i] = self.yellow_key
                word[i] = winner[winner.index(c)] = self.gray_key

        return "".join(res)


class Repository:
    def __init__(self, filename: str):
        self.filename = filename

    def store(self, date: datetime.date, tries: list[str], results: list[str], winning: str):
        line = f"{date.isoformat()},{' '.join(tries)},{' '.join(results)},{winning}\n"
        with open(self.filename, "a") as file:
            file.write(line)

    def get(self, date):
        pass


class Controller:
    def __init__(self, repo, all_words_source=WORDS_LIST_LINK):
        self.repo = repo
        self.game = None
        r = requests.get(all_words_source)
        self.all_words = r.text.split('\n')


    def start_game(self):
        self.game = WordleGame()
    
    def add_try(self, word_tried: str, result: str):
        if self.game is None:
            raise Exception("Game not started.")
        self.game.add_try(word_tried, result)

    def get_possible_solutions(self):
        if self.game is None:
            raise Exception("Game not started.")
        
        grays = self.game.gray_chars
        yellows = self.game.yellow_chars
        greens = self.game.green_chars

        filtered = list(filter(lambda x: len(set(x) & set(grays)) == 0, self.all_words)) # gray
        filtered = list(filter(lambda x: all([x[i] not in yellows[i+1] for i in range(5)]), filtered)) # yellow
        filtered = list(filter(lambda x: all([True if greens[i+1] is None else x[i] == greens[i+1] for i in range(5)]), filtered)) # green

        return filtered

    def store(self, tries, winning):
        date = datetime.date.today()
        simulation = WordleSimulation(winning)
        results = [simulation.result(word) for word in tries]
        tries = [w.upper() for w in tries]
        self.repo.store(date, tries, results, winning.upper())


class CLI:
    BOLD = '\033[1m'
    END = '\033[0m'

    def __init__(self, controller: Controller):
        self.srv = controller
    
    def print():
        print("--- Available commands ---")
        print(f"{CLI.BOLD}checker{CLI.END} - start game for checking possibilities")
        print(f"{CLI.BOLD}save{CLI.END} - save already completed game")
        # print(f"{CLI.BOLD}backup{CLI.END} - backup saves to timestamped file")
        print(f"{CLI.BOLD}exit{CLI.END} - quit")

    def checker_menu(self):
        self.srv.start_game()

        while True:
            print("-- Enter word, EXIT, or leave empty and enter to return possible solutions")
            word = input()
            match word.lower():
                case 'exit':
                    return
                case '':
                    print("-- POSSIBLE SOLUTIONS --")
                    for solution in self.srv.get_possible_solutions():
                        print(solution.upper())
                    print()
                case _:
                    result = input("Enter result: ")
                    self.srv.add_try(word, result)
                    print("ADDED TRY\n")

    def save_menu(self):
        print("-- Enter winning word or CANCEL to exit")
        winning = input().lower()
        match winning:
            case 'cancel':
                return
            case _:
                print("-- Enter the words or empty to exit")
                tries = []
                for _ in range(6):
                    word = input().lower()
                    if word == winning:
                        tries.append(winning)
                        break
                    if word.strip() == '':
                        break
                    tries.append(word)
        
        self.srv.store(tries, winning)
        print("GAME SAVED")

    def start(self):
        while True:
            CLI.print()
            cmd = input("\nCommand: ")
            match cmd.lower():
                case 'checker':
                    self.checker_menu()
                case 'save':
                    self.save_menu()
                case 'exit':
                    break
                case _:
                    print("Invalid command.")


if __name__ == '__main__':
    ui = CLI(Controller(Repository("data/wordles.txt")))
    ui.start()
