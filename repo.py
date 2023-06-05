import shutil, os
import datetime
import sqlite3


class Repository:
    def __init__(self, filename: str, game_class):
        self.filename = filename
        self.game_class = game_class

        with open(self.filename, 'a+') as f:
            pass
    
    def add(self, game):
        with open(self.filename, 'a') as f:
            print(repr(game), file=f)
    
    def get(self, date):
        result = []
        with open(self.filename, 'r') as f:
            result = f.readlines()
        
        if len(result) == 0:
            return None
        
        if date is None:
            return self.game_class.from_repr(result[-1].strip())
        
        for line in result:
            if line.startswith(date.isoformat()):
                return self.game_class.from_repr(line.strip())
        
        return None
    
    def get_all(self):
        with open(self.filename, 'r') as f:
            return [self.game_class.from_repr(line) for line in f.readlines()]

    def backup(self, date: datetime.datetime):
        filename, file_extension = os.path.splitext(self.filename)
        backup_file = f"{filename}_{date.strftime('%Y%m%d-%H%M%S')}{file_extension}"
        shutil.copy2(self.filename, backup_file)
        return backup_file


class RepositoryDb:
    def __init__(self, path, game_class):
        self.path = path
        self.game_class = game_class
        self.conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self._create_table()
    
    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.game_class.NAME} (
                date DATE, tries TEXT, results TEXT, solution TEXT
            )
        """)
        self.conn.commit()

    def add(self, game):
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO {self.game_class.NAME} VALUES (?, ?, ?, ?)",
            (game.date, ' '.join(game.tries), ' '.join(game.results), game.solution))
        self.conn.commit()
    
    def get(self, date):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.game_class.NAME} WHERE date = ?", (date,))
        result = cursor.fetchone()
        
        if result is None:
            return None

        return self.game_class(result[0], result[1].split(), result[2].split(), result[3])

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.game_class.NAME}")

        return [self.game_class(row[0], row[1].split(), row[2].split(), row[3]) for row in cursor.fetchall()]

    def backup(self, date: datetime.datetime):
        if self.path == ":memory:":
            return ":memory:"
        
        filename, file_extension = os.path.splitext(self.path)
        backup_file = f"{filename}_{date.strftime('%Y%m%d-%H%M%S')}{file_extension}"
        shutil.copy2(self.path, backup_file)
        return backup_file


def csv_to_db(repo_csv, repo_db):
    games = repo_csv.get_all()
    for game in games:
        repo_db.add(game)
