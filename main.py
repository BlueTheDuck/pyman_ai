from time import sleep
from random import randint
from godot import Godot, array_to_key
from sys import argv
import socket
import neat


HOST = "127.0.0.1"
PORT = 4040
NN = 10
INIT_STEPS = 10
MAX_SCORE = 2460
STEPS_PER_SEC = 20.0


def eval_genomes(genomes, config):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        error = None
        try:
            s.listen()
            for genome_id, genome in genomes:
                genome.fitness = 0.0
                net = neat.nn.FeedForwardNetwork.create(genome, config)
                print("Wating connection")
                cnx, addr = s.accept()
                godot = Godot(cnx)
                # godot.send_genome(genome)
                # input("Press enter")
                try:
                    # Store last step state to check whether Pacman made any progress or not
                    steps_without_progress = 0
                    steps_not_moving = 0
                    dist_to_walls = {
                        "left": 0,
                        "front": 0,
                        "right": 0,
                        "back": 0,
                    }
                    last_score = 0
                    while steps_without_progress < STEPS_PER_SEC*5 and steps_not_moving < 5:
                        godot.update()

                        # Is Pacman making any progress?
                        if godot._pacman.score != last_score:
                            last_score = godot._pacman.score
                            steps_without_progress = 0
                        else:
                            steps_without_progress += 1
                        n = 0
                        for key in dist_to_walls.keys():
                            if round(dist_to_walls[key], 8) == round(godot._pacman.walls[key], 8):
                                n += 1
                        if n == 4:
                            steps_not_moving += 1
                        else:
                            steps_not_moving = 0
                        dist_to_walls = godot._pacman.walls.copy()

                        value = net.activate(godot.to_array())
                        # print("Activation yielded ", value)
                        key = array_to_key(value)
                        print("Key: ", key)
                        godot.move(key)
                        print(key, ": ", value)
                        print("Steps without progress: ",
                              steps_without_progress)
                        print("Steps without moving: ",
                              steps_not_moving)
                        sleep(1.0 / STEPS_PER_SEC)
                    print("Score: ", godot._pacman.score)
                    genome.fitness = godot._pacman.score * godot._pacman.score
                    print("Fitness: ", genome.fitness)
                    godot.quit()
                except BrokenPipeError as bp:
                    print("Broken pipe")
                except:
                    godot.quit()
                    raise
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
pop.add_reporter(neat.Checkpointer(1, 30, "checkpoints/neat-"))
pop.add_reporter(neat.StatisticsReporter())
winner = pop.run(eval_genomes)
with open("winner", "w") as file:
    file.write(str(winner))
print('\nBest genome:\n{!s}'.format(winner))
