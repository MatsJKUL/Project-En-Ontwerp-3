def calculate_win_probability(player_cards, dealer_cards, player_point, dealer_point, remaining_deck):
    # Create a dictionary to count the occurrences of each card rank in the remaining deck
    card_dict = dict()
    for card in remaining_deck:
        rank = card[0]
        if rank not in card_dict:
            card_dict[rank] = 1
        else:
            card_dict[rank] += 1

    # Calculate the probability of the player going bust (going over 21)
    bust_probability = 0
    for card_rank in card_dict:
        if player_point + card_values[card_rank] > 21:
            bust_probability += card_dict[card_rank] / len(remaining_deck)

    # Calculate the probability of the player getting a blackjack (21 points with 2 cards)
    blackjack_probability = 0
    if len(player_cards) == 2 and player_point == 21:
        blackjack_probability = 1

    # Calculate the probability of the player winning by comparing to the dealer's final hand
    win_probability = 0
    if player_point <= 21:
        while dealer_point < 17:
            # Dealer hits until they have 17 or more points
            for card_rank in card_dict:
                if dealer_point + card_values[card_rank] <= 21:
                    win_probability += (card_dict[card_rank] / len(remaining_deck)) * dealer_win_probability(dealer_point + card_values[card_rank])

    # Calculate the overall chance of winning
    total_win_probability = (1 - bust_probability) * blackjack_probability + (1 - bust_probability) * win_probability

    return total_win_probability

# Example card values (you may define your own values)
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def dealer_win_probability(dealer_point):
    if dealer_point > 21:
        return 0
    elif dealer_point == 21:
        return 100
    elif dealer_point < 17:
        return 0
    else:
        return 100

# Example usage
player_cards = [('A', 'Spades'), ('9', 'Hearts')]
dealer_cards = [('K', 'Diamonds'), ('7', 'Clubs')]
player_point = 20
dealer_point = 17
remaining_deck = [('2', 'Clubs'), ('3', 'Hearts'), ('4', 'Diamonds')]

win_probability = calculate_win_probability(player_cards, dealer_cards, player_point, dealer_point, remaining_deck)
print(f"Player's chance of winning: {win_probability:.2f}%")
