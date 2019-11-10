import socket
from time import sleep
from random import randint
from godot import Godot, array_to_key
import numpy as np
import neat
from sys import argv


HOST = "127.0.0.1"
PORT = 4040
NN = 10
INIT_STEPS = 10
MAX_SCORE = 2460
STEPS_PER_SEC = 10.0


def eval_genomes(genomes, config):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        error = None
        try:
            s.listen()
            for genome_id, genome in genomes:
                genome.fitness = 4.0
                net = neat.nn.FeedForwardNetwork.create(genome, config)
                print("Wating connection")
                cnx, addr = s.accept()
                godot = Godot(cnx)
                try:
                    remaining_steps = INIT_STEPS
                    steps_without_progress = 0
                    last_score = 0
                    while remaining_steps > 0 and steps_without_progress < STEPS_PER_SEC*5:
                        godot.update()
                        if godot._pacman.score != last_score:
                            remaining_steps += STEPS_PER_SEC
                            last_score = godot._pacman.score
                            steps_without_progress = 0
                        else:
                            steps_without_progress += 1
                        value = net.activate(godot.to_array())
                        # print("Activation yielded ", value)
                        key = array_to_key(value)
                        print("Key: ", key)
                        godot.move(key)
                        print(key, ": ", value)
                        print("Remaining steps: ", remaining_steps)
                        remaining_steps = remaining_steps - 1
                        sleep(1.0 / STEPS_PER_SEC)
                    print("Score: ", godot._pacman.score)
                    genome.fitness = godot._pacman.score
                    print("Fitness: ", genome.fitness)
                except Exception as e:
                    raise
                finally:
                    godot.quit()
        except Exception as e:
            print("Error: ", e)
        s.close()


config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation, "neat-config")
pop = None
if argv.__len__() == 2:
    import os
    if os.path.exists(argv[1]):
        print("Using file")
        pop = neat.Checkpointer.restore_checkpoint(argv[1])
    else:
        raise Exception("File not found")
else:
    print("New pop")
    pop = neat.Population(config)
pop.add_reporter(neat.StdOutReporter(False))
pop.add_reporter(neat.Checkpointer(1, 30))
winner = pop.run(eval_genomes)
print('\nBest genome:\n{!s}'.format(winner))
