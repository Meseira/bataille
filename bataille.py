"""
Simple simulator of Bataille card game

This module allows to simulate Bataille card game for an arbitrary
number of players, choosing the number of suits, cards per suit and
jokers in the card deck.
"""

import collections
import random


class Deck(object):
    """
    Configurable deck of cards that can be distributed
    """
    def __init__(self, card_count_per_color, color_count, joker_count):
        """
        Initialize deck of cards

        Args:
            card_count_per_color (int): number of cards per suit
            color_count (int): number of suits
            joker_count (int): number of jokers
        """
        joker_value = card_count_per_color
        self.cards = (
            list(range(card_count_per_color)) * color_count +
            [joker_value] * joker_count
        )

    def distribute(self, n):
        """
        Distribute the cards in n stacks

        Args:
            n (int): number of stacks

        Returns:
            List of n card stacks
        """
        random.shuffle(self.cards)
        return [self.cards[i::n] for i in range(n)]


class Player(object):
    """
    Orderable card player with score
    """
    def __init__(self, name, cards):
        """
        Initialize player attributes

        Args:
            name (str): player's name
            cards (list): player's card deck
        """
        self.name = str(name)
        self.cards = collections.deque(cards)
        self.clear()

    def __lt__(self, other):
        """
        Score based less-than operator
        """
        return self.score < other.score

    def clear(self):
        """
        Clear player's score
        """
        self.played_cards = []
        self.score = [-1, -1]

    def collect_cards(self, cards):
        """
        Collect cards at the bottom of player's card stack

        Args:
            cards (list): cards to be collected
        """
        self.cards.extend(cards)

    def discard_card(self):
        """
        Discard a card without changing the score
        """
        self.played_cards.append(self.cards.popleft())

    def has_card(self):
        """
        Returns True if the player has at least one playable card
        """
        return len(self.cards) > 0

    def play_card(self):
        """
        Play a card and update player's score
        """
        played_card = self.cards.popleft()
        self.played_cards.append(played_card)
        self.score[0] += 1
        self.score[1] = played_card


class Game(object):
    """
    Bataille game to run
    """
    def __init__(self, deck, player_count):
        """
        Initialize Bataille game

        Args:
            deck (Deck): full deck of cards
            player_count (int): number of players
        """
        self.players = [
            Player(f'Player {i}', cards)
            for (i, cards)
            in enumerate(deck.distribute(player_count))
        ]
        self.results = {}

    def run(self):
        """
        Run the game
        """
        # Only keep players with cards
        playing_players = [
            player
            for player
            in self.players
            if player.has_card()
        ]

        round_count = 0
        while len(playing_players) > 1:
            round_count += 1
            played_cards = []

            # Play round
            for player in playing_players:
                player.play_card()
            playing_players.sort(reverse=True)

            while (
                playing_players[0].score != [-1, -1] and
                playing_players[0].score == playing_players[1].score
            ):
                # Bataille phase
                i = 0
                max_score = playing_players[0].score.copy()
                while (
                    i < len(playing_players) and
                    playing_players[i].score == max_score
                ):
                    player = playing_players[i]
                    if player.has_card():
                        player.discard_card()
                        if player.has_card():
                            player.play_card()
                        else:
                            # Collect cards and mark player as loser
                            played_cards.extend(player.played_cards)
                            player.clear()
                    else:
                        # Collect cards and mark player as loser
                        played_cards.extend(player.played_cards)
                        player.clear()
                    i += 1
                playing_players.sort(reverse=True)

            # Collect played cards
            for player in playing_players:
                played_cards.extend(player.played_cards)
            random.shuffle(played_cards)
            if playing_players[0].score != [-1, -1]:
                playing_players[0].collect_cards(played_cards)

            # Clear scores
            for player in playing_players:
                player.clear()

            # Remove players without cards
            playing_players = [
                player
                for player
                in playing_players
                if player.has_card()
            ]

        # Export results
        if len(playing_players) == 1:
            winner = playing_players[0]
            self.results['winner'] = winner.name
            self.results['round_count'] = round_count
        else:
            self.results['winner'] = None
            self.results['round_count'] = round_count


if __name__ == '__main__':
    # Create a deck of 52 cards and 2 jokers
    deck = Deck(card_count_per_color=13, color_count=4, joker_count=2)
    # Initialize a game with 4 players
    game = Game(deck=deck, player_count=4)
    # Run the game
    game.run()
    # Print results
    round_count = game.results['round_count']
    if game.results['winner'] is not None:
        winner_name = game.results['winner']
        print(f'Winner is {winner_name} in {round_count} rounds')
    else:
        print(f'No winner in {round_count} rounds')
