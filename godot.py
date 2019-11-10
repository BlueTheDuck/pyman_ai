from socket import socket
import struct
from array import array
import numpy as np

FWD = 0
ROT_LEFT = 1
BWD = 2
ROT_RIGHT = 3


def array_to_key(vals: list):
    highest_i = -1
    for i in range(vals.__len__()):
        if vals[i] > vals[highest_i]:
            highest_i = i
    if vals[highest_i] > 0.7:
        return highest_i
    return -1


class Pacman:
    dots = {}
    walls = {}
    ghosts = {}
    powered = False,
    score = 0.0

    def __init__(self):
        self.dots = {
            "left": 0,
            "front": 0,
            "right": 0,
            "back": 0,
        }
        self.walls = {
            "left": 0,
            "front": 0,
            "right": 0,
            "back": 0,
        }
        self.ghosts = {
            "left": 0,
            "front": 0,
            "right": 0,
            "back": 0,
        }
        self.powered = False
        self.score = 0

    def to_array(self):
        return (self.dots["left"],
                self.dots["front"],
                self.dots["right"],
                self.dots["back"],
                self.walls["left"],
                self.walls["front"],
                self.walls["right"],
                self.walls["back"],
                self.ghosts["left"],
                self.ghosts["front"],
                self.ghosts["right"],
                self.ghosts["back"],
                1 if self.powered else 0)


class Godot:
    _cnx: socket = None
    _pacman: Pacman = None

    def __init__(self, cnx: socket):
        self._cnx = cnx
        self._pacman = Pacman()
        assert(self.read_string() == "CNX")

    def read_uint(self):
        bs = self._cnx.recv(4)
        assert(bs.__len__() == 4)
        return struct.unpack("=I", bs)[0]

    def read_double_uint(self):
        bs = self._cnx.recv(8)
        assert(bs.__len__() == 8)
        return struct.unpack("=Q", bs)[0]

    def read_float(self):
        bs = self._cnx.recv(4)
        assert(bs.__len__() == 4)
        return struct.unpack("=f", bs)[0]

    def read_string(self):
        str_size = self.read_uint()
        string = self._cnx.recv(str_size).decode("utf-8")
        return string

    def send_arr(self, arr: list):
        self._cnx.send(array("B", arr))

    def send_uint(self, n: int):
        self._cnx.send(array("B", [n]))

    def move(self, dir=int):
        if dir == -1:
            return
        self.send_arr([0xFF, dir])

    def update(self):
        # print("Updating internal state")
        self._dots_dist = []
        self.send_arr([0xFE, 0xFE])
        # print("Req. sent")
        # print("Reading dots")
        dots_keys = self._pacman.dots.keys()
        for key in self._pacman.dots.keys():
            self._pacman.dots[key] = self.read_float()
        # print("Reading walls")
        for key in self._pacman.walls.keys():
            self._pacman.walls[key] = self.read_float()
        # print("Reading ghosts")
        for key in self._pacman.ghosts.keys():
            self._pacman.ghosts[key] = self.read_float()
        self._pacman.score = float(self.read_uint())
        # print("Done updating")

    def quit(self):
        self.send_arr([0xFE, 0x00])

    def to_array(self):
        return self._pacman.to_array()
