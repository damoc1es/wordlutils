import shutil, os
import datetime


class Repository:
    def __init__(self, filename: str, game_type):
        self.filename = filename
        self.game_type = game_type

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
            return self.game_type.from_repr(result[-1].strip())
        
        for line in result:
            if line.startswith(date.isoformat()):
                return self.game_type.from_repr(line.strip())
        
        return None
    
    def get_all(self):
        with open(self.filename, 'r') as f:
            return [self.game_type.from_repr(line) for line in f.readlines()]

    def backup(self, date: datetime.datetime):
        filename, file_extension = os.path.splitext(self.filename)
        backup_file = f"{filename}_{date.strftime('%Y%m%d-%H%M%S')}{file_extension}"
        shutil.copy2(self.filename, backup_file)
        return backup_file
