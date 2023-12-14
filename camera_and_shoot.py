from card_detector import capture_image
from test_shoot import shoot_card
from test_shoot import stop_dc1
from test_shoot import stop_dc2

import time
symbols = ['s', 'c', 'h', 'd']
cards = []

for i in range(4):
    for j in range(1, 14):
        cards.append((symbols[i], j))

def main():
    just = 0 
    for i in range(0, 52):
        captured = capture_image()
        print(cards[i])
        if captured == cards[i]:
            just += 1
        shoot_card()
        time.sleep(1)
    print(just + "/52")
            
try:
    main()
except KeyboardInterrupt: 
    stop_dc1()
    stop_dc2()

