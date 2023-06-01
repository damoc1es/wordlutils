from wordle import *
from nerdle import *
from repo import Repository
import unittest


class TestWordleCtrl(unittest.TestCase):
    def setUp(self):
        self.controller = WordleCtrl(Repository("data/test_wordles.csv", WordleGame))
        self.controller.start()

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


class TestWordleRunner(unittest.TestCase):
    def test(self):
        game = WordleRunner()
        game.add_try('OCTAL', '___Y_')
        game.add_try('SIREN', 'G___Y')
        game.add_try('DUMPY', '_Y___')
        game.add_try('STUNT', 'G_YY_')
        game.add_try('SONAR', 'G_YY_')

        gray, yellow, green = game.get_data()
        
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
        assert w.result('CLOSE') == 'GGGGG'
    
    def testB(self):
        w = WordleSimulation('GREEN')
        assert w.result('EEEGE') == 'Y_GY_'


class TestNerdleSimulation(unittest.TestCase):
    def testA(self):
        w = NerdleSimulation("11+5-7=9")
        assert w.result("15+24=39") == 'GYG__Y_G'
        assert w.result("17+1-9=9") == 'GYGYG_GG'
        assert w.result("11+5-7=9") == 'GGGGGGGG'
    
    def testB(self):
        w = NerdleSimulation("99-41=58")
        assert w.result("15+24=39") == 'YY__YG_Y'
        assert w.result("54-14=40") == 'YYGY_G__'
        assert w.result("99-55=44") == 'GGGY_GY_'


if __name__ == '__main__':
    unittest.main()
