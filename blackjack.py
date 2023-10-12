class players:
    def __init__(self,cards):
        self.cards = cards
        self.points = 0
        self.amount_of_aces = 0
        self.add_points()

    def get_card(self,card):
        self.cards.append(card)
        self.add_points()

    def add_points(self):
        points = 0
        amount_of_aces = 0
        for card in self.cards:
            if type(card[1]) is int:
                points += card[1]

            elif card[1] == 'ace':
                amount_of_aces += 1
                points += 11
            else:
                points += 10
        self.points = points
        self.amount_of_aces = amount_of_aces
        self.total_points()

    def total_points(self):
        if self.points > 21:
            if self.amount_of_aces > 0:
                self.points -= 10
                self.amount_of_aces -= 1
                self.total_points()


    def status(self):
        print(self.cards)
        if self.points < 21:
            print(self.points)
        else:
            print('busted')

player1 = players([('harten',2),('schoppen',3)])
player1.get_card(('klaveren',5))
player1.get_card(('klaveren','jack'))

player1.status()

player2 = players([('harten',8),('schoppen','ace')])
player2.get_card(('klaveren',5))
player2.get_card(('klaveren','jack'))

player2.status()
