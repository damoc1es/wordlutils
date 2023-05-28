import datetime
import requests
import shutil, os
import matplotlib.pyplot as plt


WORDS_LIST_LINK = 'https://raw.githubusercontent.com/tabatkins/wordle-list/main/words'


class ResultKey:
    GRAY = '_'
    YELLOW = 'Y'
    GREEN = 'G'

def result_to_colored_box(string):
    res = ""
    for c in string:
        match c:
            case ResultKey.GRAY:
                res += '⬛'
            case ResultKey.YELLOW:
                res += '🟨'
            case ResultKey.GREEN:
                res += '🟩'
            case _:
                res += c
    return res


class WordleGame:
    def __init__(self, date=None, solution=None, tries=None, results=None):
        self.green_chars: dict[int, str|None] = {1: None, 2: None, 3: None, 4: None, 5: None}
        self.yellow_chars = {1: "", 2: "", 3: "", 4: "", 5: ""}
        self.gray_chars = ""

        self.date = date
        self.solution = solution
        if tries is None:
            self.tries = []
        else: self.tries = tries
        
        if results is None:
            self.results = []
        else: self.results = results

    def add_try(self, word_tried: str, result: str) -> None:
        if len(word_tried) != len(result) or len(word_tried) != 5:
            raise Exception("Word length must be 5 and the result has to be the same length.")
        
        word_tried = word_tried.lower()
        
        self.tries.append(word_tried)

        if set(result) == ResultKey.GREEN:
            self.solution = word_tried
            return

        i = 0
        for c, t in zip(word_tried, result):
            i += 1
            
            match t:
                case ResultKey.GRAY:
                    if word_tried.count(c) == 1:
                        self.gray_chars += c
                    else:
                        for c2, t2 in zip(word_tried, result):
                            if c2 == c and t2 == ResultKey.GREEN:
                                self.yellow_chars[i] += c
                                break
                case ResultKey.YELLOW:
                    self.yellow_chars[i] += c
                case ResultKey.GREEN:
                    self.green_chars[i] = c
                case _:
                    raise Exception("Invalid result character found.")
    
    def __str__(self):
        s = f"{self.date} | {self.solution}"
        for r, t in zip(self.results, self.tries):
            s += f"\n{result_to_colored_box(r)} {t}"
        return s


class NerdleGame:
    def __init__(self, date=None, solution=None, tries=None, results=None):
        self.date = date
        self.solution = solution
        if tries is None:
            self.tries = []
        else: self.tries = tries
        
        if results is None:
            self.results = []
        else: self.results = results
    
    def __str__(self):
        s = f"{self.date} | {self.solution}"
        for r, t in zip(self.results, self.tries):
            s += f"\n{result_to_colored_box(r)} {t}"
        return s


class WordleSimulation:
    def __init__(self, winning_word):
        self.winning_word = winning_word.lower()
    
    def result(self, word):
        word = list(word.lower())
        winner = list(self.winning_word)
        res = [ResultKey.GRAY for _ in range(5)]

        for i, c in enumerate(word):
            if c == winner[i]:
                res[i] = ResultKey.GREEN
                word[i] = winner[i] = ResultKey.GRAY
        
        for i, c in enumerate(word):
            if c != ResultKey.GRAY and c in winner:
                res[i] = ResultKey.YELLOW
                word[i] = winner[winner.index(c)] = ResultKey.GRAY

        return "".join(res)


class NerdleSimulation:
    def __init__(self, winning_eq):
        self.winning_eq = winning_eq

    def result(self, guess):
        guess = list(guess)
        winner = list(self.winning_eq)
        res = [ResultKey.GRAY for _ in range(8)]

        for i, c in enumerate(guess):
            if c == winner[i]:
                res[i] = ResultKey.GREEN
                guess[i] = winner[i] = ResultKey.GRAY
        
        for i, c in enumerate(guess):
            if c != ResultKey.GRAY and c in winner:
                res[i] = ResultKey.YELLOW
                guess[i] = winner[winner.index(c)] = ResultKey.GRAY

        return "".join(res)


