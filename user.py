'''
Betting Bot for Discord -> module user
Date: Nov 2018 - Mar 2019
'''
DEFAULT_COINS = 100

class User:
    def __init__(self, username):
        self.__username = username
        self.__coins = DEFAULT_COINS
        self.__betted = False
        self.__cur_bet_option = 0
        self.__cur_bet = 0

    @property
    def username(self):
        return self.__username
    @property
    def coins(self):
        return self.__coins
    @property
    def betted(self):
        return self.__betted
    @property
    def cur_bet_option(self):
        return self.__cur_bet_option
    @property
    def cur_bet(self):
        return self.__cur_bet
    @coins.setter
    def coins(self, coins):
        if isinstance(coins, int):
            if not coins < 0:
                self.__coins = coins
    @betted.setter
    def betted(self, betted):
        if isinstance(betted, bool):
            self.__betted = betted
    @cur_bet_option.setter
    def cur_bet_option(self, cur_bet_option):
        if cur_bet_option == 0 or cur_bet_option == 1:
            self.__cur_bet_option = cur_bet_option
    @cur_bet.setter
    def cur_bet(self, cur_bet):
        if isinstance(cur_bet, int):
            if not cur_bet < 0:
                self.__cur_bet = cur_bet