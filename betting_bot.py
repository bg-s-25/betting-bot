import discord
import math
import random
import os.path

COMMANDS_LIST = ['!hello', '!help', '!join', '!op <clear, start, stop, scores>', '!coins / !c', '!bet <option> <n>', '!bail', '!flip <n>', '!roll <n>']
joined_users = {} # joined users - User objects
op_users = [] # admins - strings
DEFAULT_COINS = 100
OP_ROLES = ['everyone'] # roles required to use !op

client = discord.Client()

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

# Definitions for client events

@client.event
async def on_message(message):
    # bot should not reply to itself
    if message.author == client.user:
        return

    # not a command
    if not message.content.startswith('!'):
        return

    msg_content = message.content
    msg_author = message.author

    if msg_content.startswith('!hello'): # say hello
        msg = "Hello, {0.author.mention}".format(message)

    elif msg_content.startswith('!help'): # list commands
        msg = "List of commands:"
        for command in COMMANDS_LIST:
            msg += "\n- " + command

    elif msg_content.startswith('!join'): # join
        if str(msg_author) in joined_users:
            msg =  "{0.author.mention} You have already joined".format(message)
        else:
            result = join(str(msg_author))
            msg = str(result[1])

    elif msg_content.startswith('!op'): # op (admin commands)
        op_allowed = False
        for role in OP_ROLES:
            if checkrole(msg_author, role):
                op_allowed = True
                break
        if not op_allowed:
            msg = "{0.author.mention} You do not have permission to use this command".format(message)
        else:
            params = str.split(msg_content[4:])
            result = op(str(msg_author), params)
            msg = str(result[1])

    elif msg_content.startswith('!coins') or msg_content.startswith('!c'): # show user's coins
        if not str(msg_author) in joined_users:
            msg = "{0.author.mention} You must !join to do that".format(message)
        else:
            cur_user_obj = joined_users[str(msg_author)]
            msg = str("{0.author.mention} Coins: " + str(cur_user_obj.coins)).format(message)

    elif msg_content.startswith('!bet'): # bet
        params = str.split(msg_content[5:])
        if not str(msg_author) in joined_users:
            msg = "{0.author.mention} You must !join to do that".format(message)
        elif not bet_setting.accept_bets:
            msg = "{0.author.mention} Bets are not currently accepted".format(message)
        elif len(params) != 2:
            msg = "{0.author.mention} Usage: !bet <option> <n>".format(message)
        else:
            result = bet(msg_author, params[0], params[1])
            msg = str(msg_author) + " has betted " + str(result[1][1]) + " coins on " + str(bet_setting.options_labels[int(result[1][0])]) if result[0] == 0 else str(result[1])

    elif msg_content.startswith('!bail'): # reset coins for user
        if not str(msg_author) in joined_users:
            msg = "{0.author.mention} You must !join to do that".format(message)
        else:
            result = bail(msg_author)
            msg = ("{0.author.mention} " + str(result[1])).format(message)

    elif msg_content.startswith('!flip'): # flip n coins
        params = str.split(msg_content[6:])
        result = flip(params[0]) if len(params) > 0 else flip(1)
        msg = "You got: " + str(result[1]) if result[0] == 0 else str(result[1])

    elif msg_content.startswith('!roll'): # roll n dice
        params = str.split(msg_content[6:])
        result = roll(params[0]) if len(params) > 0 else roll(1)
        msg = "You got: " + str(result[1]) if result[0] == 0 else str(result[1])

    elif msg_content.startswith('!checkrole'): # check for user role
        params = str.split(msg_content[11:])
        found_role = checkrole(msg_author, params[0])
        if found_role:
            msg = ("{0.author.mention} You have role @" + str(params[0])).format(message)
        else:
            msg = ("{0.author.mention} You do not have role @" + str(params[0])).format(message)

    else:
        return # do nothing if unknown command read

    if msg != "":
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# Definitions for bot commands
# Each method returns a tuple with a status code and content; 0 = success, 1 = error

def join(user):
    # assumes user has not joined
    joined_users[user] = User(user)
    # attempt to load score for user
    if os.path.isfile('scores.txt'):
        scores_data = fileLst('scores.txt')
        for i in range(len(scores_data)):
            if scores_data[i][0] == user:
                joined_users[user].coins = int(scores_data[i][1])
                break
    print("[JOINED] " + user)
    return (0, "Notice: " + user + " has joined")