class Repository:
    def __init__(self, filename: str):
        self.filename = filename

    def store(self, date: datetime.date, tries: list[str], results: list[str], winning: str):
        line = f"{date.isoformat()},{' '.join(tries)},{' '.join(results)},{winning}\n"
        with open(self.filename, 'a') as file:
            file.write(line)

    def get(self, date, nerdle=False):
        result = []
        with open(self.filename, 'r') as file:
            result = file.readlines()
        
        if date != None:
            result = [x.strip() for x in result if x.split(',')[0] == str(date)]
        else: result = [result[-1].strip()]
        
        if len(result) == 0:
            return None
        
        s = result[0].split(',')
        if nerdle:
            return NerdleGame(s[0], s[3], s[1].split(), s[2].split())
        return WordleGame(s[0], s[3], s[1].split(), s[2].split())
    
    def get_all(self, nerdle=False):
        result = []
        with open(self.filename, 'r') as file:
            result = file.readlines()
        
        if nerdle:
            return [NerdleGame(x.split(',')[0], x.split(',')[3], x.split(',')[1].split(), x.split(',')[2].split()) for x in result]
        return [WordleGame(x.split(',')[0], x.split(',')[3], x.split(',')[1].split(), x.split(',')[2].split()) for x in result]
    
    def backup(self, date: datetime.datetime):
        filename, file_extension = os.path.splitext(self.filename)
        backup_file = f"{filename}_{date.strftime('%Y%m%d-%H%M%S')}{file_extension}"
        shutil.copy2(self.filename, backup_file)
        return backup_file


class Controller:
    def __init__(self, repo, nerdle_repo, all_words_source=WORDS_LIST_LINK):
        self.repo = repo
        self.nerdle_repo = nerdle_repo
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

        for y in yellows.values(): # yellow
            if y != "":
                filtered = list(filter(lambda x: all([c in x for c in y]), filtered))
        
        filtered = list(filter(lambda x: all([True if greens[i+1] is None else x[i] == greens[i+1] for i in range(5)]), filtered)) # green

        return filtered

    def store(self, tries, winning, nerdle=False):
        date = datetime.date.today()
        if not nerdle:
            simulation = WordleSimulation(winning)
        else: simulation = NerdleSimulation(winning)

        results = [simulation.result(word) for word in tries]
        tries = [w.upper() for w in tries]
        if not nerdle:
            self.repo.store(date, tries, results, winning.upper())
        else: self.nerdle_repo.store(date, tries, results, winning.upper())
    
    def get_game(self, date=None):
        return self.repo.get(date)
    
    def get_nerdle(self, date=None):
        return self.nerdle_repo.get(date, nerdle=True)
    
    def backup(self):
        return self.repo.backup(datetime.datetime.now())
    
    def get_stats(self, nerdle=False):
        dates = []
        scores = []
        if not nerdle:
            games = self.repo.get_all()
        else:
            games = self.nerdle_repo.get_all(nerdle)
        for game in games:
            dates.append(game.date)

            score = len(game.results)
            if set(game.results[-1]) != set([ResultKey.GREEN]):
                score += 1
            scores.append(score)
        
        return dates, scores


