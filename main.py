from wordle import *
from nerdle import *
from repo import Repository, RepositoryDb, csv_to_db
from utils import GameType
import matplotlib.pyplot as plt
import tomllib


class CLI:
    BOLD = '\033[1m'
    END = '\033[0m'

    def __init__(self, word_ctrl, nerd_ctrl):
        self.word_ctrl = word_ctrl
        self.nerd_ctrl = nerd_ctrl
        self.game = GameType.NONE
    
    def print_menu(self):
        if self.game is GameType.NONE:
            print("--- Choose ---")
            print(f"{CLI.BOLD}wordle{CLI.END}")
            print(f"{CLI.BOLD}nerdle{CLI.END}")
            print(f"{CLI.BOLD}exit{CLI.END}")
        else:
            print(f"--- MENU [{self.game.name}]---")
            if self.game != GameType.NERDLE:
                print(f"{CLI.BOLD}checker{CLI.END} - start game for checking possibilities")
            print(f"{CLI.BOLD}save{CLI.END} - save already completed game")
            print(f"{CLI.BOLD}get{CLI.END} - look up a saved game by date")
            print(f"{CLI.BOLD}stats{CLI.END} - get a plot of stats for all games")
            print(f"{CLI.BOLD}backup{CLI.END} - backup saves to timestamped file")
            print(f"{CLI.BOLD}exit{CLI.END} - quit")
    
    def checker_menu(self):
        self.word_ctrl.start()

        while True:
            print("-- Enter word, EXIT, or leave empty and enter to return possible solutions")
            word = input()
            match word.lower():
                case 'exit':
                    return
                case '':
                    print("-- POSSIBLE SOLUTIONS --")
                    for solution in self.word_ctrl.get_possible_solutions():
                        print(solution.upper())
                    print()
                case _:
                    result = input(f"Enter result (gray '{ResultKey.GRAY}', yellow '{ResultKey.YELLOW}', green '{ResultKey.GREEN}'):\n")
                    try:
                        self.word_ctrl.add_try(word, result)
                        print("ADDED TRY\n")
                    except Exception as e:
                        print(e)
    
    def save_menu(self):
        print("-- Enter the solution or CANCEL to exit")
        length_try = 5
        if self.game == GameType.NERDLE:
            length_try = 8
        winning = input().lower()
        match winning:
            case 'cancel':
                return
            case _:
                if len(winning) != length_try:
                    print(f"Length must be {length_try}.")
                    return
                print("-- Enter the tries or CANCEL to exit")
                tries = []
                i = 0
                while i < 6:
                    word = input().lower()
                    if word == 'cancel':
                        return
                    if len(word) != length_try:
                        print(f"Length must be {length_try}.")
                        continue
                    if word == winning:
                        tries.append(winning)
                        break
                    if word.strip() == '':
                        break
                    tries.append(word)
                    i += 1
        
        match self.game:
            case GameType.WORDLE:
                simulation = WordleSimulation(winning)
                results = [simulation.result(word) for word in tries]
                game = WordleGame(datetime.date.today(), tries, results, winning)
                self.word_ctrl.store(game)
            case GameType.NERDLE:
                simulation = NerdleSimulation(winning)
                results = [simulation.result(word) for word in tries]
                game = NerdleGame(datetime.date.today(), tries, results, winning)
                self.nerd_ctrl.store(game)
            case _:
                print("No game chosen.") # should never happen
                return
        print("GAME SAVED")

    def get_menu(self, ctrl):
        print("-- Enter date (YEAR-MONTH-DAY) or leave empty to get the last one")
        date_str = input()
        if date_str in ("EXIT", "exit"):
            return
        if date_str == "":
            game = ctrl.get()
            if game is None:
                print("No game saved.")
            else: print(game)
        else:
            try:
                date = datetime.date.fromisoformat(date_str)
                game = ctrl.get(date)
                if game is None:
                    print("No game saved for that date.")
                else: print(game)
            except:
                print("Invalid date format.")
        print()

    def stats_menu(self, ctrl):
        dates, scores = ctrl.get_stats()
        overall = {}

        for score in sorted(set(scores)):
            times = scores.count(score)
            if times == 1:
                word = "game"
            else: word = "games"

            count = scores.count(score)
            overall[score] = count

            if score == 7:
                print(f"not guessed: {count} {word}")
            else: print(f"guessed in {score} tries: {count} {word}")

        print()
        
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.suptitle(f"{self.game.name} STATS")

        ax1.plot(scores, color="#1E51C9")
        if len(scores):
            ax1.set_yticks(range(max(min(scores)-1, 1), 8))
        ax1.set_ylabel("Tries")
        ax1.set_xlabel("Game Number")

        hbars = ax2.bar(overall.keys(), overall.values(), color="#E7FBFF", edgecolor="#1E51C9")
        ax2.bar_label(hbars, fmt='%d')
        ax2.set_xlabel("Tries")
        ax2.set_ylabel("Games")
        plt.show()

    def start_wordle(self):
        while True:
            self.print_menu()
            cmd = input("\nChoose action: ")
            match cmd.lower():
                case "checker":
                    self.checker_menu()
                case "save":
                    self.save_menu()
                case "get":
                    self.get_menu(self.word_ctrl)
                case "backup":
                    print(f"Backup made to '{self.word_ctrl.backup()}'")
                case "stats":
                    self.stats_menu(self.word_ctrl)
                case "exit":
                    break
                case _:
                    print("Invalid command.")
    
    def start_nerdle(self):
        while True:
            self.print_menu()
            cmd = input("\nChoose action: ")
            match cmd.lower():
                case "save":
                    self.save_menu()
                case "get":
                    self.get_menu(self.nerd_ctrl)
                case "backup":
                    print(f"Backup made to '{self.nerd_ctrl.backup()}'")
                case "stats":
                    self.stats_menu(self.nerd_ctrl)
                case "exit":
                    break
                case _:
                    print("Invalid command.")

    def choose_game(self):
        while True:
            self.print_menu()
            cmd = input("\nChoose game: ")
            match cmd.lower():
                case "wordle":
                    self.game = GameType.WORDLE
                    self.start_wordle()
                    self.game = GameType.NONE
                case "nerdle":
                    self.game = GameType.NERDLE
                    self.start_nerdle()
                    self.game = GameType.NONE
                case "exit":
                    break


if __name__ == '__main__':
    try:
        with open("settings.toml", "rb") as f:
            data = tomllib.load(f)
        
        if 'wordle_repo_path' not in data:
            data['wordle_repo_path'] = "data/wordles.csv"
        if 'nerdle_repo_path' not in data:
            data['nerdle_repo_path'] = "data/nerdles.csv"
        if 'db_repo' not in data:
            data['db_repo'] = False

        if data['db_repo']:
            word_repo = RepositoryDb(data['wordle_repo_path'], WordleGame)
            nerd_repo = RepositoryDb(data['nerdle_repo_path'], NerdleGame)
        else:
            word_repo = Repository(data['wordle_repo_path'], WordleGame)
            nerd_repo = Repository(data['nerdle_repo_path'], NerdleGame)
    except:
        word_repo = Repository("data/wordles.csv", WordleGame)
        nerd_repo = Repository("data/nerdles.csv", NerdleGame)
    
    ui = CLI(WordleCtrl(word_repo), NerdleCtrl(nerd_repo))
    ui.choose_game()
