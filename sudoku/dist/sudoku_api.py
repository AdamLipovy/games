Position = tuple[int, int]
Tile_data = dict[Position, int| set[int]]

poss_val = set([i for i in range(1,10)])

class Sudoku():
    def __init__(self, data: Tile_data) -> None:
        self.picture: Tile_data = data
        self.picture.update({(row, col): poss_val.copy() for row in range(9) for col in range(9) if (row, col) not in self.picture.keys()})

    def iteration(self) -> bool:
        for row_i in range(9):
            for col_i in range(9):
                tile = self.picture.get((row_i, col_i), None)

                if isinstance(tile, int):
                    self.remove_from_square(tile, (row_i, col_i))
                    self.remove_num_from_column(tile, col_i)
                    self.remove_num_from_row(tile, row_i)

        self.check_only_one_possible()

        return self.normalize()

    def solve(self, is_origin: bool):
        has_changed = True
        iteration = 0
        while has_changed:

            has_changed = self.iteration()

            iteration += 1
        if not is_origin:
            return 
        max_length = 9
        equal_length: dict[Position, set[int]] = {}
        for tile, values in self.picture.items():
            if isinstance(values, set):
                if len(values) < max_length:
                    max_length = len(values)
                    equal_length.clear()
                    continue
                if len(values) == max_length:
                    equal_length[tile] = values

        if len(equal_length) != 0 and max_length != 1:
            for cur_tile, value in equal_length.items():
                for permutation in value:
                    variation = Sudoku({tile: val for tile, val in self.picture.items() if isinstance(val, int)})
                    variation.picture[cur_tile] = permutation

                    variation.solve(False)
                    if variation.is_valid():
                        self.picture.update(variation.picture.items())
                        return
        return

    def is_valid(self) -> bool:
        for (x, y), val in self.picture.items():
            if isinstance(val, set) or val is None:
                return False
            for i in range(9):
                if (self.picture[(x, i)] == val and i != y) or\
                        (self.picture[(i, y)] == val and i != x):
                    return False
        return True

    def check_only_one_possible(self):
        # squares changer
        for row_i in range(3):
            for col_i in range(3):
                tiles = self.get_square((row_i, col_i))
                optional_values: dict[int, int] = self.values_in_section(tiles)
                
                self.change_to_int(optional_values, tiles)

        # cols changer
        for i in range(9):
            col_section = self.get_col(i)
            col_value_count: dict[int, int] = self.values_in_section(col_section)

            self.change_to_int(col_value_count, col_section)

            row_section = self.get_row(i)
            row_value_count: dict[int, int] = self.values_in_section(row_section)

            self.change_to_int(row_value_count, row_section)

        return
    
    def change_to_int(self, value_count: dict[int, int], section: list[set[int] | int]) -> None:
        change_to_int = []
        for val, count in value_count.items():
            if count == 1:
                change_to_int.append(val)
        
        for val in change_to_int:
            for tile in section:
                if isinstance(tile, int):
                    continue
                if val in tile:
                    change_to_int.remove(val)
                    tile.clear()
                    tile.add(val)
                    break

    def values_in_section(self, tiles: list[set[int] | int]) -> dict[int, int]:
        aux: dict[int, int] = {i: 0 for i in poss_val}
        for tile in tiles:
            if isinstance(tile, int):
                continue
            
            for val in tile:
                aux[val] += 1

        return aux
    
    def get_square(self, position: Position) -> list[set[int] | int]:
        aux: list[set[int] | int] = []
        row_i, col_i = position
        square_row = row_i // 3
        square_col = col_i // 3

        for row_i in range(3):
            for col_i in range(3):
                tile = self.picture.get((3 * square_row + row_i, 3 * square_col + col_i), None)
                if tile is not None:
                    aux.append(tile)
        return aux
    
    def get_col(self, col_i: int) -> list[set[int] | int]:
        aux: list[set[int] | int] = []

        for i in range(9):
            aux.append(self.picture.get((i, col_i), poss_val.copy()))
        return aux

    def get_row(self, row_i: int) -> list[set[int] | int]:
        aux: list[set[int] | int] = []

        for i in range(9):
            aux.append(self.picture.get((row_i, i), poss_val.copy()))
        return aux


    def normalize(self) -> bool:
        aux = False
        for row_i in range(9):
            for col_i in range(9):
                tile = self.picture.get((row_i, col_i), None)
                
                if isinstance(tile, int) or tile is None:
                    continue

                if len(tile) == 1:
                    self.picture[(row_i, col_i)] = tile.pop()
                    aux = True
        return aux        


    def remove_from_square(self, num: int, position: Position):
        
        for tile in self.get_square(position):
            if isinstance(tile, int):
                continue
            
            if num in tile:
                tile.remove(num)

    def remove_num_from_row(self, num: int, row_i: int):
        for col_i in range(9):
            tile = self.picture.get((row_i, col_i), None)

            if isinstance(tile, int):
                continue

            if tile is None:
                self.picture[(row_i, col_i)] = poss_val - {num}
                continue

            if num in tile:
                tile.remove(num)

    def remove_num_from_column(self, num: int, col_i: int):
        for row_i in range(9):
            tile = self.picture.get((row_i, col_i), None)

            if isinstance(tile, int):
                continue

            if tile is None:
                self.picture[(row_i, col_i)] = poss_val - {num}
                continue

            if num in tile:
                tile.remove(num)


    def show(self):
        # print top line
        print("┌───┬───┬───┬───┬───┬───┬───┬───┬───┐")
        for row_i in range(9):
            row_data: list[ int| set[int]] = []
            for col_i in range(9):
                val = self.picture.get((row_i, col_i), poss_val)
                row_data.append(val)
            
            # first line contains only 1, 2, 3
            for x in range(0, 3):
                line_printer = "|"
                for tile in row_data:                    
                    for i in range(1 + x * 3, 4 + x * 3):
                        if isinstance(tile, int) and tile == i or\
                            isinstance(tile, set) and i in tile:
                            line_printer += str(i)
                        else:
                            line_printer += " "
                    line_printer += "|"
                print(line_printer)
            
            if row_i != 8:
                print("├───┼───┼───┼───┼───┼───┼───┼───┼───┤")
            else:
                print("└───┴───┴───┴───┴───┴───┴───┴───┴───┘")

