import itertools
import random
import warnings

from collections import namedtuple

from isolation import Board
from sample_players import RandomPlayer
from sample_players import null_score
from sample_players import open_move_score
from sample_players import improved_score
from game_agent import CustomPlayer
from game_agent import custom_score

NUM_TOURNAMENTS = 5
NUM_MATCHES = 5  # number of matches against each opponent
TIME_LIMIT = 150  # number of milliseconds before timeout

TIMEOUT_WARNING = "One or more agents lost a match this round due to " + \
                  "timeout. The get_move() function must return before " + \
                  "time_left() reaches 0 ms. You will need to leave some " + \
                  "time for the function to return, and may need to " + \
                  "increase this margin to avoid timeouts during  " + \
                  "tournament play."


Agent = namedtuple("Agent", ["player", "name"])

def play_match(player1, player2):
    """
    Play a "fair" set of matches between two agents by playing two games
    between the players, forcing each agent to play from randomly selected
    positions. This should control for differences in outcome resulting from
    advantage due to starting position on the board.
    """
    num_wins = {player1: 0, player2: 0}
    num_timeouts = {player1: 0, player2: 0}
    num_invalid_moves = {player1: 0, player2: 0}
    games = [Board(player1, player2), Board(player2, player1)]

    # initialize both games with a random move and response
    for _ in range(2):
        move = random.choice(games[0].get_legal_moves())
        games[0].apply_move(move)
        games[1].apply_move(move)

    # play both games and tally the results
    for game in games:
        winner, _, termination = game.play(time_limit=TIME_LIMIT)

        if player1 == winner:
            num_wins[player1] += 1

            if termination == "timeout":
                num_timeouts[player2] += 1
            else:
                num_invalid_moves[player2] += 1

        elif player2 == winner:

            num_wins[player2] += 1

            if termination == "timeout":
                num_timeouts[player1] += 1
            else:
                num_invalid_moves[player1] += 1

    if sum(num_timeouts.values()) != 0:
        warnings.warn(TIMEOUT_WARNING)

    return num_wins[player1], num_wins[player2]


def play_round(agents, num_matches):
    """
    Play one round (i.e., a single match between each pair of opponents)
    """
    agent_1 = agents[-1]
    wins = 0.
    total = 0.

    # print("\nPlaying Matches:")
    # print("----------")

    for idx, agent_2 in enumerate(agents[:-1]):

        counts = {agent_1.player: 0., agent_2.player: 0.}
        names = [agent_1.name, agent_2.name]
        # print("  Match {}: {!s:^11} vs {!s:^11}".format(idx + 1, *names), end=' ')

        # Each player takes a turn going first
        for p1, p2 in itertools.permutations((agent_1.player, agent_2.player)):
            for _ in range(num_matches):
                score_1, score_2 = play_match(p1, p2)
                counts[p1] += score_1
                counts[p2] += score_2
                total += score_1 + score_2

        wins += counts[agent_1.player]

    return 100. * wins / total


def main():
    for tour_num in range(NUM_TOURNAMENTS):
        HEURISTICS = [("Null", null_score),
                      ("Open", open_move_score),
                      ("Improved", improved_score)]
        AB_ARGS = {"search_depth": 5, "method": 'alphabeta', "iterative": False}
        MM_ARGS = {"search_depth": 3, "method": 'minimax', "iterative": False}
        CUSTOM_ARGS = {"method": 'alphabeta', 'iterative': True}

        mm_agents = [Agent(CustomPlayer(score_fn=h, **MM_ARGS),
                           "MM_" + name) for name, h in HEURISTICS]
        ab_agents = [Agent(CustomPlayer(score_fn=h, **AB_ARGS),
                           "AB_" + name) for name, h in HEURISTICS]
        random_agents = [Agent(RandomPlayer(), "Random")]

        test_agents = [Agent(CustomPlayer(score_fn=improved_score, **CUSTOM_ARGS), "ID_Improved"),
                       Agent(CustomPlayer(score_fn=custom_score, **CUSTOM_ARGS), "Student")]

        for agentUT in test_agents:
            agents = random_agents + mm_agents + ab_agents + [agentUT]
            win_ratio = play_round(agents, NUM_MATCHES)
            print("{:>10.2f}".format(win_ratio))

        print("-----")


if __name__ == "__main__":
    main()
