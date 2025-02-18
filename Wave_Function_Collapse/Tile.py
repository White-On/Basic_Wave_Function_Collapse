import os
import random



UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class Tile:
    def __init__(self, img, edges) -> None:
        self.image = img
        self.edges = edges

        self.up = []
        self.down = []
        self.left = []
        self.right = []
    
    def rotate(self, nbRotations):
        # Often we you create a new tile , you can just rotate the old one
        # This is the purpuse of this function
        self.image = self.image.rotate(90*nbRotations)
        tmp = len(self.edges)
        newEdges = [0]*tmp
        for i in range(tmp):
            newEdges[i] = self.edges[(i-nbRotations+tmp)%tmp]   # modulo to avoid negative index
        self.edges = newEdges
        return self
    
    def __repr__(self) -> str:
        return f"Edges : {self.edges}, Up : {self.up}, Right: {self.right}, Down : {self.down}, Left : {self.left}"
    
    def analyzeEdges(self, tiles):
        #  Analyze the edges of the tile and create the adjacency lists for each direction
        #  The adjacency lists are used to determine if a tile can be placed on a certain direction 
        #  We are basically creating the rules for the tiles to be placed 
        for i in range(len(tiles)):
            tile = tiles[i]

            #  Up connection
            if tile.edges[DOWN] == self.edges[UP]:
                self.up.append(i)
            #  Right connection
            if tile.edges[LEFT] == self.edges[RIGHT]:
                self.right.append(i)
            #  Down connection
            if tile.edges[UP] == self.edges[DOWN]:
                self.down.append(i)
            #  Left connection
            if tile.edges[RIGHT] == self.edges[LEFT]:
                self.left.append(i)
        
    