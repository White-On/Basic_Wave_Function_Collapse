import os
import random
from PIL import Image, ImageTk, ImageOps


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
            

    # def __len__(self):
    #     return len(self.options)
    
    # def updateTile(self):
    #     pass

    # def copy(self):
    #     newTile = Tile()
    #     newTile.isColapsed = self.isColapsed
    #     newTile.options = self.options
    #     newTile.image = self.image
    #     return newTile

    # @classmethod
    # def update(cls):
    #     if len(Tile.notColapsed) == 0:
    #         return

    #     for tile in Tile.notColapsed:
    #         tile.updateTile()

    #     tile = cls.getTileLessEntropy()
    #     tile.isColapsed = True
    #     if len(tile.options) == 1:
    #         tile.image = cls.allTiles[tile.options[0]]
            
    #     else:
    #         tile.image = cls.allTiles[random.choice(tile.options)]
    #     cls.notColapsed.remove(tile)
    
    # @classmethod
    # def getTileLessEntropy(cls):
    #     cls.notColapsed.sort(key=lambda x: len(x))
    #     return cls.notColapsed[0]

    # @classmethod
    # def init(cls):
    #     cls.allTiles = getAllTiles()
    
    