'''Where I left off:

implementing place bet_pass
- check when to set / reset place_bets_on

'''

import logging
import random
from itertools import permutations
from collections import defaultdict
import numpy as np

point_list = [4, 5, 6, 8, 9, 10]
place_payout_odds = [9, 7, 7, 7, 7, 9] # assuming bets of: [5, 5, 6, 6, 5, 5]

# Rolling functions 
def roll_dice():
    d1, d2 = random.choices(np.arange(1,7), k=2)
    return d1, d2, d1+d2

# to specify the number rolled (for testing)
dice_rolls = list(permutations(range(1, 7), 2))
for i in range(1, 7):
    dice_rolls.append((i, i))
rolls_with_sum = [(x, y, x+y) for x,y in dice_rolls]
dice_dict = defaultdict(list)
for roll in rolls_with_sum:
    dice_dict[roll[2]].append([roll[0], roll[1]])

def test_dice(val):
    possible_rolls = dice_dict[val]
    # rr = random.choice(possible_rolls)
    d1, d2 = random.choice(possible_rolls)
    # rr.append(val)
    # return rr
    return d1, d2, val


class Error(Exception):
    pass 

class CrapsError(Error):
    def __init__(self, message):
        self.message = message

class CrapsRound():
    def __init__(self, min_bet, bankroll, log_level=logging.INFO, place_bets_on=False):
        '''
        place_bets_on = whether to keep place bets on during comeout roll
        '''
        self.min_bet = min_bet
        self.bank = bankroll
        self.num_rolls = 0
        self.num_games = 0
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger()
        # self.place_bets_on = False
        self.keep_place_bets_on = place_bets_on

        self._reset_indicators()
        self._reset_pass_bets()
        self._reset_come_bets()
        self._reset_place_bets()


    # RESET functions ----------------------------------------------------------
    def _reset_indicators(self):
        self.natural = False
        self.craps = False
        self.point_hit = False
        self.come_hit = False

    def _reset_pass_bets(self):
        self.point = -1
        self.pass_bet = 0
        self.dn_pass_bet = 0

    def _reset_come_bets(self):
        self.come_points = []
        self.come_bet = 0
        self.dn_come_bet = 0
        self.come_bets = [0, 0, 0, 0, 0, 0] # these correspond to point list indexes

    def _reset_place_bets(self):
        self.place_points = []
        self.place_bets = [0, 0, 0, 0, 0, 0] # these correspond to point list indexes
        self.place_bets_on = False


    # SHOW functions ----------------------------------------------------------
    def show_bank(self):
        self.logger.debug(f'Bank value: ${self.bank}')
        pass

    def show_bets(self):
        self.logger.info(f'Pass bet is ${self.pass_bet}')
        self.logger.info(f'Point is {self.point}')
        self.logger.info(f'Come bet is ${self.come_bet}')
        self.logger.info(f'Come bets are {list(zip(point_list, self.come_bets))}')
        self.logger.info(f'Place bets are {list(zip(point_list, self.place_bets))}')


    # BETTING functions ----------------------------------------------------------
    def bet_pass(self, bet):
        # check that we don't already have a pass bet:
        if self.pass_bet != 0 or self.point > 0:
            # self.logger.error('error! There is already a pass bet')
            self.logger.error('You cannot place a Pass bet now')
        else:
            self.pass_bet += bet
            self.logger.debug('Placing pass bet')

    def bet_dont_pass(self, bet):
        # check that we don't already have a don't pass bet:
        if self.dn_pass_bet != 0 or self.point > 0:
            # self.logger.error('error! There is already a pass bet')
            self.logger.error('You cannot place a Pass bet now')
        else:
            self.dn_pass_bet += bet
            self.logger.debug("Placing don't pass bet")

    def bet_come(self, bet):
        # check that we don't already have a come bet
        # and that there has already been a comeout roll
        if self.come_bet != 0 | self.point < 0:
            self.logger.error('Cannot place a come bet')
        else:
            self.come_bet += bet
            self.logger.debug('Placing come bet')

    def bet_dont_come(self, bet):
        # check that we don't already have a bet
        # and that there has already been a comeout roll
        if self.dn_come_bet != 0 | self.point < 0:
            self.logger.error("Cannot place a don't come bet")
        else:
            self.dn_come_bet += bet
            self.logger.debug("Placing don't come bet")

    def bet_place(self, bet, number): 
        '''
        Notes:
        - It's recommended to bet in multiples of $5 on 4,5,9,10
        and in multiples of $6 on 6,8
        - place bets kept on after winning by default. Call 
        `take_down_place_bet` if wish to take down at any point.
        '''
        if self.point < 0:
            raise CrapsError("Cannot make a place bet before or during the comeout roll")

        if number not in point_list:
            raise ValueError("Number for place bet must be a point")

        if number in self.place_points:
            raise ValueError(f"Place bet has already been made on {number}")
        
        self.logger.debug(f'Making a place bet on {number}')
        self.place_bets[point_list.index(number)] = bet
        self.place_points.append(number)
        self.place_bets_on = True


