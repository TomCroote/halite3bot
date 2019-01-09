#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

from hlt import *

import numpy as np

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
me = game.me
game_map = game.game_map

#halite_map = np.zeros((game_map.width,game_map.height))

i = 0

halite_map = np.array([[game_map[Position(x,y)].halite_amount for y in range(0, game_map.width)] for x in range(0, game_map.height)])
max_halite_square = np.unravel_index(np.argmax(halite_map), halite_map.shape)
logging.info(max_halite_square)
logging.info(game_map[Position(max_halite_square[0], max_halite_square[1])].halite_amount)

halite_group_map = np.zeros((int(game_map.width/4),int(game_map.height/4)))

for x in range(0, int(game_map.width/4)):
    for y in range(0, int(game_map.height/4)):
        halite_group_map[x,y] = np.mean(halite_map[x*4:(x*4)+4,y*4:(y*4)+4])

max_halite_group = np.unravel_index(np.argmax(halite_group_map), halite_group_map.shape)

#halite dist
#for x in range (0,game_map.width):
#    for y in range (0,game_map.height): 
#        halite_map[]game_map[Position(x,y)].halite_amount)
        
#logging.info(max(halite_map))
        
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("NotoriousBOT")

ship_status = {}

ship_movement_counter = {}

ship_last_position = {}

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    halite_map = np.array([[game_map[Position(x,y)].halite_amount for y in range(0, game_map.width)] for x in range(0, game_map.height)])
    max_halite_square = np.unravel_index(np.argmax(halite_map), halite_map.shape)
    halite_group_map = np.zeros((int(game_map.width/4),int(game_map.height/4)))

    for x in range(0, int(game_map.width/4)):
        for y in range(0, int(game_map.height/4)):
            halite_group_map[x,y] = np.mean(halite_map[x*4:(x*4)+4,y*4:(y*4)+4])

    max_halite_group = np.unravel_index(np.argmax(halite_group_map), halite_group_map.shape)
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    first_turn = "true"

    for ship in me.get_ships():
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))
        
        #if "scouting" not in str(ship_status):
        #    ship_status[ship.id] = "scouting"
        #    logging.info("no it isnt")
            
        #if "exploring" in str(ship_status):
        #    logging.info("yes it is")
        
        #logging.info(ship_status)
        
        if ship.id not in ship_movement_counter:
            ship_movement_counter[ship.id] = 0
        
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"

        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                 ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        #if ship_status[ship.id] == "scouting":
        #    command_queue.append(
        #        ship.move(
        #            random.choice([ Direction.North, Direction.East ])))
            
        elif ship.halite_amount >= constants.MAX_HALITE * (3 / 4):
            ship_status[ship.id] = "returning"
        
        if ship_status[ship.id] == "exploring":
            #if game_map[Position(max_halite_square[0], max_halite_square[1])].is_empty or ship.is_full:
            #    command_queue.append(
            #        ship.move(
            #            game_map.naive_navigate(ship, Position(max_halite_group[0]*4, max_halite_group[1]*4))))
            #else if game_map[Position(max_halite_square[0], max_halite_square[1])].is_occupied and ship.position != Position(max_halite_square[0], max_halite_square[1]):
            #    command_queue.append(
            #        ship.move(
            #            game_map.naive_navigate(ship, Position(max_halite_square[0], max_halite_square[1]))))
            #else:
            #    command_queue.append(ship.stay_still())
            if ship_movement_counter[ship.id] >= 10:
                command_queue.append(
                    ship.move(
                        random.choice([ Direction.North, Direction.East, Direction.West, Direction.South ])))
                logging.info("ship stuck")    
            elif game_map[ship.position].halite_amount >= 50:
                command_queue.append(ship.stay_still())
            elif game_map[Position(max_halite_square[0], max_halite_square[1])].is_occupied and ship.position != Position(max_halite_square[0], max_halite_square[1]):
                command_queue.append(
                    ship.move(
                        game_map.naive_navigate(ship, Position(max_halite_square[0]+ship.id, max_halite_square[1]+ship.id))))
            else:
                command_queue.append(
                    ship.move(
                        game_map.naive_navigate(ship, Position(max_halite_square[0], max_halite_square[1]))))

            if ship.id in ship_last_position:
                if ship.position == ship_last_position[ship.id]:
                    ship_movement_counter[ship.id] += 1
                    logging.info("ship still")
                else:
                    ship_movement_counter[ship.id] = 0
            
            
        logging.info("Ship {} is {}".format(ship.id, ship_status[ship.id]))
        logging.info(ship.position)
        
        ship_last_position[ship.id] = ship.position
        
        #if game_map[ship.position].halite_amount >= 500:
        #    poi = ship.position

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if len(me.get_ships()) <= 10 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

