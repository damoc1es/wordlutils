from wordlutils import *
import unittest


class TestWordleController(unittest.TestCase):
    def setUp(self):
        self.controller = Controller(Repository("data/test_wordles.csv"))
        self.controller.start_game()

    def test(self):
        self.controller.add_try('OCTAL', '___Y_')
        assert len(self.controller.get_possible_solutions()) > 0
        self.controller.add_try('SIREN', 'G___Y')
        assert len(self.controller.get_possible_solutions()) > 0
        self.controller.add_try('DUMPY', '_Y___')
        assert len(self.controller.get_possible_solutions()) > 0
        self.controller.add_try('STUNT', 'G_YY_')
        assert len(self.controller.get_possible_solutions()) > 0
        self.controller.add_try('SONAR', 'G_YY_')
        assert len(self.controller.get_possible_solutions()) > 0
        self.controller.add_try('SNAFU', 'GGGGG')
        assert len(self.controller.get_possible_solutions()) == 1


class TestWordleGame(unittest.TestCase):
    def test(self):
        game = WordleGame()
        game.add_try('OCTAL', '___Y_')
        game.add_try('SIREN', 'G___Y')
        game.add_try('DUMPY', '_Y___')
        game.add_try('STUNT', 'G_YY_')
        game.add_try('SONAR', 'G_YY_')

        gray = game.gray_chars
        yellow = game.yellow_chars
        green = game.green_chars
        
        assert set(gray) == set('octliredmpyor')
        
        assert set(yellow[1]) == set()
        assert set(yellow[2]) == set('u')
        assert set(yellow[3]) == set('un')
        assert set(yellow[4]) == set('ana')
        assert set(yellow[5]) == set('n')

        assert green == {1: 's', 2: None, 3: None, 4: None, 5: None}


class TestWordleSimulation(unittest.TestCase):
    def testA(self):
        w = WordleSimulation('CLOSE')
        assert w.result('CHEER') == 'G_Y__'
        assert w.result('LEAVE') == 'Y___G'
    
    def testB(self):
        w = WordleSimulation('GREEN')
        assert w.result('EEEGE') == 'Y_GY_'

if __name__ == '__main__':
    unittest.main()
