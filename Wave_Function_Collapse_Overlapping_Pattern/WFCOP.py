from tkinter import *
import numpy as np
from PIL import  ImageTk, Image
import random
from tqdm import tqdm

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

MAX_RECURSION_DEPTH = 10

class Grid:
    def __init__(self, dim: int, nb_unique_tiles:int) -> None:
        self.grid = [[Cell(nb_unique_tiles, i+j*dim) for i in range(dim)] for j in range(dim)]
        self.dim = dim
        self.idx_not_collapsed = list(range(dim**2))
        self.idx_grid = np.asarray([x for xs in self.grid for x in xs])
        
    def __repr__(self) -> str:
        return str(self.grid)
    
    def get_lowest_entropy_cell(self):
         # Get non-collapsed cells
        not_collapsed_cells = self.idx_grid[self.idx_not_collapsed]

        if len(not_collapsed_cells) == 0:
            return None  # No available cells

        # Find the minimum entropy value
        min_entropy = min(len(cell.options) for cell in not_collapsed_cells)

        # Collect all cells with the lowest entropy
        lowest_entropy_cells = [cell for cell in not_collapsed_cells if len(cell.options) == min_entropy]

        # Return a random cell from those with the lowest entropy
        return random.choice(lowest_entropy_cells)
    
    def get_neighboor(self, cell):
        """Returns a dictionary of neighboring cells with directions as keys."""
        neighbors = {}

        # Find the position of the cell in the grid
        for i in range(self.dim):
            for j in range(self.dim):
                if self.grid[i][j] == cell:
                    # Define possible directions with their corresponding row/col adjustments
                    directions = {
                        NORTH: (i - 1, j),
                        SOUTH: (i + 1, j),
                        WEST: (i, j - 1),
                        EAST: (i, j + 1),
                    }

                    # Check each direction and add valid neighbors
                    for direction, (ni, nj) in directions.items():
                        if 0 <= ni < self.dim and 0 <= nj < self.dim:
                            neighbors[direction] = self.grid[ni][nj]

                    return neighbors  # Return as soon as we find the cell

        return {}  # Return an empty dictionary if the cell is not found


class Cell:
    def __init__(self, nb_unique_tiles:int, idx:int) -> None:
        self.collapsed = False
        self.options = list(range(nb_unique_tiles))
        self.index = idx
        self.checked = False
        self.cached_img = None
    
    def __repr__(self) -> str:
        return f"Collapsed:{self.collapsed},Options:{self.options}, Idx:{self.index}"

