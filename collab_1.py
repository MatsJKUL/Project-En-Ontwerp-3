import pygame
import os
import sys
import random
import csv
import copy
import argparse
import itertools

import cv2 as cv
import numpy as np
import mediapipe as mp

from model import KeyPointClassifier


DEBUG = True


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)

    args = parser.parse_args()

    return args


args = get_args()

cap_device = args.device
cap_width = args.width
cap_height = args.height

use_static_image_mode = args.use_static_image_mode
min_detection_confidence = args.min_detection_confidence
min_tracking_confidence = args.min_tracking_confidence

use_brect = True


cap = cv.VideoCapture(cap_device)
cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=use_static_image_mode,
    max_num_hands=1,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
)

keypoint_classifier = KeyPointClassifier()

# Read labels ###########################################################
with open('model/keypoint_classifier/keypoint_classifier_label.csv',
          encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [
        row[0] for row in keypoint_classifier_labels
    ]


def recognise_hand():
    while True:
        ret, image = cap.read()
        if not ret:
            continue

        image = cv.flip(image, 1)  # Mirror display

        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        #  ####################################################################
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                landmark_list = calc_landmark_list(image, hand_landmarks)

                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)

                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                confidence = handedness.classification[0].score

                if DEBUG:
                    print(f"Sign id: {hand_sign_id}")
                    print(f"Confidence: {confidence}")

                if confidence < 0.99:
                    print("Confidence not high enough => Trying again")
                    continue

                if hand_sign_id == 3:
                    return 'OK'
                elif hand_sign_id == 4:
                    return 'Peace'
                elif hand_sign_id == 5:
                    return 'Fakjoe'


def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    if key == 104:  # h
        mode = 2
    return number, mode


def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)

    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # Convert to a one-dimensional list
    temp_point_history = list(
        itertools.chain.from_iterable(temp_point_history))

    return temp_point_history


def logging_csv(number, mode, landmark_list, point_history_list):
    if mode == 0:
        pass
    if mode == 1 and (0 <= number <= 9):
        csv_path = 'model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    if mode == 2 and (0 <= number <= 9):
        csv_path = 'model/point_history_classifier/point_history.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *point_history_list])
    return


def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        # Outer rectangle
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                     (0, 0, 0), 1)

    return image


def draw_info_text(image, brect, handedness, hand_sign_text,
                   finger_gesture_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                 (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

    if finger_gesture_text != "":
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2,
                   cv.LINE_AA)

    return (image, hand_sign_text)


def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(image, (point[0], point[1]), 1 + int(index / 2),
                      (152, 251, 152), 2)

    return image


def draw_info(image, fps, mode, number):
    cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 0), 4, cv.LINE_AA)
    cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (255, 255, 255), 2, cv.LINE_AA)

    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                   cv.LINE_AA)
        if 0 <= number <= 9:
            cv.putText(image, "NUM:" + str(number), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                       cv.LINE_AA)
    return image


class Players:
    def __init__(self):
        self.cards = []
        self.points = 0
        self.amount_of_aces = 0
        self.add_points()

    def get_card(self, card):
        self.cards.append(card)
        self.add_points()

    def add_points(self):
        points = 0
        amount_of_aces = 0
        for card in self.cards:
            if card[1] < 11 and 1 < card[1]:
                points += card[1]

            elif card[1] == 1:
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
        return self.cards, self.points


# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
CARD_WIDTH, CARD_HEIGHT = 10, 15
background = (1, 150, 32)

card_images = {}
card_path = 'cards/'  # Create a folder 'cards' and put card images inside
for suit in ['h', 'd', 'c', 's']:
    for rank in range(1, 14):
        card_name = f'{suit}{rank}.png'
        card_images[(suit, rank)] = pygame.image.load(
            os.path.join(card_path, card_name))
back = 'back'
card_images[(back, back)] = pygame.image.load(
    os.path.join(card_path, f'{back}.png'))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack Cards")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Police de texte
font = pygame.font.Font(None, 36)

# Création du bouton Play
# Variable pour le démarrage du code principal
running = False

# Variable pour contrôler la boucle principale
game_start = True

# Police de texte

