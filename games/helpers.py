""" Helpful functions for the games app """

def get_rank_skill_odds(player):
    """ simple algorithm to be used to improve odds in certain games """
    # from 0 - 10
    if player.games_done <= 10:
        skill = 0
    # from 11 - 100
    elif player.games_done > 10 and player.games_done <= 100:
        skill = 1
    # from 101-200
    elif player.games_done > 100 and player.games_done <= 200:
        skill = 2
    # from 201-
    elif player.games_done > 200 and player.games_done <= 500:
        skill = 3
    # from 501+
    elif player.games_done > 500:
        skill = 4

    rank_skill_odds = player.rank.id * skill

    return rank_skill_odds