def main():
    prev = Sudoku({(0, 1): 1, (0, 7): 9,
                   (1, 2): 6, (1, 3): 1, (1, 5): 4, (1, 6): 2,
                   (2, 0): 2, (2, 4): 6, (2, 8): 5,
                   (3, 1): 9, (3, 3): 6, (3, 5): 3, (3, 7): 7,
                   (4, 4): 4,
                   (5, 1): 4, (5, 3): 8, (5, 5): 9, (5, 7): 2,
                   (6, 0): 3, (6, 4): 9, (6, 8): 1,
                   (7, 2): 1, (7, 3): 7, (7, 5): 6, (7, 6): 8,
                   (8, 1): 8, (8, 7): 5})
    
    prev.solve(True)
    print(prev.is_valid())

    prev2 = Sudoku({(0, 2): 7, (0, 4): 9, (0, 7): 3,
                    (1, 1): 6, (1, 5): 2, (1, 8): 7,
                    (2, 1): 1, (2, 5): 4, (2, 6): 6,
                    (3, 0): 7, (3, 4): 3, (3, 6): 9,
                    (4, 1): 5, (4, 2): 6, (4, 6): 8, (4, 7): 1,
                    (5, 2): 3, (5, 4): 6, (5, 8): 2,
                    (6, 2): 4, (6, 3): 2, (6, 7): 8,
                    (7, 0): 6, (7, 3): 5, (7, 7): 2,
                    (8, 1): 3, (8, 4): 8, (8, 6): 1})
    
    prev2.solve(True)

if __name__ == "__main__":
    main()