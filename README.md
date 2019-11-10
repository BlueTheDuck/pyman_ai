# Pyman AI

Using darwinism to play Pacman (because it wasn't already hard enought)

## Overview
This project is a simple program that uses a *neural network* to play Pacman. To do the training we use *NEAT*, a kind of *genetic algorithm* that generates a population of NNs (in this case, NNs that will play Pacman) and tests them against an enviroment. The ones that perform the best get to pass down their genes

## Requirements
* [This custom implementation of Pacman](github.com/PeronTheDuck/godot_pacman) that comes without ghosts (for the time being) and connects to the server that main.py creates.
* Python 3.6
  * [Neat](https://github.com/CodeReclaimers/neat-python): `pip install neat`

## Notes
* This program was only tested on Ubuntu 18.04
