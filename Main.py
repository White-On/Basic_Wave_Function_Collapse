import os
import PIL
from tkinter import *
from Tile import *
from Grid import *
import numpy as np
from PIL import  ImageTk

DEFAULT = 5 #the index of the default tile 5 without allDir, 6 otherwise
tileSize = 20

def getAllTiles():
    """ Returns a list of all the tiles"""
    # add a special Tile "all Directions"
    # tilesName = [ "blank", "up", "right", "down", "left","allDir","default"];

    tilesName = [ "blank", "up", "right", "down", "left","default"];
    tiles = []
    for i in range (len(tilesName)):
        tiles.append(PIL.Image.open(os.path.dirname(os.path.abspath(__file__))+"/tiles/"+tilesName[i]+".png").resize((tileSize,tileSize)))
    return tiles 

def checkValid(array, validOptions):
    # Parsing the array and removing the invalid options
    lenghtArray  = len(array)-1
    for i in range(lenghtArray,-1,-1):
        if array[i] not in validOptions:
            array.pop(i)

def restart():
    global grid, DIM, tiles, saveButton
    #  Reset the grid
    grid = Grid(DIM, tiles)
    saveButton.config(state=DISABLED)
    

def save():
    global grid, tiles, DIM 
    # The image is a grid of tiles
    img = np.zeros((DIM*tileSize,DIM*tileSize,3), dtype=np.uint8)
    for i in range (DIM):
        for j in range (DIM):
            #  Concatenate the tile with the image to obtain the final image
            subTile = list(np.array(tiles[grid.grid[i][j].options[0]].image))
            img[i*tileSize:(i+1)*tileSize,j*tileSize:(j+1)*tileSize,:] = subTile
    img = PIL.Image.fromarray(img)
    img.save("ImageResult.png")
    

def draw(grid):
    global tileImages, gridLabel, tiles, img_list
    img_list = []
    for i in range (DIM):
        for j in range (DIM):
            cell = grid.grid[i][j]
            if cell.collapsed:
                try:
                    #  For each cell, we draw the tile with the correct index in the tileImages list
                    index = cell.options[0]
                except IndexError:
                    # As my version has no backtrack, something there is no possible option so we start from scratch
                    restart()
                tileImg = tileImages[index]
                gridLabel[i][j].config(image=tileImg)
            else:
                #  If the cell is not collapsed, we draw the default tile 
                defaultTile = tileImages[DEFAULT]
                all_option = np.array([tiles_simple_image[opt] for opt in cell.options])
                mean_all_option = np.mean(all_option, axis=0)
                img = ImageTk.PhotoImage(PIL.Image.fromarray(mean_all_option.astype(np.uint8),mode="RGB"))
                img_list.append(img)
                gridLabel[i][j].config(image=img)

    

def update(): 
    global grid, tiles, saveButton
    draw(grid)

    #looking for the cell with the least options
    gridCopy = grid.copy(tiles)
    cell = gridCopy.getCellLeastEntropy()

    # If were done with the grid, we can save the image
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

    #  We create a copy of the grid to be the next iteration
    nextGrid = Grid(DIM, tiles)

    for i in range (DIM):
        for j in range (DIM):
            cell = grid.grid[i][j]
            if cell.collapsed:
                #  if the cell is collapsed, we just copy the cell to the new grid
                nextGrid.grid[i][j] = cell.copy()
                # print("collapsed",nextGrid.grid[i][j])
            else:
                # If the cell is not collapsed, we look for the possible options
                # We look in the 4 directions and we remove the options that are not possible
                # to reduce the entropy of the cell
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
                    
                nextGrid.grid[i][j] = Cell.createCellFromOptions(options)
                

    grid = nextGrid

    window.after(1,update)


def main():
    global grid, window, DIM, tiles, tileImages, gridLabel, saveButton, tiles_simple_image

    #  Dimension of the grid (number of cells DIM x DIM)
    DIM = 15

    window = Tk()
    window.title("Wave function Collapse")
    #  if the dimension is under a certain value, we use a set window size
    if DIM > 7:
        window.geometry(f"{DIM*tileSize}x{DIM*tileSize+50}")
    else:
        window.geometry("200x200")
    window.resizable(0, 0)

    # Load and create all tiles
    # This is really specific to the tiles you input in the tiles folder
    tileImages = getAllTiles()

    #  Create the Tiles
    #  the code here can be used to create a grid of tiles, but end up bad for saved image a the end of the program

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
    tiles_simple_image = [np.asarray(img).tolist() for img in tileImages]
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