class Wave_Function_Collapse:
    def __init__(self, tile_size:int, patern_path:str, 
                 grid_dim:int, rotating_pattern:bool):
        
        self.window = Tk()
        self.window.title("Wave function Collapse")

        # initial mesure
        self.tile_size = tile_size
        self.patern_path = patern_path
        self.grid_dim = grid_dim

        #  if the dimension is under a certain value, we use a set window size
        if self.grid_dim > 7:
            self.window.geometry(f"{grid_dim*tile_size}x{grid_dim*tile_size+50}")
        else:
            self.window.geometry("200x200")
        self.window.resizable(0, 0)

        # get the tiles from the patern img
        patern_img = np.asarray(Image.open(patern_path))
        # we remove the absorbance 
        if patern_img.shape[-1] == 4:
            patern_img = patern_img[:,:,:-1]

        all_tiles_with_rotation = extract_tiles_from_img_with_rotation(patern_img, 3) if rotating_pattern else extract_tiles_from_img(patern_img, 3)
        self.unique_tiles = get_unique_tiles(all_tiles_with_rotation)
        self.tiles_probabilities = frequency_tiles(all_tiles_with_rotation) 
        self.tiles_img = [ImageTk.PhotoImage(Image.fromarray(create_uniform_tile(tile,tile_size), mode='RGB')) for tile in self.unique_tiles]
        
        # evaluate the neighbor
        self.neighboor_edge = evaluate_neighboor(self.unique_tiles)     

        assert len(self.unique_tiles) == len(self.tiles_probabilities)

        self.grid = Grid(grid_dim, len(self.unique_tiles))

        all_option = np.array([create_uniform_tile(self.unique_tiles[opt],self.tile_size) for opt in self.grid.idx_grid[0].options])
        mean_all_option = np.mean(all_option, axis=0)
        self.default_img = ImageTk.PhotoImage(Image.fromarray(mean_all_option.astype(np.uint8),mode="RGB"))
        
        # maintain state for the Label element in order to display them
        self.grid_label = []
        for i in range (self.grid_dim):
            self.grid_label.append([])
            for j in range (self.grid_dim):
                
                label = Label(self.window, image=self.default_img, borderwidth=0)
                label.grid(row=i, column=j)
                self.grid_label[i].append(label)
        
        # Restart button
        self.restartButton = Button(self.window, text="Restart", command=self.restart)
        self.restartButton.grid(row=self.grid_dim, column=0, columnspan=int(self.grid_dim/2), padx=10, pady=10)

        # Save button
        self.saveButton = Button(self.window, text="Save", command=self.save, state=DISABLED)
        self.saveButton.grid(row=self.grid_dim, column=int(self.grid_dim/2), columnspan=int(self.grid_dim/2), padx=10, pady=10)

        self.progress_bar = tqdm(total=grid_dim**2, desc='Cells collapsed', ncols=100)

    def get_lowest_entropy_cell(self):
        return self.grid.get_lowest_entropy_cell()

    def draw(self):
        for i in range(self.grid_dim):
            for j in range(self.grid_dim):
                cell = self.grid.grid[i][j]
                
                if cell.collapsed:
                    try:
                        #  For each cell, we draw the tile with the correct index in the tileImages list
                        idx = cell.options[0]
                    except IndexError:
                        # As my version has no backtrack, something there is no possible option so we start from scratch
                        self.restart()
                        return
                    self.grid_label[i][j].config(image=self.tiles_img[idx])

                elif cell.checked:
                    if len(cell.options) == 0:
                        self.restart()
                        return 
                    all_option = np.array([create_uniform_tile(self.unique_tiles[opt],self.tile_size) for opt in cell.options])
                    mean_all_option = np.mean(all_option, axis=0)
                    img = ImageTk.PhotoImage(Image.fromarray(mean_all_option.astype(np.uint8),mode="RGB"))
                    cell.cached_img = img
                    self.grid_label[i][j].config(image=img)

                cell.checked = False
    
    def collaspe_cell(self, cell:'Cell'):
        #collapse the cell
        cell.collapsed = True
        self.grid.idx_not_collapsed.remove(cell.index)
        self.progress_bar.update(1)
        try:
            options_weights = self.tiles_probabilities[cell.options]
            cell.options = random.choices(cell.options, weights=options_weights)
        except Exception as e:
            print(f'Error when collapsing a cell {cell}, Exception: {e}')
            self.restart()
            return

    def update(self):
        self.draw()
        lowest_entropy_cell = self.get_lowest_entropy_cell()

        # If were done with the grid, we can save the image
        if lowest_entropy_cell is None:
            self.saveButton.config(state=ACTIVE)
            # self.progress_bar.refresh()
            self.progress_bar.close()
            print(f'Wave Finished ! 🤩')
            return
        else:
            #collapse the cell
            self.collaspe_cell(lowest_entropy_cell)
        
            # update the entropy 
            self.reduce_entropy(lowest_entropy_cell,0)
        
        idx_to_remove = []
        for idx in self.grid.idx_not_collapsed:
            cell = self.grid.idx_grid[idx]
            if len(cell.options) == 1:
                #collapse the cell
                self.collaspe_cell(cell)
            
                # update the entropy 
                self.reduce_entropy(cell,0)

                idx_to_remove.append(idx)

        # print(f'only {len(self.grid.idx_not_collapsed)} cell to collapse before finishing')
        self.window.after(1,self.update)
    
    def reduce_entropy(self, cell: 'Cell', depth):
        # Stop propagation if max depth is reached or cell already checked
        if (depth > MAX_RECURSION_DEPTH or cell.checked):
            return
        cell.checked = True

        neighbors = self.grid.get_neighboor(cell)
        
        for dir, neighbor_cell in neighbors.items():
            if (self.check_options(cell, neighbor_cell, dir)):
                self.reduce_entropy(neighbor_cell, depth + 1);
    
    def check_options(self, cell:'Cell', neighbor:'Cell', direction):
        # Check if the neighbor is valid and not already collapsed
        if not neighbor.collapsed:
            # Collect valid options based on the current cell's adjacency rules
            validOptions = [];
            for option in cell.options:
                validOptions += self.neighboor_edge[option][direction];
            # Filter the neighbor's options to retain only those that are valid
            neighbor.options = [opt for opt in neighbor.options if opt in validOptions]

            return True;
        else:
            return False;

    def restart(self):
        hard_reset = len(self.grid.idx_not_collapsed) == 0

        self.grid = Grid(self.grid_dim, len(self.unique_tiles))
        self.saveButton.config(state=DISABLED)
        [x.config(image=self.default_img) for xs in self.grid_label for x in xs]

        if hard_reset :
            self.progress_bar.close()
            self.progress_bar = tqdm(total=self.grid_dim**2, desc='Cells collapsed', ncols=100)
        else:
            self.progress_bar.reset()

        self.update()

    def save(self):
        img = np.zeros((self.grid_dim,self.grid_dim,3), dtype=np.uint8)
        N, M, _ = img.shape
        for i in range(N):
            for j in range(M):
                img[i,j] = create_uniform_tile(self.unique_tiles[self.grid.grid[i][j].options[0]], 1)

        img = Image.fromarray(img)
        img.save("WFCOP.png")
        print('Image saved as "WFCOP.png"')

