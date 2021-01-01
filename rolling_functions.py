import logging
import scripts as s

def pass_line_only(bankroll, max_rolls, min_bet, log_level=logging.INFO):
    logging.basicConfig(level=log_level)
    r = s.CrapsRound(min_bet, bankroll, log_level)
    i = 1
    bank_list = []

    while i < max_rolls:
        
        if r.bank < 0:
            break
        
        if r.point < 0:
        
            logging.debug(f"Bank = ${r.bank}")
            bank_list.append(r.bank)
            
            r.bet_pass(min_bet)
            r.comeout_roll()
        else:
            # extend rolls so we finish the round
            if i == max_rolls:
                i -= 1
            r.keep_rolling()

        i += 1
    
    logging.debug(f"Bank = ${r.bank}")
    bank_list.append(r.bank)
    return r.num_games, r.num_rolls, r.bank, bank_list


def dont_pass_line_only(bankroll, max_rolls, min_bet, log_level=logging.INFO):
    r = s.CrapsRound(min_bet, bankroll, log_level)
    i = 0
    bank_list = []


    while i < max_rolls:
        if r.bank < 0:
            break

        if r.dn_pass_bet == 0:
            r.bet_dont_pass(min_bet)

        if r.point < 0:
            bank_list.append(r.bank)
            r.comeout_roll()
        else:
            # extend rolls so we finish the round
            if i == max_rolls - 1:
                i -= 1
            r.keep_rolling()

        i += 1

    bank_list.append(r.bank)
    return r.num_games, r.num_rolls, r.bank, bank_list


def pass_and_come(bankroll, max_rolls, min_bet, max_num_bets, log_level=logging.INFO):
    r = s.CrapsRound(min_bet, bankroll, log_level)
    i = 0
    bank_list = []

    while i < max_rolls:
        if r.bank < 0:
            break

        if r.pass_bet == 0:
            r.bet_pass(min_bet)
        if r.point < 0:
            bank_list.append(r.bank)
            r.comeout_roll()
        else:
            if len(r.come_points) < max_num_bets:
                r.bet_come(min_bet)
            r.keep_rolling()
            # extend rolls so we finish the round
            if i == max_rolls - 1:
                i -= 1
        i += 1

    bank_list.append(r.bank)
    return r.num_games, r.num_rolls, r.bank, bank_list


def place_bets_6and8(bankroll, max_rolls, min_bet, place_bet, keep_on, log_level=logging.INFO):
    '''keep_on = whether to keep place bets on during comeout roll
    '''
    r = s.CrapsRound(min_bet, bankroll, place_bets_on=keep_on, log_level=log_level)
    i = 0
    bank_list = []

    while i < max_rolls:
        if r.bank < 0:
            break
        
        if r.point < 0:
            bank_list.append(r.bank)
            r.comeout_roll()
        else: 
            if 6 not in r.place_points:
                r.bet_place(place_bet, 6)
            if 8 not in r.place_points:
                r.bet_place(place_bet, 8)
            
            # extend rolls so we finish the round
            if i == max_rolls - 1:
                i -= 1
            r.keep_rolling()

        i += 1

    bank_list.append(r.bank)
    return r.num_games, r.num_rolls, r.bank, bank_list