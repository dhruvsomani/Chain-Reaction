# ChainReaction
# Author: Dhruv Somani
# Heuristic: 11

import time
import random
import copy

import sys
sys.setrecursionlimit(100)

class ChainBoard:
    def __init__(self, array, turn):
        # The Input Array is a 5 X 5 array of tuples like:
        # (player_number, orbs)

        self.array = array
        self.turn = turn


    def __str__(self):
        string = '\n'
        for row in self.array:
            string += str(row) + '\n'
        return string;


    def __getitem__(self, key):
        return self.array[key[0]][key[1]]


    def __setitem__(self, key, value):
        self.array[key[0]][key[1]] = value
        return None


    def orbs_to_critical(self, row, column):
        player, orbs = self[row, column]

        if (row, column) in [(0, 0), (0, 4), (4, 0), (4, 4)]:
            return 1 - orbs

        elif (row == 0 or row == 4) or (column == 0 or column == 4):
            return 2 - orbs

        else:
            return 3 - orbs


    def game_over(self):
        my_orbs = False
        opp_orbs = False

        for row in range(5):
            for column in range(5):
                player, orbs = self[row, column]

                if player == self.turn:
                    my_orbs = True

                elif player != 0:
                    opp_orbs = True

        return (not my_orbs or not opp_orbs)


    def suggest_move(self, depth):
        ratings = {(x, y): 0 for x in range(5) for y in range(5)}

        for row in range(5):
            for column in range(5):
                player, orbs = self[row, column]

                if (player == self.turn) | (player == 0):
                    rating = 0

                    experimentation_board = copy.deepcopy(self) # Create an exact copy of board to carry out experimentation
                    
                    try:
                        experimentation_board.new_orb(row, column)  # experiments and give ratings
                    except Exception as err:
                        
##                        print(err, 'at', row, column)
##                        for neighbor in self.get_neighbors(row, column):
##                            print((row, column), 'has a neighbor', (neighbor[0], neighbor[1]), 'with', self[neighbor[0], neighbor[1]][1], 'orbs',
##                                  'which has', self.orbs_to_critical(neighbor[0], neighbor[1]), 'to explode')

                        rating += float('inf') # Since this is an infinite move cycle, we win

##                    print()
##                    print('Row:', row, 'Column:', column)
##                    print(experimentation_board)

                    # Analysis of the Stage of Experimentation Board
                    my_orbs = 0
                    opp_orbs = 0
                    my_box_stronger = 0
                    num_of_corners = int(experimentation_board[0, 0][0] == self.turn) + \
                                     int(experimentation_board[0, 4][0] == self.turn) + \
                                     int(experimentation_board[4, 0][0] == self.turn) + \
                                     int(experimentation_board[4, 4][0] == self.turn)
                    num_of_edges = 0
                    max_loss_rating = 0
                    

                    for exp_row in range(5):
                        for exp_column in range(5):
                            exp_player, exp_orbs = experimentation_board[exp_row, exp_column]

                            if exp_player == self.turn:
                                my_orbs += exp_orbs

                                if (exp_row == 0 or exp_row == 4) or (exp_column == 0 or exp_column == 4):
                                    num_of_edges += 1

                                strong_than_all = True

                                for neighbor in self.get_neighbors(exp_row, exp_column):
                                    if self[neighbor[0], neighbor[1]][0] != 0 and self[neighbor[0], neighbor[1]][0] != self.turn:                                        
                                        my_orbs_to_critical = experimentation_board.orbs_to_critical(exp_row, exp_column)
                                        opp_orbs_to_critical = experimentation_board.orbs_to_critical(neighbor[0], neighbor[1])
                                        
                                        if my_orbs_to_critical < opp_orbs_to_critical:
                                            my_box_stronger += exp_orbs * (1 / (opp_orbs_to_critical - my_orbs_to_critical + 1)**2) / 3

                                        else:
                                            my_box_stronger -= exp_orbs * (1 / (my_orbs_to_critical - opp_orbs_to_critical + 1)**2.4) / 2.3
                                            strong_than_all = False

                                            if opp_orbs_to_critical == 0:
                                                vulnerable_neighbors = 0

                                                for neighbor in self.get_neighbors(exp_row, exp_column):
                                                    if experimentation_board[neighbor[0], neighbor[1]][0] == self.turn:
                                                        vulnerable_neighbors += self[neighbor[0], neighbor[1]][1]

                                                my_box_stronger -= vulnerable_neighbors * 0.05

                                    elif experimentation_board[neighbor[0], neighbor[1]][0] == self.turn:
                                        my_box_stronger += self[neighbor[0], neighbor[1]][1] * 0.002

                                if strong_than_all:
                                    my_box_stronger += 0.009 * exp_orbs                                                                             

                            elif (exp_player != 0) and depth > 0:
                                opp_orbs += exp_orbs

                                verification_board = copy.deepcopy(experimentation_board)
                                verification_board.turn = (verification_board.turn * 2) % 3

                                try:
                                    verification_board.new_orb(exp_row, exp_column)
                                except:
                                    max_loss_rating -= 100 # Hey! What should the value over here be? Can it affect averages and stuff?

                                my_ver_orbs = 0
                                opp_ver_orbs = 0
                                ver_opp_box_stronger = 0

                                for ver_row in range(5):
                                    for ver_column in range(5):
                                        ver_player, ver_orbs = experimentation_board[ver_row, ver_column]

                                        if ver_player == self.turn:
                                            my_ver_orbs += ver_orbs

                                            strong_than_all = True

                                            for neighbor in self.get_neighbors(ver_row, ver_column):
                                                if self[neighbor[0], neighbor[1]][0] != 0 and self[neighbor[0], neighbor[1]][0] != self.turn:                                        
                                                    my_orbs_to_critical = self.orbs_to_critical(ver_row, ver_column)
                                                    opp_orbs_to_critical = self.orbs_to_critical(neighbor[0], neighbor[1])
                                                    
                                                    if my_orbs_to_critical < opp_orbs_to_critical:
                                                        ver_opp_box_stronger += ver_orbs * (1 / (opp_orbs_to_critical - my_orbs_to_critical + 1)**2) / 3

                                                    else:
                                                        ver_opp_box_stronger -= ver_orbs * (1 / (my_orbs_to_critical - opp_orbs_to_critical + 1)**0.8) / 5
                                                        strong_than_all = False

                                                        if opp_orbs_to_critical == 0:
                                                            vulnerable_neighbors = 0

                                                            for neighbor in self.get_neighbors(ver_row, ver_column):
                                                                if self[neighbor[0], neighbor[1]][0] == self.turn:
                                                                    vulnerable_neighbors += self[neighbor[0], neighbor[1]][1]

                                                            ver_opp_box_stronger -= vulnerable_neighbors * 0.05

                                            if strong_than_all:
                                                ver_opp_box_stronger += 0.009 * exp_orbs                                                                             

                                        elif exp_player != 0:
                                            opp_ver_orbs += ver_orbs

                                max_loss_rating = max(max_loss_rating, (opp_ver_orbs + 1) / (my_ver_orbs + 1) * 1.35 + ver_opp_box_stronger * 0.4)

                                

