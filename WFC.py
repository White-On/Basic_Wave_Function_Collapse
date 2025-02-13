import os
from tkinter import *
import numpy as np
from PIL import  ImageTk, Image

tile_size = 20
patern_path = "tiles/city.png"
# Dimension of the grid (number of cells DIM x DIM)
grid_dim = 15

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

window = Tk()
window.title("Wave function Collapse")


class Grid:
    def __init__(self, dim: int, nb_unique_tiles:int) -> None:
        self.grid = [[Cell(nb_unique_tiles) for _ in range(dim)] for _ in range(dim)]
        self.dim = dim
        
    def __repr__(self) -> str:
        return str(self.grid)

class Cell:
    def __init__(self, nb_unique_tiles:int) -> None:
        self.collapsed = False
        self.options = list(range(nb_unique_tiles))
    
    def __repr__(self) -> str:
        return f"Collapsed:{self.collapsed},Options:{self.options}"

class Wave_Function_Collapse:
    def __init__(self):
        self.window = None
        self.tile_size = None
        self.patern_path = None
        self.grid_dim = None
        self.grid_label = None
        self.tile_img = None
        self.tile_array = None
        self.neighboor_edge = None

    def get_least_entropy_tile(self):
        pass

    def draw():
        pass

    def uptade():
        pass

def main():

    #  if the dimension is under a certain value, we use a set window size
    if grid_dim > 7:
        window.geometry(f"{grid_dim*tile_size}x{grid_dim*tile_size+50}")
    else:
        window.geometry("200x200")
    window.resizable(0, 0)

    # Load and create all tiles

    patern_img = np.asarray(Image.open(patern_path))
    unique_tiles = get_unique_tiles(extract_tiles_from_img_with_rotation(patern_img))
    tiles_img = [Image.fromarray(tile, mode='RGB').resize((tile_size,tile_size)) for tile in unique_tiles]

    # evaluate the neighbor

    neighboor_edge = evaluate_neighboor(unique_tiles)

    grid = Grid(grid_dim, len(unique_tiles))

    # We average the image to get the default display tile
    # TODO fix the issue with the resize
    # and transform this into it's own class
    default_img = np.mean(unique_tiles,axis=0)
    default_img = ImageTk.PhotoImage(Image.fromarray(default_img.astype(np.uint8),mode="RGB")
                                        .resize((tile_size,tile_size)))

    # maintain state for the Label element in order to display them
    grid_label = []
    for i in range (grid_dim):
        grid_label.append([])
        for j in range (grid_dim):
            
            label = Label(window, image=default_img, borderwidth=0)
            label.grid(row=i, column=j)
            grid_label[i].append(label)
    
    # # Restart button
    # restartButton = Button(window, text="Restart", command=restart)
    # restartButton.grid(row=DIM, column=0, columnspan=int(DIM/2), padx=10, pady=10)
    # # Save button
    # saveButton = Button(window, text="Save", command=save, state=DISABLED)
    # saveButton.grid(row=DIM, column=int(DIM/2), columnspan=int(DIM/2), padx=10, pady=10)

    # Start the update loop
    update(grid, unique_tiles, neighboor_edge, tiles_img, grid_label, default_img)
    # mainloop
    window.mainloop()

def update(grid, unique_tiles, neighboor_edge, tiles_img, grid_label, default_tile):
    draw_grid(grid, tiles_img, grid_label, default_tile)

    window.after(1,update, grid, unique_tiles, neighboor_edge, tiles_img, grid_label, default_tile)

def draw_grid(grid, tiles_img, grid_label, default_tile):
    img_list = []
    for i in range(grid.dim):
        for j in range(grid.dim):
            cell = grid.grid[i][j]
            if cell.collapsed:
                try:
                    #  For each cell, we draw the tile with the correct index in the tileImages list
                    index = cell.options[0]
                except IndexError:
                    # restart()
                    print("error no more options")
                    exit()
                tileImg = tiles_img[index]
                grid_label[i][j].config(image=tileImg)
            else:
                grid_label[i][j].config(image=default_tile)

def extract_tiles_from_img(img:np.array, tile_size=(3,3)) -> list:
    extracted_tiles = []
    N,M,_ = img.shape
    for i in range(N-tile_size[0]+1):
        for j in range(M-tile_size[1]+1):
            tile = img[i:i+tile_size[0],j:j+tile_size[1]]
            extracted_tiles.append(tile)
    return extracted_tiles

def extract_tiles_from_img_with_rotation(img):
    result = []
    copy = img.copy()
    for _ in range(4):
        result += extract_tiles_from_img(copy)
        copy = np.rot90(copy)
    return result

def get_unique_tiles(list_tiles):
    unique = []
    def is_in_list(list,element):
        for elem in list:
            if np.array_equal(elem,element):
                return True
    for tile in list_tiles:
        if not is_in_list(unique,tile):
            unique.append(tile)
    
    return unique

def frequency_tiles(tiles_list):
    unique_tiles = get_unique_tiles(tiles_list)
    frequency = np.zeros(len(unique_tiles))
    for t1 in tiles_list:
        for idx, t2 in enumerate(unique_tiles):
            if np.array_equal(t1, t2):
                frequency[idx] +=1
    
    return frequency

def overlaping_tile_east(tile1, tile2):
    return np.array_equal(tile1[:,1:],tile2[:,:2])

def overlaping_tile_south(tile1, tile2):
    return np.array_equal(tile1[1:,:],tile2[:2,:])

def overlaping_tile_west(tile1, tile2):
    return np.array_equal(tile1[:,:2],tile2[:,1:])

def overlaping_tile_north(tile1, tile2):
    return np.array_equal(tile1[:2,:],tile2[1:,:])


def evaluate_neighboor(list_tiles):
    neighboor = {i:[[],[],[],[]] for i in range(len(list_tiles))}
    for i, tile1 in enumerate(list_tiles):
        for j, tile2 in enumerate(list_tiles):
            neighboor[i][NORTH].append(j) if overlaping_tile_north(tile1, tile2) else None
            neighboor[i][EAST].append(j) if overlaping_tile_east(tile1, tile2) else None
            neighboor[i][SOUTH].append(j) if overlaping_tile_south(tile1, tile2) else None
            neighboor[i][WEST].append(j) if overlaping_tile_west(tile1, tile2) else None
    
    return neighboor


if __name__ == "__main__":
    main()
