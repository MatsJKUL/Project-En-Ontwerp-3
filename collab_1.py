import pygame
#import pigpio
from pygame.locals import *
import os
import random
import csv
import copy
import argparse
import itertools
import cv2 as cv
import numpy as np
import mediapipe as mp
from model import KeyPointClassifier
#import RPi.GPIO as GPIO
import time
from card_detector import capture_image
import cv2

DEBUG = False

####################    MOTOR AND LIMIT_SWITCH   ##########################
'''GPIO.setmode(GPIO.BCM) #setup motors
servo1_pin = 14
servo2_pin = 15
dc1_pin = 17
dc2_pin = 18
switch_pin = 27
switched = 0

current_pos_1 = 0
current_pos_2 = 0

pwm1 = pigpio.pi(port=30000)

pwm1.set_mode(servo1_pin, pigpio.OUTPUT)
pwm1.set_mode(servo2_pin, pigpio.OUTPUT)

pwm1.set_PWM_frequency(servo1_pin, 50)
pwm1.set_PWM_frequency(servo2_pin, 50)

GPIO.setup(dc1_pin, GPIO.OUT)
GPIO.setup(dc2_pin, GPIO.OUT)
GPIO.setup(switch_pin, GPIO.OUT)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #setup limit_switch
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setmode(GPIO.BCM)  # Set the GPIO mode to use the BCM numbering
print("init pins")

def turn_dc1():
    print('turndc1')
    GPIO.output(dc1_pin, GPIO.HIGH)

def stop_dc1():
    GPIO.output(dc1_pin, GPIO.LOW)

def turn_dc2():
    print('dc2')
    GPIO.output(dc2_pin, GPIO.HIGH)
    print("turned")

def switch_dc2():
    global switched 
    print("switch")
    if switched == 0:
        GPIO.output(switch_pin, GPIO.HIGH)
        switched = 1
    elif switched == 1:
        GPIO.output(switch_pin, GPIO.LOW)
        switched = 0


def stop_dc2():
    GPIO.output(dc2_pin, GPIO.LOW)

def turn_servo2(angle):
    global current_pos_2
    print('turnservo2')

    if angle > current_pos_2:
        print("FORWARD")
        for i in range(int(current_pos_2), int(angle) + 1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(.01)

    elif angle < current_pos_2:
        print("BACK")
        for i in range(int(current_pos_2), int(angle) + 1, -1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo2_pin, pulsewidth)
            time.sleep(.01)
    current_pos_2 = angle

def turn_servo1(angle):
    global current_pos_1
    print('turnservo1')
    if angle > current_pos_1:
        print("FORWARD")
        for i in range(int(current_pos_1), int(angle) + 1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo1_pin, pulsewidth)
            time.sleep(.01)

    elif angle < current_pos_1:
        print("BACK")
        for i in range(int(current_pos_1), int(angle) + 1, -1):
            pulsewidth =  2000*i/270 + 500 # Map the angle to the duty cycle
            pwm1.set_servo_pulsewidth(servo1_pin, pulsewidth)
            time.sleep(.01)

    current_pos_1 = angle

def servo_stop():
    pwm1.set_PWM_dutycycle(servo1_pin, 0)
    pwm1.set_PWM_dutycycle(servo2_pin, 0)
    pwm1.set_PWM_frequency(servo1_pin, 0)
    pwm1.set_PWM_frequency(servo2_pin, 0)

<<<<<<< HEAD
def shoot_card():
    turn_dc1()
    print("shoot")
=======
def #shoot_card():
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
    turn_dc2()
    print("pre sleep")
    time.sleep(0.3)
    print("sleep 1.5")
    stop_dc2()
    switch_dc2()
    time.sleep(0.5)
    turn_dc2()
    time.sleep(1)
    stop_dc2()
    time.sleep(0.1)
<<<<<<< HEAD
    switch_dc2()
    stop_dc1()
    print("end")
    time.sleep(0.5)
=======
    stop_dc2()
    switch_dc2()'''
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
####################    MOTOR AND LIMIT_SWITCH   ##########################
######################### RECOGNISION   ##########################
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

