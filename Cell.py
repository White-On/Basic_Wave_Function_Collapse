class Cell:
    def __init__(self, nbTiles) -> None:
        self.collapsed = False
        self.options = [i for i in range(nbTiles)]
    
    def __repr__(self) -> str:
        return f"Collapsed:{self.collapsed},Options:{self.options}"
    
    def copy(self) -> "Cell":
        copy = Cell(1)
        copy.collapsed = self.collapsed
        copy.options = self.options.copy()
        return copy
    
    @classmethod
    def createCellFromOptions(cls, options) -> "Cell":
        copy = Cell(len(options))
        copy.collapsed = False
        copy.options = options
        return copy

    def __len__(self):
        return len(self.options)

