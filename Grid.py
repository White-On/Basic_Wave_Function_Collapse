import random
from matplotlib.pyplot import grid
from numpy import sort
from Cell import Cell
from tkinter import *

class Grid:
    def __init__(self, dim: int, tiles) -> None:
        self.grid = []
        for i in range(dim):
            self.grid.append([])
            for j in range(dim):
                self.grid[i].append(Cell(len(tiles)))
                
    
    def __repr__(self) -> str:
        return str(self.grid)
    
    def copy(self, tiles) -> "Grid":
        DIM = len(self.grid)
        copy = Grid(DIM, tiles)
        for i in range(DIM):
            for j in range(DIM):
                copy.grid[i][j] = self.grid[i][j].copy()
        return copy
    
    def getCellLeastEntropy(self):
        leastEntropyCell = None
        list = []
        for i in range(len(self.grid)):
            for j in range(len(self.grid)):
                cell = self.grid[i][j]
                if cell.collapsed:
                    continue
                else:
                    list.append(cell)

        if len(list) == 0:
            # print(self)
            return None
        
        list.sort(key=lambda x: len(x.options))
        tmp = len(list[0].options)
        # print("tmp", tmp)
        stopIndex = 1
        for i in range(len(list)):
            if len(list[i].options) > tmp:
                stopIndex = i
                break

        list = list[:stopIndex]
        # print("list", list)
        return random.choice(list)


    