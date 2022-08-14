import collections
import random


class Deck(object):
    def __init__(self, card_count_per_color, color_count, joker_count):
        joker_value = card_count_per_color
        self.cards = (
            list(range(card_count_per_color)) * color_count +
            [joker_value] * joker_count
        )

    def distribute(self, n):
        random.shuffle(self.cards)
        return [self.cards[i::n] for i in range(n)]


class Player(object):
    def __init__(self, name, cards):
        self.name = str(name)
        self.cards = collections.deque(cards)
        self.clear()

    def __lt__(self, other):
        return self.score < other.score

    def clear(self):
        self.played_cards = []
        self.score = [-1, -1]

    def collect_cards(self, cards):
        self.cards.extend(cards)

    def discard_card(self):
        self.played_cards.append(self.cards.popleft())

    def has_card(self):
        return len(self.cards) > 0

    def play_card(self):
        played_card = self.cards.popleft()
        self.played_cards.append(played_card)
        self.score[0] += 1
        self.score[1] = played_card


class Game(object):
    def __init__(self, deck, player_count):
        self.players = [
            Player(f'Player {i}', cards)
            for (i, cards)
            in enumerate(deck.distribute(player_count))
        ]

    def run(self):
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

        # Final message
        if len(playing_players) == 1:
            winner = playing_players[0]
            print(f'Winner is {winner.name} in {round_count} rounds')
        else:
            print(f'No winner in {round_count} rounds')


if __name__ == '__main__':
    # Create a deck of 52 cards and 2 jokers
    deck = Deck(card_count_per_color=13, color_count=4, joker_count=2)
    # Initialize a game with 4 players
    game = Game(deck=deck, player_count=4)
    # Run the game
    game.run()