with open('model/keypoint_classifier/keypoint_classifier_label.csv',
      encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [
        row[0] for row in keypoint_classifier_labels
    ]


def recognise_hand():
    print('recognize_hand')
    icount = 0
    while True:
        hand_sign_id = None
        for i in range(5):
            cap.grab()
        ret, image = cap.read()
        if not ret:
            continue

        icount += 1
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
                print(hand_sign_id)

                if DEBUG:
                    print(f"Sign id: {hand_sign_id}")
                    print(f"Confidence: {confidence}")

                if confidence < 0.80:
                    print("Confidence not high enough => Trying again")
                    continue

                if hand_sign_id == 3:
                    print('OK')
                    return 'OK'
                elif hand_sign_id == 4:
                    print('peace')
                    return 'Peace'
                elif hand_sign_id == 0:
                    print('phone')
                    return 'Phone'
                if hand_sign_id == 1:
                    print('Thumb')
                    return 'Thumb'

    cap.release()

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
    print("switched")
    print("switched")
    print("switched")

    return temp_landmark_list
####################    HAND RECOGNISION   ##########################

####################    PLAYER   ##########################

class Player:
    def __init__(self, num, bet, name):
        self.cards = []
        self.bet = bet
        self.points = 0
        self.amount_of_aces = 0
        self.number = num
        self.name = name
        self.add_points()
        self.hand_amount = 1
        self.state = ''

    '''def get_bet(self):
        print('get_bet')
        move = None
        pygame.font.Font(None, 36).render(f"PLACE YOUR BET {self.name}", True, (50, 50, 50))
        while move != 'OK':
            if GPIO.input(21) == 1:
                self.bet.append(5)
                print('bet veranderd')
                move = recognise_hand()
            elif GPIO.input(20) == 1:
                self.bet.append(10)
                print('bet veranderd')
                move = recognise_hand()
<<<<<<< HEAD
        if self.bet >= 0:
            print("BET = " + self.bet)
            print("YAY")
=======
        if len(self.bet) == 0:
            self.get_bet()'''
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac

    def get_total_bet(self):
        return sum(self.bet)


    def get_card(self, card):
        self.cards.append(card)
        self.add_points()

    def add_points(self):
        points = 0
        amount_of_aces = 0
        for card in self.cards:
            print(card[1])
            if int(card[1]) < 11 and 1 < int(card[1]):
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

    def get_cards(self):
        return self.cards

    def get_card_by_index(self, i):
        try:
            card = self.cards[i]
        except:
            print("NOT A VALID CARD INDEX, returning first card")
            card = self.cards[0]

        return card

    def get_points(self):
        return self.points

    def get_card_amount(self):
        return len(self.cards)

    def get_winst(self, game_state):
        if self.state == 'BUSTED':
            return -self.get_total_bet()
        elif self.state == 'PUSH':
            return 0
        elif self.state == 'WIN':
            for i in self.bet:
                if i == 10:
                    turn_servo2(0)
                    turn_servo2(90)
                if i == 5:
                    turn_servo2(180)
                    turn_servo2(90)
            return 2*self.get_total_bet()

    def display_player_cards(self, game, pos):
        self.add_points()
        pts = self.get_points()
        points = game.font.render(
            str(pts), True, game.white)
        points_rect = points.get_rect()
        points_rect.center = ((pos + 1) * game.screen_width //
                              (game.max_cards_on_screen + 1), 685)

        if (pts > 21):
            game.render_bust(pos)

        pygame.draw.rect(game.screen, game.background, points_rect)
        game.screen.blit(points, points_rect)

        name = game.font.render(
            str(f"{self.name}"), True, game.white)

        name_rect = name.get_rect()
        name_rect.center = ((pos + 1) * game.screen_width //
                            (game.max_cards_on_screen + 1), 650)

        pygame.draw.rect(game.screen, game.background, name_rect)
        game.screen.blit(name, name_rect)

        for i in range(self.get_card_amount()):
            game.screen.blit(game.card_images[self.get_card_by_index(i)], ((
                pos+1) * game.screen_width//(game.max_cards_on_screen+1) +
                (i) * 30 - 60, 500))

        pygame.display.update()
        game.clock.tick(30)
    ####################    PLAYER   ##########################


class GameState:
    ####################    INITIALISING   ##########################
    def __init__(self):
        pygame.init()
        print("init game")

        self.screen_width, self.screen_height = 1200, 800
        self.font = pygame.font.Font(None, 36)
        self.font2 = pygame.font.Font(None, 30)
        self.background = (1, 150, 32)

        self.min_bet = [5]
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("Blackjack self.cards")

        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        self.faces = ['h', 'd', 'c', 's']
        self.values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.sounds = {}

        self.sounds['0'] = pygame.mixer.Sound("sounds/0.mp3")
        self.sounds['1'] = pygame.mixer.Sound("sounds/1.mp3")
        self.sounds['2'] = pygame.mixer.Sound("sounds/2.mp3")
        self.sounds['3'] = pygame.mixer.Sound("sounds/3.mp3")
        self.sounds['DETECT'] = pygame.mixer.Sound("sounds/DETECT.mp3")
        self.sounds['PHONE'] = pygame.mixer.Sound("sounds/FAKJOE.mp3")
        self.sounds['HIT'] = pygame.mixer.Sound("sounds/HIT.mp3")
        self.sounds['DOUBLE'] = pygame.mixer.Sound("sounds/DOUBLE.mp3")
        self.sounds['STAND'] = pygame.mixer.Sound("sounds/PEACE.mp3")
        self.sounds['BUST'] = pygame.mixer.Sound("sounds/BUST.mp3")
        self.sounds['CRASH'] = pygame.mixer.Sound("sounds/CRASH.mp3")
        self.sounds['tutorial_start'] = pygame.mixer.Sound("sounds/start_tutorial.mp3")
        self.sounds['tutorial_hit'] = pygame.mixer.Sound("sounds/tutorial_hit.mp3")
        self.sounds['tutorial_double'] = pygame.mixer.Sound("sounds/tutorial_double.mp3")
        self.sounds['tutorial_stand'] = pygame.mixer.Sound("sounds/tutorial_stand.mp3")
        self.sounds['tutorial_split'] = pygame.mixer.Sound("sounds/tutorial_split.mp3")
        self.sounds['tutorial_end'] = pygame.mixer.Sound("sounds/tutorial_end.mp3")

        self.max_cards_on_screen = 3
        self.clock = pygame.time.Clock()
        print("init buttons")
        self.init_buttons()
        print("plat_game")
        #play_game = self.game_or_tutorial()
        play_game = True
        print("PLAY RET", play_game)
        while play_game:
            self.run_game()
            play_game = self.display_again_screen()
        if play_game is False:
            self.run_tutorial()
            GameState()
        stop_dc1()
        cap.release()
        pygame.quit()
        servo_stop()
        quit()


    def init_cards(self):
        self.card_images = {}
        self.cards = []
        self.deleted_cards = []

        card_path = 'cards/'
        for face in ['h', 'd', 'c', 's']:
            for value in range(1, 14):
                card_name = f'{face}{value}'
                self.cards.append((face, value))

                card_image_name = card_name + '.png'
                self.card_images[(face, value)] = pygame.image.load(
                    os.path.join(card_path, card_image_name))
        self.back = 'back'
        self.card_images[(self.back, self.back)] = pygame.image.load(
            os.path.join(card_path, f'{self.back}.png'))
    def init_players(self):
        print('initPlayer')
        self.player_nums = {}
        self.players = []
        bet = [0]
        for i in range(self.player_amount):
            print("PLAYER:", i)
            self.player_nums[i+1] = Player(i+1, bet, f"Player {i+1}")
            self.players.append(self.player_nums[i+1])
        angle = 270 / (self.player_amount + 1)
        for number in range(self.player_amount):
            print("NUMBER", number)
            player = self.players[number]
<<<<<<< HEAD
            shoot_card()
            print("get_card")
            player.get_card(self.random_card_choice())
            print("got card")
            turn_servo1(angle*number)
            print("final turn")
        turn_servo1(269)
        print("second turn")
=======
            #shoot_card()
            player.get_card(self.random_card_choice())
            #self.turn_servo1(angle*number)
        #self.turn_servo1(270)
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
        self.dealer = Player('d', [], 'dealer')
        #shoot_card()
        self.dealer.get_card(self.random_card_choice())
<<<<<<< HEAD
        turn_servo1(0)
        for number in range(self.player_amount):
            player = self.players[number]
            shoot_card()
            time.sleep(0.2)
            player.get_card(self.random_card_choice())
            turn_servo1(angle * number)
        turn_servo1(270)
        self.dealer.get_card(self.random_card_choice())
        shoot_card()
        turn_servo1(0)
=======
        #self.turn_servo1(0)
        for number in range(self.player_amount):
            player = self.players[number]
            #shoot_card()
            player.get_card(self.random_card_choice())
            #self.turn_servo1(angle * number)
        #self.turn_servo1(270)
        self.dealer.get_card(self.random_card_choice())
        #shoot_card()
        #self.turn_servo1(0)
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
        for number in range(self.player_amount):
            player = self.players[number]
            self.screen.blit(
                self.card_images[self.dealer.get_card_by_index(0)], (550, 30))
            self.screen.blit(
                self.card_images[(self.back, self.back)], (580, 30))
            player.display_player_cards(self, 1)
            pygame.display.update()
            self.clock.tick(30)
            #player.get_bet()
            self.screen.fill(self.background)
<<<<<<< HEAD
            turn_servo1(angle * number)
        print("NEXT")
=======
            #self.turn_servo1(angle * number)
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
        for number in range(0,2):
            player = self.players[number]
            player.display_player_cards(self, number + 1)
        self.screen.blit(
            self.card_images[self.dealer.get_card_by_index(0)], (550, 30))
        self.screen.blit(
            self.card_images[(self.back, self.back)], (580, 30))
<<<<<<< HEAD
        turn_servo1(0)
=======
        #self.turn_servo1(0)

>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
    def init_buttons(self):
        self.play_button = self.font.render("Play", True, self.white)
        self.button_game = self.font.render("Game", True, self.white)
        self.button_tutorial = self.font.render("Tutorial", True, self.white)
        self.button_hit = self.font.render("Hit", True, self.white)
        self.button_double = self.font.render("Double", True, self.white)
        self.button_stand = self.font.render("Stand", True, self.white)
        self.split = self.font.render("Split", True, self.white)
        self.button_again = self.font.render("Play again", True, self.white)
        self.button_stop = self.font.render("Stop", True, self.white)
        self.min_bet_txt = self.font.render(
            f"MINIMUM Bet: ${self.min_bet[0]}", True, self.white)
        self.bet_txt = self.font.render( f"Place you bet", True, self.white)

        self.play_rect = self.play_button.get_rect()
        self.game_rect = self.button_game.get_rect()
        self.tutorial_rect = self.button_tutorial.get_rect()
        self.hit_rect = self.button_hit.get_rect()
        self.double_rect = self.button_double.get_rect()
        self.stand_rect = self.button_stand.get_rect()
        self.split_rect = self.split.get_rect()
        self.again_rect = self.button_again.get_rect()
        self.stop_rect = self.button_stop.get_rect()
        self.min_bet_rect = self.min_bet_txt.get_rect()
        self.bet_txt_rect = self.bet_txt.get_rect()

        self.play_rect.center = (self.screen_width // 2, self.screen_height // 2)
        self.game_rect.center = (self.screen_width // 2 +
                                100, self.screen_height // 2)
        self.tutorial_rect.center = (self.screen_width // 2 -
                                100, self.screen_height // 2)
        self.hit_rect.center = (50, 30)
        self.double_rect.center = (210, 30)
        self.stand_rect.center = (115, 30)
        self.split_rect.center = (260, 30)
        self.again_rect.center = (self.screen_width // 2 -
                                  100, self.screen_height // 2)
        self.stop_rect.center = (self.screen_width // 2 +
                                 100, self.screen_height // 2)
        self.min_bet_rect.center = (125, 40)
        self.bet_txt_rect.center = (165,40)

    def game_or_tutorial(self):
        while True:
            self.screen.fill(self.black)
            self.screen.blit(self.button_game, self.game_rect)
            self.screen.blit(self.button_tutorial, self.tutorial_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_rect.collidepoint(event.pos):
                        pygame.display.flip()
                        pygame.display.update()

                        return True
                    elif self.tutorial_rect.collidepoint(event.pos):
                        print("TUTORIAL")
                        pygame.display.flip()
                        pygame.display.update()
                        return False
            pygame.display.update()
    def game_options(self):
        player_amount = 1

        while True:
            self.screen.fill(self.black)
            self.screen.blit(self.play_button, self.play_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_rect.collidepoint(event.pos):
                        pygame.display.flip()
                        self.player_amount = player_amount
                        return

                elif event.type == pygame.KEYDOWN and event.key == K_RETURN:
                    pygame.display.flip()
                    self.player_amount = player_amount
                    return

                elif event.type == pygame.KEYDOWN:
                    key = self.get_number_of_players(event)

                    if key is not None and type(key) == int:
                        player_amount = key

            self.display_player_number(player_amount)
    def init_game(self):
        print('init_game')
        self.init_buttons()
        self.init_cards()
        self.game_options()
        self.screen.fill(self.background)
        self.screen.blit(self.min_bet_txt, self.min_bet_rect)
        pygame.display.update()
        self.clock.tick(30)
        self.init_players()
        pygame.display.update()
        self.clock.tick(30)
    ####################    INITIALISING   ##########################

    ####################    POSSIBLE MOVES   ##########################
    def handle_move(self, move, player, pos):
        if move == 'OK':
            print("RUNNING HIT")
            self.hit(player)
            self.render_hit(player, pos)
            player_points = player.get_points()

            if player_points > 21:
                self.render_bust(pos)
                time.sleep(.5)
                pygame.mixer.Sound.play(self.sounds["BUST"])
                pygame.mixer.Sound.play(self.sounds["CRASH"])
                self.busted_players.append(player)
                return "STOP"
            else:
                return "CONTINUE"
        elif move == "Phone":
            if player.cards[0][1] != player.cards[1][1] and len(player.cards) == 2:
                move = recognise_hand()
                return self.handle_move(move, player, pos)
            else:
                new_player = Player(player.number, self.min_bet,
                                    player.name + "-" + str(player.hand_amount))
                player.hand_amount += 1
                new_player.cards = [player.cards[1]]
                #shoot_card()
                new_player.get_card(self.random_card_choice())
                player.cards = [player.cards[0]]
                #shoot_card()
                player.get_card(self.random_card_choice())
                self.players.insert(
                    player.number + player.hand_amount - 2, new_player)
                self.player_amount += 1
                self.render_cards_on_screen(player.number - 1)

        elif move == 'Thumb':
            self.double(player)
            self.render_double(player, pos)
            player_points = player.get_points()

            if player_points > 21:
                self.render_bust(pos)
                time.sleep(.5)
                pygame.mixer.Sound.play(self.sounds["BUST"])
                pygame.mixer.Sound.play(self.sounds["CRASH"])
                self.busted_players.append(player)
            return "STOP"

        elif move.upper() == 'PEACE':
            self.render_move("STAND")
            return 'STOP'

    def hit(self,player):
        #shoot_card()
        player.get_card(self.random_card_choice())

    def double(self,player):
        #shoot_card()
        player.get_card(self.random_card_choice())
    ####################    POSSIBLE MOVES   ##########################


    ####################    DISPLAYS    ##########################
    def render_move(self, txt): #displays the chosen move
        pygame.mixer.music.stop()
        f = pygame.font.Font(None, 50)
        hit_popup = f.render(txt, True, (255, 0, 0))
        hit_popup_rect = hit_popup.get_rect()
        hit_popup_rect.center = (
            int(self.screen_width/2), int(self.screen_height/2))

        pygame.draw.rect(
            self.screen, self.background, hit_popup_rect)
        self.screen.blit(hit_popup, hit_popup_rect)

        pygame.display.update()
        self.clock.tick(30)

        pygame.mixer.Sound.play(self.sounds[txt.upper()])
    def render_hit(self, player, pos):
        points = self.font.render(str(player.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (
            (pos+1)*self.screen_width//(self.max_cards_on_screen + 1), 685)

        card_image = self.card_images[player.get_card_by_index(-1)]
        image_point = (self.calc_next_card_pos(player, pos), 500)
        self.screen.blit(card_image, image_point)

        pygame.draw.rect(
            self.screen, self.background, points_rect)
        self.screen.blit(points, points_rect)

        self.render_move("HIT")
        pygame.display.update()
        self.clock.tick(30)
    def render_double(self,player, pos):
        points = self.font.render(str(player.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (
            (pos + 1) * self.screen_width // (self.max_cards_on_screen + 1), 685)

        card_image = self.card_images[player.get_card_by_index(-1)]
        image_point = (self.calc_next_card_pos(player, pos), 500)
        self.screen.blit(card_image, image_point)

        pygame.draw.rect(
            self.screen, self.background, points_rect)
        self.screen.blit(points, points_rect)

        self.render_move("DOUBLE")

        pygame.display.update()
        self.clock.tick(30)
    def display_player_number(self, player_amount):
        text = self.font.render("How many players: " +
                                str(player_amount), True, self.white)
        text_rect = text.get_rect()
        text_rect.center = (self.screen_width // 2,
                            self.screen_height // 2 + 50)
        self.screen.blit(text, text_rect)
        pygame.display.update()
    def display_game_over(self, text, number, color=(255, 255, 255)):
        player = self.players[number]
        name = self.font2.render(
            str(f"{player.name}"), True, self.white)
        name_rect = name.get_rect()
        name_rect.center = ((number + 1) * self.screen_width //
                            (self.player_amount + 1), 650)

        pygame.draw.rect(self.screen, self.background, name_rect)
        self.screen.blit(name, name_rect)

        text = self.font2.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.center = (
            (number + 1) * self.screen_width // (self.player_amount + 1), 680)
        self.screen.blit(text, text_rect)

        points = self.font2.render(
            "POINTS" + str(player.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.topleft = (
            (number + 1) * self.screen_width // (self.player_amount + 1) - 10, 600)
        self.screen.blit(points, points_rect)

        inzet = self.font2.render("BET: " + str(
            player.get_total_bet()), True, self.white)
        inzet_rect = inzet.get_rect()
        inzet_rect.topleft = (
            (number + 1) * self.screen_width // (self.player_amount + 1) - 10, 500)
        self.screen.blit(inzet, inzet_rect)

        winst = self.font2.render("WINST: " + str(
            player.get_winst(self)), True, self.white)
        winst_rect = winst.get_rect()
        winst_rect.topleft = (
            (number + 1) * self.screen_width // (self.player_amount + 1) - 10, 550)
        self.screen.blit(winst, winst_rect)

    def render_bust(self, pos):
        busted = self.font.render(
            "BUSTED", True, (255, 50, 50))
        busted_rect = busted.get_rect()
        busted_rect.center = (
            (pos + 1) * self.screen_width // (self.max_cards_on_screen + 1), 720)
        self.screen.blit(busted, busted_rect)
        pygame.display.update()
        self.clock.tick(30)

    def clear_move(self):
        f = pygame.font.Font(None, 50)
        clear = f.render("AAAAAAAAAAAAAAAAAAAAAAAAAAA",
                         True, self.background)
        clear_rect = clear.get_rect()
        clear_rect.center = (
            int(self.screen_width/2), int(self.screen_height/2))

        pygame.draw.rect(
            self.screen, self.background, clear_rect)
        self.screen.blit(clear, clear_rect)
        pygame.display.update()

    def clear_cards(self):
        rect = pygame.Rect((150, 400), (self.screen_width - 300, 350))
        pygame.draw.rect(self.screen, self.background, rect)
        pygame.display.update()

    def display_count(self, txt):
        f = pygame.font.Font(None, 80)
        count = f.render(txt, True, self.white)
        count_rect = count.get_rect()
        count_rect.center = (self.screen_width - 200, 150)
        pygame.mixer.Sound.play(self.sounds[txt])
        pygame.draw.rect(
            self.screen, (255, 0, 0), count_rect)
        self.screen.blit(count, count_rect)
        pygame.display.update()
        time.sleep(1)
        pygame.mixer.music.stop()

    def render_cards_on_screen(self, number):
        self.clear_cards()
        for i in range(-1, 2):
            if number + i <= self.player_amount - 1 and number + i >= 0:
                player = self.players[number + i]
                player.display_player_cards(self, i + 1)

    def display_again_screen(self):
        self.screen.blit(self.button_again, self.again_rect)
        self.screen.blit(self.button_stop, self.stop_rect)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.again_rect.collidepoint(event.pos):
                        return True
                    elif self.stop_rect.collidepoint(event.pos):
                        return False

    def display_count_down(self, number):
        player = self.players[number]
        f = pygame.font.Font(None, 50)
        count = f.render(f"Get ready {player.name}!", True, self.white)
        count_rect = count.get_rect()
        count_rect.center = (self.screen_width - 200, 80)

        rect = pygame.Rect((self.screen_width - 350, 115), (300, 70))
        pygame.draw.rect(self.screen, (255, 0, 0), rect)
        pygame.display.update()

        pygame.draw.rect(
            self.screen, self.background, count_rect)
        self.screen.blit(count, count_rect)
        pygame.display.update()

        for i in range(3, -1, -1):
            self.display_count(str(i))
        self.display_count("DETECT")

    def display_score(self):
        self.clear_cards()
        dealer_score = self.dealer.get_points()
        for number in range(self.player_amount):
            player = self.players[number]
            player_score = player.get_points()
            if player in self.busted_players:
                player.state = 'BUSTED'
                self.display_game_over("BUSTED", number, (255, 0, 0))
                continue
            elif dealer_score > 21:
                player.state = 'WIN'
                self.display_game_over("YOU WON", number)
            elif player_score > dealer_score:
                player.state = 'WIN'
                self.display_game_over("YOU WON", number)
            elif player_score == dealer_score:
                player.state = 'PUSH'
                self.display_game_over("PUSH", number)
            else:
                player.state = 'BUSTED'
                self.display_game_over("YOU LOST", number)
            pygame.display.update()
            self.clock.tick(30)
    ####################    DISPLAYS    ##########################

    ####################    HELPER FUNCTIONS    ##########################
    def calc_next_card_pos(self, player, player_num):
        return (player_num + 1) * self.screen_width // (self.max_cards_on_screen + 1) + (player.get_card_amount() - 1) * 30 - 60

    def random_card_choice(self):
        random_cards = capture_image()
        return random_cards
    def get_number_of_players(self, event):
        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7] and event.unicode.isdigit():
            return int(event.unicode)
    ####################    HELPER FUNCTIONS    ##########################
    def run_tutorial(self):
        self.player_amount = 4
        self.init_buttons()
        self.init_cards()
        self.screen.fill(self.background)
        self.screen.blit(
            self.card_images[self.dealer.get_card_by_index(0)], (550, 30))
        self.screen.blit(
            self.card_images[(self.back, self.back)], (580, 30))
        pygame.display.update()
        self.clock.tick(30)
        self.players = []
        for i in range(0,4):
            player = Player(i + 1, [5], f"Player {i + 1}")
            self.players.append(player)
            if i == 0:
                self.players[-1].cards = [('d', 7),('h', 6)]
            elif i == 1:
                self.players[-1].cards = [('s', 10), ('c', 4)]
            elif i == 2:
                self.players[-1].cards = [('h', 'j'), ('d', 1)]
            elif i == 3:
                self.players[-1].cards = [('h', 10), ('d', 10)]
            self.dealer = Player('d', [], 'dealer')
            self.dealer.cards = [('h',1),('s',2)]
            if i >= 0 and i < 2:
                self.players[i].display_player_cards(self, i + 1)
        number = 0
        while True:
            if number < self.player_amount:
                player = self.players[number]
                self.render_cards_on_screen(number)
                turn = self.font.render(
                    f"YOUR TURN {player.name}", True, (50, 50, 50))
                turn_rect = turn.get_rect()
                turn_rect.center = (2 * self.screen_width //
                                    (self.max_cards_on_screen + 1), 450)
                self.screen.blit(turn, turn_rect)
                pygame.display.update()
                self.clock.tick(30)
                pygame.mixer.Sound.play(self.sounds["tutorial_start"])
                play = "CONTINUE"
                while play != "STOP":
                    self.display_count_down(number)
                    move = None
                    if number == 0:
                        pygame.mixer.Sound.play(self.sounds["tutorial_hit"])
                        while move != 'OK':
                            move = recognise_hand()
                        self.render_hit(player,1)
                    if number == 1:
                        pygame.mixer.Sound.play(self.sounds["tutorial_double"])
                        while move != 'Thumb':
                            move = recognise_hand()
                        self.render_double(player, 1)
                    if number == 2:
                        pygame.mixer.Sound.play(self.sounds["tutorial_stand"])
                        while move != 'Peace':
                            move = recognise_hand()
                    if number == 3:
                        pygame.mixer.Sound.play(self.sounds["tutorial_split"])
                        while move != 'Phone':
                            move = recognise_hand()
                        new_player = Player(player.number, self.min_bet,
                                            player.name + "-" + str(player.hand_amount))
                        player.hand_amount += 1
                        new_player.cards = [player.cards[1]]
                        new_player.get_card(self.random_card_choice())
                        player.cards = [player.cards[0]]
                        player.get_card(self.random_card_choice())
                        self.players.insert(
                            player.number + player.hand_amount - 2, new_player)
                        self.player_amount += 1
                        self.render_cards_on_screen(player.number - 1)
                    pygame.mixer.Sound.play(self.sounds["tutorial_end"])
                    time.sleep(1)
                    self.clear_move()
                pygame.display.update()
                self.clock.tick(30)
                pygame.draw.rect(self.screen, self.background, turn_rect)
                number += 1
            else:
                break


    def run_game(self):
<<<<<<< HEAD
        print("predc")
        print("TURNING")
=======
        #turn_dc1()
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
        self.init_game()
        print("init the game")
        self.busted_players = []
        number = 0
        angle = 270/self.player_amount
        while True:
            if number < self.player_amount:
                player = self.players[number]
                self.render_cards_on_screen(number)
                turn = self.font.render(
                    f"YOUR TURN {player.name}", True, (50, 50, 50))
                turn_rect = turn.get_rect()
                turn_rect.center = (2 * self.screen_width //
                                    (self.max_cards_on_screen + 1), 450)
                self.screen.blit(turn, turn_rect)
                pygame.display.update()
                self.clock.tick(30)
                play = "CONTINUE"
                while play != "STOP":
                    self.display_count_down(number)
                    move = recognise_hand()
                    play = self.handle_move(move, player, 1)
                    time.sleep(1)
                    self.clear_move()

                pygame.display.update()
                self.clock.tick(30)
                pygame.draw.rect(self.screen, self.background, turn_rect)
<<<<<<< HEAD
                turn_servo1(angle*number)
                number += 1
            else:
                turn_servo1(270)
=======
                #self.turn_servo1(angle*number)
                number += 1
            else:
                #self.turn_servo1(270)
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
                break
        dealer_takes_card = True
        self.screen.blit(
            self.card_images[self.dealer.get_card_by_index(1)], (580, 30))
        points = self.font.render(
            str(self.dealer.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (600, 180)
        pygame.draw.rect(self.screen, self.background, points_rect)
        self.screen.blit(points, points_rect)
        pygame.display.update()
        self.clock.tick(30)

        while dealer_takes_card:
            dealer_score = self.dealer.status()[1]
            if dealer_score > 21:
                busted = self.font.render("BUSTED", True, (255, 50, 50))
                busted_rect = busted.get_rect()
                busted_rect.center = (600, 210)
                self.screen.blit(busted, busted_rect)
                dealer_takes_card = False
            elif dealer_score >= 17:
                dealer_takes_card = False
            else:
                #shoot_card()
                self.dealer.get_card(self.random_card_choice())
                self.screen.blit(self.card_images[self.dealer.get_card_by_index(-1)],
                                 (550 + (self.dealer.get_card_amount() - 1) * 30, 30))
                points = self.font.render(
                    str(self.dealer.get_points()), True, self.white)
                points_rect = points.get_rect()
                points_rect.center = (600, 180)
                pygame.draw.rect(self.screen, self.background, points_rect)
                self.screen.blit(points, points_rect)
            pygame.display.update()
            self.clock.tick(30)
        self.display_score()

#ik haat mij
if __name__ == '__main__':
    try:
        print("initting game")
        game = GameState()
    except KeyboardInterrupt:
        cap.release()
        servo_stop()
        pygame.quit()
<<<<<<< HEAD
        servo_stop()
        stop_dc1()
        cv2.destroyAllWindows()
=======
        #servo_stop()
        #stop_dc1()
>>>>>>> e29a1e9e4a7dc9da7be584f32364a534203e84ac