class CLI:
    BOLD = '\033[1m'
    END = '\033[0m'

    def __init__(self, controller: Controller):
        self.srv = controller
    
    def print_menu(self):
        print("--- Available commands ---")
        print(f"{CLI.BOLD}checker{CLI.END} - start game for checking possibilities")
        print(f"{CLI.BOLD}save{CLI.END} - save already completed game")
        print(f"{CLI.BOLD}get{CLI.END} - look up a saved game by date")
        print(f"{CLI.BOLD}stats{CLI.END} - get a plot of stats for all games")
        print(f"{CLI.BOLD}save nerdle{CLI.END} - save already completed nerdle game")
        print(f"{CLI.BOLD}get nerdle{CLI.END} - look up a saved nerdle game by date")
        print(f"{CLI.BOLD}stats nerdle{CLI.END} - get a plot of stats for all nerdle games")
        print(f"{CLI.BOLD}backup{CLI.END} - backup saves to timestamped file")
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
                    if len(word) != 5:
                        print("Word length must be 5.")
                        continue
                    result = input(f"Enter result (gray '{ResultKey.GRAY}', yellow '{ResultKey.YELLOW}', green '{ResultKey.GREEN}'):\n")
                    try:
                        self.srv.add_try(word, result)
                        print("ADDED TRY\n")
                    except Exception as e:
                        print(e)

    def save_menu(self):
        print("-- Enter winning word or CANCEL to exit")
        winning = input().lower()
        match winning:
            case 'cancel':
                return
            case _:
                if len(winning) != 5:
                    print("Word length must be 5.")
                    return
                print("-- Enter the words or CANCEL to exit")
                tries = []
                i = 0
                while i < 6:
                    word = input().lower()
                    if word == 'cancel':
                        return
                    if len(word) != 5:
                        print("Word length must be 5.")
                        continue
                    if word == winning:
                        tries.append(winning)
                        break
                    if word.strip() == '':
                        break
                    tries.append(word)
                    i += 1
        
        self.srv.store(tries, winning)
        print("GAME SAVED")

    def get_nerdle_menu(self):
        print("-- Enter date (YEAR-MONTH-DAY), empty to get the last one, or EXIT to exit")
        date_str = input()
        if date_str in ("EXIT", "exit"):
            return
        if date_str == "":
            try:
                game = self.srv.get_nerdle()
                print(game)
            except:
                print("NO SAVED NERDLE GAME")
        else:
            try:
                date = datetime.date.fromisoformat(date_str)
                game = self.srv.get_nerdle(date)
                print(game)
            except:
                print("INVALID DATE FORMAT")
    
    def get_menu(self):
        print("-- Enter date (YEAR-MONTH-DAY), empty to get the last one, or EXIT to exit")
        date_str = input()
        if date_str in ("EXIT", "exit"):
            return
        if date_str == "":
            try:
                game = self.srv.get_game()
                print(game)
            except:
                print("NO SAVED NERDLE GAME")
        else:
            try:
                date = datetime.date.fromisoformat(date_str)
                game = self.srv.get_game(date)
                print(game)
            except:
                print("INVALID DATE FORMAT")

    def save_nerdle_menu(self):
        print("-- Enter winning equation or CANCEL to exit")
        winning = input().lower()
        match winning:
            case 'cancel':
                return
            case _:
                if len(winning) != 8:
                    print("Length must be 8.")
                    return
                print("-- Enter the equations or CANCEL to exit")
                tries = []
                i = 0
                while i < 6:
                    equation = input().lower()
                    if equation == 'cancel':
                        return
                    if len(equation) != 8:
                        print("Length must be 8.")
                        continue
                    if equation == winning:
                        tries.append(winning)
                        break
                    if equation.strip() == '':
                        break
                    tries.append(equation)
                    i += 1
        
        self.srv.store(tries, winning, nerdle=True)
        print("GAME SAVED")

    def stats_menu(self, nerdle=False):
        dates, scores = self.srv.get_stats(nerdle)

        for score in sorted(set(scores)):
            times = scores.count(score)
            if times == 1:
                word = "game"
            else: word = "games"

            if score == 7:
                print(f"not guessed: {scores.count(score)} {word}")
            else: print(f"guessed in {score} tries: {scores.count(score)} {word}")
        print()

        plt.plot(scores)
        plt.yticks(range(max(min(scores)-1, 1), 8))
        plt.ylabel("Tries")
        plt.xlabel("Game Number")
        plt.show()

    def start(self):
        while True:
            self.print_menu()
            cmd = input("\nCommand: ")
            match cmd.lower():
                case 'checker':
                    self.checker_menu()
                case 'save':
                    self.save_menu()
                case 'save nerdle':
                    self.save_nerdle_menu()
                case 'get':
                    self.get_menu()
                case 'get nerdle':
                    self.get_nerdle_menu()
                case 'backup':
                    print(f"Backup made to '{self.srv.backup()}'")
                case 'exit':
                    break
                case 'stats':
                    self.stats_menu()
                case 'stats nerdle':
                    self.stats_menu(True)
                case _:
                    print("Invalid command.")


if __name__ == '__main__':
    ui = CLI(Controller(Repository("data/wordles.csv"), Repository("data/nerdles.csv")))
    ui.start()
