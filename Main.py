import os
import PIL
from tkinter import *
from Tile import *
from Grid import *
import numpy as np

DEFAULT = 5 #the index of the default tile 5 without allDir, 6 otherwise
tileSize = 20

def getAllTiles():
    # add a special Tile "all Directions"
    # tilesName = [ "blank", "up", "right", "down", "left","allDir","default"];

    tilesName = [ "blank", "up", "right", "down", "left","default"];
    tiles = []
    for i in range (len(tilesName)):
        tiles.append(PIL.Image.open(os.path.dirname(os.path.abspath(__file__))+"/tiles/"+tilesName[i]+".png").resize((tileSize,tileSize)))
    return tiles 

def checkValid(array, validOptions):
    toRemove = []
    for option in array:
        if option not in validOptions:
            toRemove.append(option)
    for option in toRemove:
        array.remove(option)

def restart():
    global grid, DIM, tiles, saveButton
    grid = Grid(DIM, tiles)
    saveButton.config(state=DISABLED)
    

def save():
    global grid, tiles, DIM 
    img = np.zeros((DIM*tileSize,DIM*tileSize,3), dtype=np.uint8)
    for i in range (DIM):
        for j in range (DIM):
            subTile = list(np.array(tiles[grid.grid[i][j].options[0]].image))
            img[i*tileSize:(i+1)*tileSize,j*tileSize:(j+1)*tileSize,:] = subTile
    img = PIL.Image.fromarray(img)
    img.save("ImageResult.png")
    

def draw(grid):
    global tileImages, gridLabel, tiles
    for i in range (DIM):
        for j in range (DIM):
            cell = grid.grid[i][j]
            if cell.collapsed:
                try:
                    index = cell.options[0]
                except IndexError:
                    restart()
                tileImg = tileImages[index]
                gridLabel[i][j].config(image=tileImg)
            else:
                defaultTile = tileImages[DEFAULT]
                gridLabel[i][j].config(image=defaultTile)


def update(): 
    global grid, tiles, saveButton
    draw(grid)

    #looking for the cell with the least options
    gridCopy = grid.copy(tiles)
    cell = gridCopy.getCellLeastEntropy()

    # If were done with the grid, we stop the loop
    if cell is None:
        saveButton.config(state=ACTIVE)
    else:
        #collapse the cell
        cell.collapsed = True
        try:
            cell.options = [random.choice(cell.options)]
        except:
            restart()

        #update the grid
        grid = gridCopy


    nextGrid = Grid(DIM, tiles)
    for i in range (DIM):
        for j in range (DIM):
            cell = grid.grid[i][j]
            if cell.collapsed:
                nextGrid.grid[i][j] = cell.copy()
                # print("collapsed",nextGrid.grid[i][j])
            else:
                options = [i for i in range(len(tiles))]

                # look up 
                if i > 0:
                    up = grid.grid[i-1][j]
                    validOptions = []
                    for option in up.options:
                        valid = tiles[option].down
                        validOptions.extend(valid)
                    checkValid(options, validOptions)
                    
                
                # look right
                if j < DIM-1:
                    right = grid.grid[i][j+1]
                    validOptions = []
                    for option in right.options:
                        valid = tiles[option].left
                        validOptions.extend(valid)
                    checkValid(options, validOptions)
                    

                # look down
                if i < DIM-1:
                    down = grid.grid[i+1][j]
                    validOptions = []
                    for option in down.options:
                        valid = tiles[option].up
                        validOptions.extend(valid)
                    checkValid(options, validOptions)
                    
                
                # look left
                if j > 0:
                    left = grid.grid[i][j-1]
                    validOptions = []
                    for option in left.options:
                        valid = tiles[option].right
                        validOptions.extend(valid)
                    checkValid(options, validOptions)
                    

                # print("options", options)
                nextGrid.grid[i][j] = Cell.createCellFromOptions(options)
                # print("nextGrid", nextGrid.grid[i][j])

                

    grid = nextGrid

    # print(grid)

    window.after(1,update)


def main():
    global grid, window, DIM, tiles, tileImages, gridLabel, saveButton

    DIM = 15

    window = Tk()
    window.title("Wave function Collapse")
    window.geometry(f"{DIM*tileSize}x{DIM*tileSize+50}")
    window.resizable(0, 0)

    # Load and create all tiles
    # This is really specific to the tiles you input in the tiles folder
    tileImages = getAllTiles()

    # tiles = [
    #     Tile(tileImages[0], [0,0,0,0]),
    #     Tile(tileImages[1], [1,1,0,1]),
    #     Tile(tileImages[1], [1,1,0,1]).rotate(1),
    #     Tile(tileImages[1], [1,1,0,1]).rotate(2),
    #     Tile(tileImages[1], [1,1,0,1]).rotate(3),
    #     # Tile(tileImages[5], [1,1,1,1]),
    # ]

    tiles = [
        Tile(tileImages[0], [0,0,0,0]),
        Tile(tileImages[1], [1,1,0,1]),
        Tile(tileImages[2], [1,1,1,0]),
        Tile(tileImages[3], [0,1,1,1]),
        Tile(tileImages[4], [1,0,1,1]),
        # Tile(tileImages[5], [1,1,1,1]),
    ]

    # we retransform the Image objects to PhotoImage objects
    for i in range (len(tileImages)):
        tileImages[i] = ImageTk.PhotoImage(tileImages[i])

    # Generate the adjacency rules based on the edges of the tiles
    for tile in tiles:
        tile.analyzeEdges(tiles)
        # print(tile)

    # Create a cell for each spot in the grid
    
    grid = Grid(DIM, tiles)

    gridLabel = []
    for i in range (DIM):
        gridLabel.append([])
        for j in range (DIM):
            
            label = Label(window, image=tileImages[5], borderwidth=0)
            label.grid(row=i, column=j)
            gridLabel[i].append(label)
    
    # Restart button
    restartButton = Button(window, text="Restart", command=restart)
    restartButton.grid(row=DIM, column=0, columnspan=int(DIM/2), padx=10, pady=10)
    # Save button
    saveButton = Button(window, text="Save", command=save, state=DISABLED)
    saveButton.grid(row=DIM, column=int(DIM/2), columnspan=int(DIM/2), padx=10, pady=10)


    # Start the update loop

    update()

    # mainloop
    window.mainloop()


if __name__ == "__main__":
    main()