def copy_tile(source, sx, sy, w):
    """
    Copy a w x w tile from the source image to the destination array, 
    wrapping around edges using modulo indexing.

    Args:
    - source (np.ndarray): Source image as a (H, W, 4) NumPy array (RGB).
    - sx (int): X-coordinate of the top-left corner in the source.
    - sy (int): Y-coordinate of the top-left corner in the source.
    - w (int): Width of the tile.
    """

    H, W, _ = source.shape  # Get source dimensions

    # Compute wrapped indices for x and y using modulo
    x_indices = np.mod(np.arange(sx, sx + w), W)
    y_indices = np.mod(np.arange(sy, sy + w), H)

    # Extract the tile using NumPy advanced indexing
    tile = source[np.ix_(y_indices, x_indices)]  # Shape (w, w, 4)

    # Copy to destination
    return tile

def extract_tiles_from_img(img:np.array, tile_size:int) -> list:
    extracted_tiles = []
    N,M,_ = img.shape
    for i in range(N):
        for j in range(M):
            tile = copy_tile(img, i, j, tile_size)
            extracted_tiles.append(tile)
    return extracted_tiles

def extract_tiles_from_img_with_rotation(img, tile_size:int):
    result = []
    copy = img.copy()
    for _ in range(4):
        result += extract_tiles_from_img(copy,tile_size)
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

def create_uniform_tile(tile: np.ndarray, size: int) -> np.ndarray:
    """
    Creates a new tile of given size filled with the middle pixel of the input tile.
    
    Parameters:
        tile (np.ndarray): Input tile (2D or 3D NumPy array).
        size (int): Size of the output tile (size x size).
    
    Returns:
        np.ndarray: A new tile filled with the middle pixel value.
    """
    # Get the dimensions of the input tile
    h, w = tile.shape[:2]

    # Find the middle pixel coordinates
    mid_x, mid_y = h // 2, w // 2

    # Extract the middle pixel (handles both grayscale and RGB images)
    middle_pixel = tile[mid_x, mid_y]

    # Create a new tile filled with the middle pixel value
    new_tile = np.full((size, size, *middle_pixel.shape) if tile.ndim == 3 else (size, size), middle_pixel, dtype=tile.dtype)

    return new_tile

def main():
    # display size of the tile for tkinker
    tile_size = 20
    # number of cell on the grid
    grid_dim = 15
    patern_path = "tiles/allDir.png"
    rotating_pattern = False

    wfc = Wave_Function_Collapse(tile_size, patern_path, grid_dim, rotating_pattern)

    wfc.update()
    # require to maintain the window
    wfc.window.mainloop()

if __name__ == "__main__":
    main()

# TODO 
# - adapt for bigger pattern 5x5 and more
# - cleanner parameters control
# - rewrite the readme