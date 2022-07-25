import random
from matplotlib.pyplot import grid
from numpy import sort
from Cell import Cell
from tkinter import *

class Grid:
    def __init__(self, dim: int, tiles) -> None:
        self.grid = []
        # To optimize the algorithm, we should create a list of cells that are not collapsed in order to
        # reduce the number of iterations when looking for the next cell to collapse
        # self.notCollapsed = []
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
        list = []

        # To optimize the algorithm, we should create a list of cells that are not collapsed in order to
        # reduce the number of iterations when looking for the next cell to collapse

        #  We create a list of cells that are not collapsed
        for i in range(len(self.grid)):
            for j in range(len(self.grid)):
                cell = self.grid[i][j]
                if cell.collapsed:
                    continue
                else:
                    list.append(cell)

        #  If there are no cells that are not collapsed, we return None -> the algorithm is done
        if len(list) == 0:
            # print(self)
            return None
        
        # We sort the list of cells by the entropy of the cell
        list.sort(key=lambda x: len(x.options))
        # We get the lowest entropy 
        lowestEntropy = len(list[0].options)
        stopIndex = 1
        # And we get all the cell with the lowest entropy
        for i in range(len(list)):
            if len(list[i].options) > lowestEntropy:
                stopIndex = i
                break

        list = list[:stopIndex]

        # We then choose a random cell from the list
        return random.choice(list)



    