##                                if time.time() - t > 0.2:
##                                    continue
##
##                                verification_board = copy.deepcopy(experimentation_board)
##                                verification_board.turn = (verification_board.turn * 2) % 3
##                                try:
##                                    verification_ratings = verification_board.suggest_move(depth-1)
##                                    verification_ratings = verification_ratings.values()
##                                    verification_ratings = [rating for rating in verification_ratings if rating != float('inf') and rating != float('-inf')]
##                                    if len(verification_ratings) != 0:
##                                        opp_moves -= sum(verification_ratings) / len(verification_ratings * 9 / 10)
##                                    
##                                except Exception as err:
##                                    print(err)
##                                    rating -= 100
                                

##                    print('My Orbs:', my_orbs)
##                    print('Opp Orbs:', opp_orbs)
##                    print('My Box Stronger:', my_box_stronger)
                                                                                   

                    rating += (my_orbs + 1) / (opp_orbs + 1) * 1.35 + num_of_corners*0.005 + num_of_edges * 0.002 + my_box_stronger*0.4 - max_loss_rating

                    if opp_orbs == 0 and my_orbs > 1:
                        rating = float('inf')
                
                    ratings[(row, column)] = rating

                else:
                    ratings[(row, column)] = float('-inf')

        return ratings


    def new_orb(self, row, column):
        # This function simulates the pressing of a button to create an orb
        # or the passing of an orb from a neighbouring explosion.

        player, orbs = self[row, column]

        my_orbs = 0
        opp_orbs = 0

        for check_row in range(5):  # Check if the game has ended and that there is one clear winner
            for check_col in range(5):
                if self[check_row, check_col][0] == self.turn:
                    my_orbs += 1
                else:
                    opp_orbs += 1

        if (my_orbs == 0 ^ opp_orbs == 0):
            return None

        if (row, column) in [(0, 0), (0, 4), (4, 0), (4, 4)]:
            if orbs < 1:
                self[row, column] = (self.turn, orbs + 1)

            else:
                self[row, column] = (0, 0)
                for neighbor in self.get_neighbors(row, column):
                    self.new_orb(neighbor[0], neighbor[1])

        elif (row == 0 or row == 4) or (column == 0 or column == 4):
            if orbs < 2:
                self[row, column] = (self.turn, orbs + 1)

            else:
                self[row, column] = (0, 0)
                for neighbor in self.get_neighbors(row, column):
                    self.new_orb(neighbor[0], neighbor[1])

        else:
            if orbs < 3:
                self[row, column] = (self.turn, orbs + 1)

            else:
                self[row, column] = (0, 0)
                for neighbor in self.get_neighbors(row, column):
                    self.new_orb(neighbor[0], neighbor[1])


    def get_neighbors(self, row, column):
        neighbors = []

        for neighbor in [(row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)]:
            if 0 <= neighbor[0] <= 4 and 0 <= neighbor[1] <= 4:
                neighbors.append(neighbor)

        return neighbors

##t = time.time()

array = []

for row_num in range(5):
    row = input().split()

    for item in range(5):
        row[item] = (int(row[item][0]), int(row[item][1])) # Model the Array accordingly

    array.append(row)

##array = [[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
##         [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
##         [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
##         [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
##         [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]]

board = ChainBoard(array, int(input())) # Modify the last argument when submitting
ratings = board.suggest_move(1)

##print(ratings)

move = max(ratings, key=ratings.get)
print(move[0], move[1])

##print(time.time() - t)