# Création du bouton Play
play_button = font.render("Play", True, WHITE)
button_hit = font.render("Hit", True, WHITE)
button_double = font.render("Double", True, WHITE)
button_stand = font.render("Stand", True, WHITE)
split = font.render("Split", True, WHITE)
button_again = font.render("Play again", True, WHITE)
button_stop = font.render("Stop", True, WHITE)
play_rect = play_button.get_rect()
hit_rect = button_hit.get_rect()
double_rect = button_double.get_rect()
stand_rect = button_stand.get_rect()
split_rect = split.get_rect()
again_rect = button_again.get_rect()
stop_rect = button_stop.get_rect()
play_rect.center = (WIDTH // 2, HEIGHT // 2)
hit_rect.center = (50, 30)
double_rect.center = (210, 30)
stand_rect.center = (115, 30)
split_rect.center = (260, 30)
again_rect.center = (WIDTH // 2 - 100, HEIGHT // 2)
stop_rect.center = (WIDTH // 2 + 100, HEIGHT // 2)

# Variable pour le démarrage du code principal
game_started = False

# Variable pour le nombre de joueurs
number_of_player = 1

# Variable pour contrôler la boucle principale
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not running:
            # Si le bouton Play est cliqué, démarrez le code principal
            if play_rect.collidepoint(event.pos):
                running = True
        if event.type == pygame.KEYDOWN and not running:
            # Incrémente le nombre de joueurs de 1 à 7 avec les touches numériques
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                number_of_player = int(event.unicode)
    screen.fill(BLACK)

    # Affichage du bouton Play
    if not running:
        screen.blit(play_button, play_rect)
        # Affichage du nombre de joueurs
        text = font.render("How many players : " +
                           str(number_of_player), True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
        screen.blit(text, text_rect)
        pygame.display.update()

    # Code principal (à exécuter après avoir cliqué sur "Play")
    if running:
        # Votre code principal ici
        run = False
        pygame.display.flip()


clock = pygame.time.Clock()
buttons_visible = False
while running:
    screen.fill(background)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Clear the screen
    pygame.display.update()
    clock.tick(30)
    colors = ["h", "d", "c", "s"]
    Waarde = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    cards = {(color, value) for color in colors for value in Waarde}
    deleted_cards = []

    def random_card_choice(cards, deleted_cards):
        random_cards = random.choice(list(cards))
        cards.remove(random_cards)
        deleted_cards.append(random_cards)
        return random_cards

    def hit(player, cards, deleted_cards):
        # in class when code is done
        player.get_card(random_card_choice(cards, deleted_cards))

    def double(player, cards, deleted_cards):
        # in class when code is done
        player.get_card(random_card_choice(cards, deleted_cards))
        # money double

     # int(input("How much players (max 7):  "))
    # gives cards to the players
    Player1 = Players()
    Player2 = Players()
    Player3 = Players()
    Player4 = Players()
    Player5 = Players()
    Player6 = Players()
    Player7 = Players()
    max_players = [Player1, Player2, Player3,
                   Player4, Player5, Player6, Player7]
    players = []
    for i in range(1, number_of_player + 1):
        players.append(max_players[i - 1])
    for number in range(len(players)):
        players[number].get_card(random_card_choice(cards, deleted_cards))
        players[number].get_card(random_card_choice(cards, deleted_cards))
        player_status = players[number].status()

    for number in range(len(players)):
        screen.blit(card_images[players[number].status()[0][0]], ((
            number+1) * WIDTH//(len(players)+1) - 60, 500))
        pygame.display.update()
        clock.tick(30)
        pygame.time.delay(500)
    # gives cards to the dealer
    dealer = Players()
    dealer.get_card(random_card_choice(cards, deleted_cards))
    screen.blit(card_images[dealer.status()[0][0]], (550, 30))
    points = font.render(str(dealer.status()[1]), True, WHITE)
    points_rect = points.get_rect()
    points_rect.center = (600, 180)
    screen.blit(points, points_rect)
    pygame.display.update()
    clock.tick(30)
    for number in range(len(players)):
        points = font.render(str(players[number].status()[1]), True, WHITE)
        points_rect = points.get_rect()
        points_rect.center = ((number + 1) * WIDTH // (len(players) + 1), 650)
        screen.blit(card_images[players[number].status()[0][1]], ((
            number+1) * WIDTH//(len(players)+1) + (len(players[number].status()[0])-1)*30 - 60, 500))
        pygame.draw.rect(screen, background, points_rect)
        screen.blit(points, points_rect)
        pygame.display.update()
        clock.tick(30)
    dealer.get_card(random_card_choice(cards, deleted_cards))
    screen.blit(card_images[(back, back)], (580, 30))
    pygame.display.update()
    clock.tick(30)

    # ask for the move
    busted_player = []

    for number in range(len(players)):
        turn = font.render("YOUR TURN", True, (50, 50, 50))
        turn_rect = turn.get_rect()
        turn_rect.center = ((number + 1) * WIDTH // (len(players) + 1), 450)
        screen.blit(turn, turn_rect)
        pygame.display.update()
        clock.tick(30)
        move = None
        move = recognise_hand()
        pygame.time.delay(1000)
        if move == 'OK':
            run_hit = True
            while run_hit:
                hit(players[number], cards, deleted_cards)
                points = font.render(
                    str(players[number].status()[1]), True, WHITE)
                points_rect = points.get_rect()
                points_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 650)
                player_status = players[number].status()
                screen.blit(card_images[players[number].status()[0][-1]], ((number+1) * WIDTH // (
                    len(players)+1) + (len(players[number].status()[0]) - 1) * 30 - 60, 500))
                pygame.draw.rect(screen, background, points_rect)
                screen.blit(points, points_rect)
                pygame.display.update()
                clock.tick(30)

                if player_status[1] > 21:
                    busted = font.render("BUSTED", True, (255, 50, 50))
                    busted_rect = busted.get_rect()
                    busted_rect.center = (
                        (number + 1) * WIDTH // (len(players) + 1), 680)
                    screen.blit(busted, busted_rect)
                    pygame.display.update()
                    clock.tick(30)
                    busted_player.append(players[number])
                    run_hit = False
                else:
                    move = recognise_hand()
                    pygame.time.delay(1000)
                    if move == 'OK':
                        run_hit = True
                    else:
                        run_hit = False
        elif move == 'Fakjoe':
            double(players[number], cards, deleted_cards)
            points = font.render(
                str(players[number].status()[1]), True, WHITE)
            points_rect = points.get_rect()
            points_rect.center = (
                (number + 1) * WIDTH // (len(players) + 1), 650)
            pygame.draw.rect(screen, background, points_rect)
            screen.blit(points, points_rect)
            pygame.display.update()
            clock.tick(30)
            player_status = players[number].status()
            screen.blit(card_images[players[number].status()[0][-1]], ((number + 1) * WIDTH // (
                len(players) + 1) + (len(players[number].status()[0]) - 1) * 30 - 60, 500))
            if player_status[1] > 21:
                busted = font.render("BUSTED", True, (255, 50, 50))
                busted_rect = busted.get_rect()
                busted_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 680)
                screen.blit(busted, busted_rect)
                busted_player.append(players[number])
            else:
                points = font.render(
                    str(players[number].status()[1]), True, WHITE)
                points_rect = points.get_rect()
                points_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 650)
                pygame.draw.rect(screen, background, points_rect)
                screen.blit(points, points_rect)
        pygame.display.update()
        clock.tick(30)
        pygame.draw.rect(screen, background, turn_rect)

    # Dealer game
    dealer_takes_card = True
    dealer_busted = False
    screen.blit(card_images[dealer.status()[0][1]], (580, 30))
    points = font.render(str(dealer.status()[1]), True, WHITE)
    points_rect = points.get_rect()
    points_rect.center = (600, 180)
    pygame.draw.rect(screen, background, points_rect)
    screen.blit(points, points_rect)
    pygame.display.update()
    clock.tick(30)
    while dealer_takes_card:
        dealer_score = dealer.status()[1]
        if dealer_score > 21:
            busted = font.render("BUSTED", True, (255, 50, 50))
            busted_rect = busted.get_rect()
            busted_rect.center = (600, 210)
            screen.blit(busted, busted_rect)
            dealer_busted = True
            dealer_takes_card = False
        elif dealer_score >= 17:
            dealer_takes_card = False
        else:
            dealer.get_card(random_card_choice(cards, deleted_cards))
            screen.blit(card_images[dealer.status()[0][-1]],
                        (550 + (len(dealer.status()[0]) - 1) * 30, 30))
            points = font.render(str(dealer.status()[1]), True, WHITE)
            points_rect = points.get_rect()
            points_rect.center = (600, 180)
            pygame.draw.rect(screen, background, points_rect)
            screen.blit(points, points_rect)
            dealer_score = dealer.status()[1]
        pygame.display.update()
        clock.tick(30)
    # Score players
    if dealer_busted == False:
        for number in range(len(players)):
            print('score player en dealer')
            print(players[number].status()[1])
            print(dealer_score)
            if players[number] in busted_player:
                pass
            elif players[number].status()[1] > dealer_score:
                you_win = font.render("YOU WON", True, WHITE)
                you_win_rect = you_win.get_rect()
                you_win_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 680)
                screen.blit(you_win, you_win_rect)
            elif players[number].status()[1] == dealer_score:
                push = font.render("PUSH", True, WHITE)
                push_rect = push.get_rect()
                push_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 680)
                screen.blit(push, push_rect)
            else:
                you_lose = font.render("YOU LOST", True, WHITE)
                you_lose_rect = you_lose.get_rect()
                you_lose_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 680)
                screen.blit(you_lose, you_lose_rect)
        pygame.display.update()
        clock.tick(30)
    if dealer_busted is True:
        for number in range(len(players)):
            if players[number] not in busted_player:
                you_win = font.render("YOU WON", True, WHITE)
                you_win_rect = you_win.get_rect()
                you_win_rect.center = (
                    (number + 1) * WIDTH // (len(players) + 1), 680)
                screen.blit(you_win, you_win_rect)

    play_again = True
    cards.update((deleted_cards))
    screen.blit(button_again, again_rect)
    screen.blit(button_stop, stop_rect)
    pygame.display.update()
    clock.tick(30)
    while play_again:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and play_again:
                if again_rect.collidepoint(event.pos):
                    running = True
                elif stop_rect.collidepoint(event.pos):
                    running = False
                    cap.release()
                    pygame.quit()
                    sys.exit()
                pygame.draw.rect(screen, background, again_rect)
                pygame.draw.rect(screen, background, stop_rect)
                pygame.display.update()
                clock.tick(30)
                play_again = False
