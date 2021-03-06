import logging
import scripts as s

def pass_line_only(bankroll, max_rolls, min_bet, log_level=logging.INFO):
    r = s.CrapsGame(min_bet, bankroll, log_level)
    i = 1
    bank_list = []

    while i < max_rolls:
        
        if r.bank < 0:
            break
        
        if r.point < 0:
        
            r.logger.debug(f"Bank = ${r.bank}")
            bank_list.append(r.bank)
            
            r.bet_pass(min_bet)
            r.comeout_roll()
        else:
            # extend rolls so we finish the round
            if i == max_rolls:
                i -= 1
            r.keep_rolling()

        i += 1

    
    r.logger.debug(f"Bank = ${r.bank}")
    bank_list.append(r.bank)
    return r.num_rounds, r.num_rolls, r.bank, bank_list


def dont_pass_line_only(bankroll, max_rolls, min_bet, log_level=logging.INFO):
    r = s.CrapsGame(min_bet, bankroll, log_level)
    i = 1
    bank_list = []


    while i < max_rolls:

        if r.bank < 0:
            break

        if r.point < 0:
            r.show_bank()
            bank_list.append(r.bank)
            r.bet_dont_pass(min_bet)
            r.comeout_roll()
        else:
            # extend rolls so we finish the round
            if i == max_rolls:
                i -= 1
            r.keep_rolling()

        i += 1

    r.show_bank()
    bank_list.append(r.bank)
    return r.num_rounds, r.num_rolls, r.bank, bank_list


def pass_and_come(bankroll, max_rolls, min_bet, max_come_bets, log_level=logging.INFO):
    """
    Set `max_come_bets` to 6 for "always" betting Come.
    """
    r = s.CrapsGame(min_bet, bankroll, log_level)
    i = 1
    bank_list = []

    while i < max_rolls:

        if r.bank < 0:
            break

        if r.point < 0:
            r.show_bank()
            bank_list.append(r.bank)

            r.bet_pass(min_bet)
            r.comeout_roll()
        else:
            # extend rolls so we finish the round
            if i == max_rolls:
                i -= 1
            
            num_come_pts = len(r.come_points)
            if (num_come_pts < max_come_bets) and (num_come_pts < len(s.point_list)):
                r.bet_come(min_bet)
                
            r.keep_rolling()
        i += 1

    bank_list.append(r.bank)
    return r.num_rounds, r.num_rolls, r.bank, bank_list


def place_bets_6and8(bankroll, max_rolls, min_bet, place_bet, keep_on, log_level=logging.INFO):
    '''keep_on = whether to keep place bets on during comeout roll
    '''
    r = s.CrapsGame(min_bet, bankroll, place_bets_on=keep_on, log_level=log_level)
    i = 1
    bank_list = []

    while i < max_rolls:

        if r.bank < 0:
            break
        
        if r.point < 0:
            bank_list.append(r.bank)
            r.comeout_roll()
        else: 
            # extend rolls so we finish the round
            if i == max_rolls:
                i -= 1
            if 6 not in r.place_points:
                r.bet_place(place_bet, 6)
            if 8 not in r.place_points:
                r.bet_place(place_bet, 8)  
            r.keep_rolling()
        i += 1
        

    bank_list.append(r.bank)
    return r.num_rounds, r.num_rolls, r.bank, bank_list