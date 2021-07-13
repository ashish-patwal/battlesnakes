import os
import random
import math
import json
import cherrypy
from queue import PriorityQueue

class spot():

    def __init__(self, data: dict):
        self.head, self.barriers, self.food, self.table, self.snakes, self.name, self.length, self.hazards = data.values()
        self.neighbours = []
        self.grid = None

    def absDistance(self, food: dict, neighbour):
        nx, ny , _ = neighbour
        fx, fy = food.values()
        return abs(nx - fx) + abs(ny - fy) 

    def gridValue(self, point: dict) -> int:
        for barrier in self.barriers:
            if barrier == point:
                return 0
        else:
            return 1

    def binaryGrid(self):
        self.grid = [ [self.gridValue({'x': j, 'y': i})  for j in range(0, self.table["width"])] for i in range(self.table["height"] - 1, -1, -1) ]

    def updateNeighbours(self):

        self.neighbours = []

        if self.head["x"] < self.table["width"] - 1 and self.grid[self.table['height'] - 1 - self.head['y']][self.head['x'] + 1]:
            self.neighbours.append((self.head["x"] + 1, self.head["y"], 'right'))

        if self.head["x"] > 0 and self.grid[self.table['height'] - 1 - self.head['y']][self.head['x'] - 1]: 
            self.neighbours.append((self.head["x"] - 1, self.head["y"], 'left'))

        if self.head["y"] < self.table["height"] - 1 and self.grid[self.table['height'] - 1 - self.head['y'] - 1][self.head['x']]: 
            self.neighbours.append((self.head["x"], self.head["y"] + 1, 'up'))

        if self.head["y"] > 0 and self.grid[self.table['height'] - 1 - self.head['y'] + 1][self.head['x']]:
            self.neighbours.append((self.head["x"], self.head["y"] - 1, 'down'))

    def dfs(self, mat, x, y, r, c, counter):

        if x < 0 or y < 0 or x >= c or y >= r or not mat[r - 1 - y][x]:
            return 

        mat[r - 1 - y][x] = 0
        counter.append(counter.pop() + 1)
        self.dfs(mat, x + 1, y, r, c, counter)
        self.dfs(mat, x, y + 1, r, c, counter)
        self.dfs(mat, x - 1, y, r, c, counter)
        self.dfs(mat, x, y - 1, r, c, counter)

    def validNeighbours(self):

        open_set = []

        for neighbour in self.neighbours:
            count = [0]
            mat = [row[:] for row in self.grid ]
            self.dfs(mat, neighbour[0], neighbour[1], self.table["height"], self.table["width"], count)
            open_set.append((count[-1], neighbour))
        
        open_set.sort()
        self.neighbours.clear()
        self.neighbours.append(open_set[-1][1])

    def hazardEvade(self):

        if self.head not in self.hazards:
            [ self.barriers.append(item) for item in self.hazards ]


    def snakeSense(self):

        dangerous = set()
        killShot = None
        
        for snake in self.snakes:
            for neighbour in self.neighbours:
                spots = []
                spots.append((neighbour[0] + 1, neighbour[1]))
                spots.append((neighbour[0] - 1, neighbour[1]))
                spots.append((neighbour[0], neighbour[1] + 1))
                spots.append((neighbour[0], neighbour[1] - 1))
                if snake["name"] != self.name:
                    if ((snake["head"]["x"], snake["head"]["y"])) in spots:
                        if snake["length"] >= self.length:
                            dangerous.add(neighbour)
                        #else:
                        #    killShot = neighbour

        if len(dangerous) == len(self.neighbours):
            return

        if dangerous:
            for danger in dangerous:
                self.neighbours.remove(danger)

        #if killShot:
        #    self.neighbours.clear()
        #    self.neighbours.append(killShot)


    def takeRisk(self):

        spots = []
        spots.append({"x": self.head["x"] + 1,"y": self.head["y"] ,"dir": "right"})
        spots.append({"x": self.head["x"] - 1,"y": self.head["y"] ,"dir": "left"})
        spots.append({"x": self.head["x"],"y": self.head["y"] + 1,"dir": "up"})
        spots.append({"x": self.head["x"],"y": self.head["y"] - 1,"dir": "down"})

        for spot in spots:
            if {"x": spot["x"] ,"y": spot["y"]} in self.hazards:
                self.neighbours.append((spot["x"], spot["y"], spot["dir"]))

#    def isTrap(self):
#        mySnakeBody = None
#        danger = ()
#
#        for snake in self.snakes:
#            if snake["name"] == self.name:
#                mySnakeBody = snake["body"]
#                break
#
#        
#        head, neck = mySnakeBody[0:2]
#
#        if not head["x"] - neck["x"]:
#            pass
#
#
#        elif not head["y"] - neck["y"]:
#            if head["x"] - neck["x"] > 0:
#
#        else:
#            print('don\'t know')




                
    def returnMove(self):

        self.hazardEvade()
        self.binaryGrid()
        self.updateNeighbours()
        self.snakeSense()

        if self.neighbours == []:
            self.takeRisk()

        if len(self.neighbours) == 2:
            tup = (self.neighbours[0][2], self.neighbours[1][2])
            if ('left' in tup and 'right' in tup) or ('up' in tup and 'down' in tup):
                self.takeRisk()
                self.validNeighbours()
        
        open_set = PriorityQueue()

        for food in self.food:
            if self.neighbours:
                for neighbour in self.neighbours:
                    open_set.put((self.absDistance(food,neighbour), neighbour[2]))

            else:
                open_set.put((-1, 'right'))

        return open_set.get()


"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "Lucifer",  # TODO: Your Battlesnake Username
            "color": "#CAF7E3",  # TODO: Personalize
            "head": "villain",  # TODO: Personalize
            "tail": "rocket",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        newData = {}

        newData["head"] = data["you"]["head"]
        newData["blocks"] = data["you"]["body"]
        newData["food"] = data["board"]["food"]
        newData["grid"] = {"height": data["board"]["height"], "width": data["board"]["width"]}
        newData["snakes"] = data["board"]["snakes"]
        newData["name"] = data["you"]["name"]
        newData["length"] = data["you"]["length"]
        newData["hazards"] = data["board"]["hazards"]
        [ newData["blocks"].append(item)  for snake in data["board"]["snakes"] for item in snake["body"] ]

        # Choose a random direction to move in
        #possible_moves = ["up", "down", "left", "right"]
        #move = random.choice(possible_moves)

        cur = spot(newData)
        _ , move = cur.returnMove()

        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