def op(user, params):
    if len(params) == 0 or params[0] == '':
        if user in op_users:
            return (1, "Error: User " + user + " already has admin rights")
        op_users.append(user)
        return (0, "Notice: " + user + " has been granted admin rights")
    if user not in op_users:
        return (1, "Error: Permission denied")
    
    if params[0] == 'clear': # clear joined users
        joined_users.clear()
        print("[JOINED USERS CLEARED]")
        return (0, "Notice: All joined users have been cleared")

    elif params[0] == 'start': # start accepting bets
        if bet_setting.accept_bets:
            print("[ERROR] Betting has already started")
            return (1, "Error: Betting has already started")
        params.pop(0)
        if len(params) < 2:
            return (1, "Error: Incorrectly specified options")
        # bet_setting = BetSetting()
        bet_setting.set_options(params)
        bet_setting.accept_bets = True
        msg_string = "Notice: Betting has started!"
        for i in range(len(bet_setting.options_labels)):
            msg_string += "\nOption " + str(i) + ": " + bet_setting.options_labels[i]
        msg_string += "\nUse !bet <option> <n> to place a bet"
        return (0, msg_string)

    elif params[0] == 'stop': # stop accepting bets
        if not bet_setting.accept_bets:
            print("[ERROR] Betting has not been started")
            return (1, "Error: Betting has not been started")
        bet_setting.accept_bets = False
        return_msg = "Notice: Betting has ended!"
        return (0, return_msg)

    elif params[0] == 'win': # stop accepting bets, set winner, allocate coins
        if len(params) != 1 or safe_cast(params[0], int) is None:
            return (1, "Error: Incorrectly specified winner")
        if int(params[0]) < 0 or int(params[0]) > len(bet_setting.options) - 1:
            return (1, "Error: Incorrectly specified winner")
        bet_setting.accept_bets = False
        win(int(params[0]))
        return_msg = "Notice: Betting has ended! The winner is " + bet_setting.options_labels[int(params[0])]
        reset()
        return (0, return_msg)

    elif params[0] == 'set': # set amount manually to user index - e.g. !set 0 100
        joined_users[str(params[1])].coins = int(params[2])
        return (0, "Set coins")

    elif params[0] == 'scores': # display scoreboard
        return (0, scoreboard())

    elif params[0] == 'save': # save all user' scores to text file
        f = open('scores.txt', 'w+')
        for user_key in joined_users:
            f.write(user_key + ' ' + str(joined_users[user_key].coins))
        f.close()
        return (0, "")

    return (1, "Error: Unrecognized parameter(s)")

def bail(user):
    # assumes user has joined
    cur_user_obj = joined_users[str(user)]
    cur_user_obj.coins = DEFAULT_COINS
    return (0, "Bailed. Coins: " + str(cur_user_obj.coins))

def bet(user, option, n):
    # assumes user has joined
    if safe_cast(option, int) is None:
        return (1, "Error: Invalid bet option")
    elif int(option) not in range(len(bet_setting.options_labels)):
        return (1, "Error: Invalid bet option")
    if safe_cast(n, int) is None:
        return (1, "Error: Invalid bet value")
    elif int(n) <= 0:
        return (1, "Error: Invalid bet value")
    user = str(user)
    cur_user_obj = joined_users[user]
    if cur_user_obj.betted:
        return (1, "Error: " + user + " has already betted this round")
    elif int(n) > cur_user_obj.coins:
        return (1, "Error: " + user + " cannot bet higher than current coins")
    cur_user_obj.coins -= int(n)
    cur_user_obj.cur_bet_option = int(option)
    cur_user_obj.cur_bet = int(n)
    bet_setting.options[int(option)][1] += 1 # update bet cnt for option
    bet_setting.options[int(option)][2] += int(n) # update bet val for option
    cur_user_obj.betted = True
    return (0, [option, n])

def win(win_index):
    pots_total = 0
    for option in bet_setting.options:
        pots_total += option[2]
    for user_key in joined_users:
        cur_user_obj = joined_users[user_key]
        if cur_user_obj.cur_bet_option == win_index: # user won bet
            amount_gained = cur_user_obj.cur_bet + math.floor((cur_user_obj.cur_bet / bet_setting.options[win_index][2]) * (pots_total - bet_setting.options[win_index][2]))
            cur_user_obj.coins += amount_gained

def reset():
    for user_key in joined_users:
        joined_users[user_key].betted = False
        joined_users[user_key].cur_bet_option = 0
        joined_users[user_key].cur_bet = 0
    bet_setting.options.clear()
    bet_setting.options_labels.clear()

def scoreboard():
    users_and_scores = []
    for user_key in joined_users:
        users_and_scores.append([joined_users[user_key].username, joined_users[user_key].coins])
    users_and_scores.sort(key=lambda x: x[1], reverse=True)
    scoreboard = "--- Scoreboard ---"
    for i in range(len(users_and_scores)):
        scoreboard += "\n" + str(i + 1) + " - " + users_and_scores[i][0] + " [" + str(users_and_scores[i][1]) + "]"
    return scoreboard

def checkrole(msg_author, seeking_role):
    for role in msg_author.roles:
        role_str = str(role)[1:]
        if str(seeking_role).lower() == role_str.lower(): # omit '@' in role string
            return True
    return False

def flip(n):
    if safe_cast(n, int) is None:
        return (1, "Error: Unrecognized parameter(s)")
    result_string = ''
    for _ in range(0, int(n)):
        rnd = random.randint(0, 1) 
        if rnd == 0:
            result_string += 'HEADS, '
        else:
            result_string += 'TAILS, '
    return (0, result_string[:-2])

def roll(n):
    if safe_cast(n, int) is None:
        return (1, "Error: Unrecognized parameter(s)")
    result_string = ''
    for _ in range(0, int(n)):
        rnd = random.randint(0, 5) + 1
        result_string += str(rnd) + ', '
    return (0, result_string[:-2])

# Misc

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def fileLst(file):
    input = []
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            input.append(line.strip())
        input = list(filter(lambda s: '\n' not in s, input))
    for i in range(len(input)):
        input[i] = input[i].split(' ')
    return input

# Get things ready
COMMANDS_LIST.sort()
f = open('current_token.txt', 'r')
lines = f.readlines()
bet_setting = BetSetting()

# Run bot
client.run(lines[0])
