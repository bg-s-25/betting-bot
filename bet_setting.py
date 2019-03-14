'''
Betting Bot for Discord -> module bet_setting
Date: Nov 2018 - Mar 2019
'''
DEFAULT_COINS = 100

class BetSetting:
    def __init__(self):
        self.__accept_bets = False
        self.__options = []
        self.__options_labels = []

    @property
    def accept_bets(self):
        return self.__accept_bets
    @property
    def options(self):
        return self.__options
    @property
    def options_labels(self):
        return self.__options_labels
    @accept_bets.setter
    def accept_bets(self, accept_bets):
        self.__accept_bets = accept_bets
    @options.setter
    def options(self, options):
        self.__options = options

    def set_options(self, options_labels):
        self.__options_labels = options_labels
        for s in options_labels:
            self.__options.append([s, 0, 0]) # ea option has [label, bet cnt, bet val]