# TODO: write function to take down place bets
    def take_down_place_bet(self, number):
        idx = point_list.index(number)
        self.bank += self.place_bets[idx] # transfer place bet back to bank
        self.place_bets[idx] = 0 # reset place_bets for this number to 0
        self.place_points.remove(number) # remove number from place_points list


    # PAYOUT & CHECKING OUTCOMES ---------------------------------------------
    def _check_comeout_roll(self, roll):
        '''NOTE: keep as separate function because need to perform
        this check on actual comeout roll, and after a come-bet is
        placed.

        This checks for Natural or Craps, and establishes the Point
        (if there is not one).
        '''
        if roll in [7, 11]: # Natural
            self.logger.debug('Natural!')
            self.natural = True
            # self._payout_basic_bets()
            return True

        elif roll in [2, 3, 12]: # Craps
            self.logger.debug('Craps!')
            self.craps = True
            # self._payout_basic_bets()
            return True
        
        else:
            return False
    

    def _payout_pass_bets(self):
        self.logger.debug(f'Craps: {self.craps}')
        if self.natural: # 7 or 11 on comeout roll
            self.bank += self.pass_bet
            self.bank -= self.dn_pass_bet

        if self.craps: # 2,3, or 12 on comeout roll; 7 or 11 before point hit
            self.bank -= self.pass_bet
            self.bank += self.dn_pass_bet

        if self.point_hit: #  point rolled before craps
            self.bank += self.pass_bet
            self.bank -= self.dn_pass_bet


    def _payout_come_bets(self):
        if self.natural: # 7 or 11 on comeout roll
            self.bank += self.come_bet
            self.bank -= self.dn_come_bet

        if self.craps: # 2,3, or 12 on comeout roll; 7 or 11 before point hit
            self.bank -= self.come_bet
            self.bank += self.dn_come_bet




    def _handle_come_bets(self, roll):
        '''NOTES:
        Need this as a separate function, because
            needs to be called from a "regular" roll
            and from a comeout roll
        Peform pay-out and resetting of variables here
            because we need to know the roll (other payouts
            do not depend on roll, so they can be called without
            that argument/information)
        '''
        # self.logger.debug('Come points are: {}'.format(self.come_points))

        if self.craps:
            # lose come bets
            self.logger.debug('All come points lost!')
            self.bank -= sum(self.come_bets)
            self._reset_come_bets()

        # if a come-point is hit
        elif roll in self.come_points:
            # pay out come bet for this point
            self.logger.debug('Come bet won for {}!'.format(roll))
            cb_idx = point_list.index(roll)
            self.bank += self.come_bets[cb_idx]

            # reset come bet & come point list for this number
            self.come_bets[cb_idx] = 0
            self.come_points.remove(roll)

        # establish come point if come bet on
        if self.come_bet > 0:
            # add point to come_points list
            # add come bet to come_bets list
            # reset come_bet
            self.logger.debug('Adding point {} to come bets'.format(roll))
            self.come_points.append(roll)
            self.come_bets[point_list.index(roll)] = self.come_bet
            self.come_bet = 0


    def _handle_place_bets(self, roll):
        '''NOTE: 
        - function is only called if self.place_bets_on == True
        - place bets stay on after winning
        '''
        # check for craps
        if self.craps:
            self.logger.debug('Place bets lost!')
            self.bank -= sum(self.place_bets)
            self._reset_place_bets()
            self.place_bets_on = False
        
        # if point was hit, check if we should turn place bets off
        else:
            if self.point_hit and not self.keep_place_bets_on:
                self.place_bets_on = False

            # else check if place bet hit
            if roll in self.place_points:
                idx = point_list.index(roll) # number index in lists
                bet = self.place_bets[idx] # what was bet?
                odds = place_payout_odds[idx] # pay-out odds for this number
                if roll in [6,8]:
                    # if you didn't bet a multiple of $6 on 6,8 you only win $%
                    if bet % 6 != 0: 
                        payout = int(bet / 5) * 5
                    # otherwise, pay out the odds
                    else: 
                        payout = int(bet / 6) * odds
                else:
                    payout = int(bet / 5) * odds
                self.logger.debug(f'Place bet won for {roll}! Payout is ${payout}')
                self.bank += payout






    # ROLLS ---------------------------------------------------------------
    def _roll(self, test=False, val=0):
        self.num_rolls += 1
        if not test:
            roll = roll_dice()
        else:
            roll = test_dice(val)
        self.logger.debug(f"You rolled {roll[2]} ({roll[0]} + {roll[1]})")
        return roll


    def comeout_roll(self, test=False, val=0):
        # if self.come_bet != 0:
        #     raise CrapsError('No come bets allowed on come-out roll!')

        self.num_games += 1
        self.logger.debug(f'***** Game # {self.num_games} *****')
        self.logger.debug(f'Bank = ${self.bank}')

        roll = self._roll(test, val)[2]

        # check for craps, natural
        roll_check = self._check_comeout_roll(roll)
        self._payout_pass_bets()

        # if there are come-points established, check them
        if len(self.come_points) > 0:
            self._handle_come_bets(roll)

        # if place bets on, check them:
        if self.place_bets_on: #& len(self.place_bets) > 0:
            self._handle_place_bets(roll)
        
        # set point
        if not roll_check:
            self.logger.debug('Point is set to {}'.format(roll))
            self.point = roll
            self.round_on = True
            # turn place bets back on 
            if len(self.place_points) > 0:
                self.place_bets_on = True
        
        # reset indicators
        self._reset_indicators()


    def keep_rolling(self, test=False, val=0):
        if self.point < 0:
            raise CrapsError('Point must be established in order for this roll to happen')
        
        roll = self._roll(test, val)[2]

        # if come-out roll for come bet:
        if self.come_bet > 0:
            self.logger.debug('Comeout roll for come bet!')
            # check for crap/natural
            roll_check = self._check_comeout_roll(roll)
            self._payout_come_bets()

            if roll_check: # reset come_bet & indicators if won/lost come bet
                self.come_bet = 0
                self._reset_indicators()
            else: # otherwise, establish come point
                self._handle_come_bets(roll)
        else:
            # if there are come-points established, check them
            if len(self.come_points) > 0:
                self._handle_come_bets(roll)

        # craps
        if roll == 7:
            self.craps = True
            self.logger.debug('Craps!')
            self._payout_pass_bets()

        # the point is hit
        elif roll == self.point:
            self.point_hit = True
            self.logger.debug('Point hit!')
            # if self.pass_bet > 0:
            #     self.logger.debug('Point wins!')
            self._payout_pass_bets()


        # if place bets on, check them:
        if self.place_bets_on: #& len(self.place_bets) > 0:
            self._handle_place_bets(roll)

        # reset pass line things if won/lost pass bets
        if self.craps or self.point_hit:
            self._reset_pass_bets()

        # reset indicators
        self._reset_indicators()
