from random import random
import tkinter as tk
from tkinter import Canvas, ttk
from enum import Enum
from tkinter.font import Font
from sudoku_api import Sudoku
import random
import time

tile_size = 70

class SudokuCommander():
    def __init__(self, playground: 'SudokuPalet', lock_button: 'Toggle_button', info: tk.Label, hardness: tk.Scale) -> None:
        self.selected_tile: Tile | None = None
        self.tiles: dict[tuple[int, int], Tile] = {(tile.y, tile.x):tile for square in playground.squares\
                                                    for tile in square.tiles}
        self.lock_button = lock_button
        self.lock_button.commander = self
        self.info = info
        self.sudoku: Sudoku | None = None
        self.hardness = hardness

        self.has_been_checked = False

        self.start: int = 0
        self.helps: int = 0

        for tile in self.tiles.values():
            tile.commander = self
        
    def select_tile(self, tile: 'Tile') -> None:
        if self.has_been_checked:
            for tmptile in self.tiles.values():
                if tmptile.state == States.good:
                    tmptile.stateChange(States.locked)
                if tmptile.state == States.bad:
                    tmptile.stateChange(States.nonactive)
            
            self.has_been_checked = False

        if self.selected_tile is not None:
            if tile == self.selected_tile:
                self.selected_tile.stateChange(States.nonactive)
                self.selected_tile = None
                return

            self.selected_tile.stateChange(States.nonactive)
            self.selected_tile = tile
            self.selected_tile.stateChange(States.active)

            # change state
            pass
        self.selected_tile = tile
        self.selected_tile.stateChange(States.active)
        return
    
    def change_number(self, val: int) -> None:
        if self.lock_button.state:
            if self.selected_tile is None:
                return
            if self.selected_tile.checked_value == val:
                self.selected_tile.checked_value = None
                self.selected_tile.val = None
                self.selected_tile.draw_values()
                return
            
            self.selected_tile.checked_value = val
            self.selected_tile.val = val
            self.selected_tile.draw_values()
            return

        if self.selected_tile is None:
            return
        values = self.selected_tile.val
        if values is None:
            self.selected_tile.val = val
            self.selected_tile.draw_values()
            return
        if isinstance(values, int):
            if values == val:
                self.selected_tile.val = None
                self.selected_tile.draw_values()
                return
            self.selected_tile.val = {values, val}
            self.selected_tile.draw_values()
            return
        if val in values:
            values.remove(val)
            if len(values) == 1:
                self.selected_tile.val = values.pop()
            self.selected_tile.draw_values()
            return
        values.add(val)
        self.selected_tile.draw_values()
        return

    def change_number_key(self, key_press) -> None:
        self.change_number(int(key_press.char))

    def lock_state(self) -> None:
        if not self.lock_button.state:
            for tile in self.tiles.values():
                if tile.state is States.locked:
                    tile.stateChange(States.nonactive)
            return

        if self.selected_tile is not None:
            self.select_tile(self.selected_tile)

        for tile in self.tiles.values():
            if tile.checked_value is not None:
                tile.stateChange(States.locked)
        self.sudoku = Sudoku({pos: tile.checked_value for pos, tile in self.tiles.items() if tile.checked_value is not None})
        self.sudoku.solve(True)
        for pos, val in self.sudoku.picture.items():
            self.tiles[pos].checked_value = val
        self.start = round(time.time())
        return

    def take_most(self) -> list[tuple[int, int]]:
        aux: list[tuple[int, int]] = []
        max_size = 1
        if self.sudoku is None:
            return [(0, 0)]
        for pos, val in self.sudoku.picture.items():
            if val is None or isinstance(val, int):
                continue
            if len(val) > max_size:
                aux = []
                max_size = len(val)
                aux.append(pos)
                continue

            if len(val) == max_size:
                aux.append(pos)
        return aux

    def solve(self) -> None:
        # self.info.configure(text="zkouším řešit...")
        # self.sudoku = Sudoku({position: tile.checked_value for position, tile in self.tiles.items() if tile.checked_value is not None})
        # self.sudoku.solve(True)
        assert self.sudoku is not None
        solvable = True
        for position, value in self.sudoku.picture.items():
            if isinstance(value, set):
                solvable = False
                continue
            self.tiles[position].checked_value = value
        
        for tile in self.tiles.values():
            tile.val = tile.checked_value
            tile.draw_values()

        if solvable:
            self.info.configure(text="řešitelné", bg="#34eb37")
            return

        self.info.configure(text="neřešitelné", bg="#db091e")

        return
    
    def show_solution(self) -> None:
        for tile in self.tiles.values():
            tile.val = tile.checked_value
            tile.draw_values()

    def generate(self) -> None:
        self.reset()
        self.sudoku = Sudoku({})
        what_to_show = set()

        self.helps = 0

        generations = 1
        i = 0

        self.info.configure(text="generuji\n pokus - " + str(generations), bg="#db091e")
        self.info.update()
        while not self.sudoku.is_valid():
            tile_pos = self.get_random_tile(generations > (15 - self.hardness.get()) * 400)

            possible_values = self.sudoku.picture[tile_pos]
            if possible_values == set() or i > 70:
                self.sudoku = Sudoku({})
                what_to_show.clear()
                generations += 1
                self.info.configure(text="generuji .\n pokus - " + str(generations), bg="#db091e")
                self.info.update()
                i = 0

            if isinstance(possible_values, set) and possible_values != set():
                self.sudoku.picture[tile_pos] = random.choice(list(possible_values)) 
                self.sudoku.iteration()
                what_to_show.add(tile_pos)
            
            i += 1

        self.info.configure(text="vygenerováno {} \nzadání".format("těžší" if (15 - self.hardness.get()) else "lehčí"), bg="#29ff57")

        i = 0
        while i < round(self.hardness.get()):
            tile_pos = self.get_random_tile(False)
            if tile_pos not in what_to_show:
                i += 1
                what_to_show.add(tile_pos)

        for tile in self.tiles.keys():
            desired_tile = self.tiles[tile]
            desired_tile.checked_value = self.sudoku.picture[tile]
            if tile in what_to_show:
                desired_tile.val = desired_tile.checked_value
                desired_tile.stateChange(States.locked)
                desired_tile.draw_values()
        
        self.start = int(time.time())
        return

    def get_random_tile(self, enforce_solution: bool) -> tuple[int, int]:
        res = self.take_most()
        if res == [] or enforce_solution:
            return random.choice(list(self.tiles.keys()))
        return random.choice(res)

    def help(self) -> None:
        acquired_positions = {pos for pos, tile in self.tiles.items() if isinstance(tile.val, int)}
        temp: dict[tuple[int, int], int| set[int]] = {}

        for pos in acquired_positions:
            temp_val = self.tiles[pos].val
            if temp_val is not None:
                temp[pos] = temp_val

        temp_sudoku = Sudoku(temp)
        temp_sudoku.iteration()

        new_positions = {pos for pos, val in temp_sudoku.picture.items() if isinstance(val, int)}

        new_positions.difference_update(acquired_positions)

        for _ in range(3):
            self.tiles[new_positions.pop()].stateChange(States.focus)

        self.helps += 1

        return    

    def reset(self) -> None:
        for tile in self.tiles.values():
            tile.val = None
            tile.checked_value = None
            tile.draw_values()
            tile.stateChange(States.nonactive)
        self.sudoku = None
        return

    def check(self) -> None:
        if self.selected_tile is not None:
            self.selected_tile.stateChange(States.nonactive)
        self.selected_tile = None
        all_checked = True
        for tile in self.tiles.values():
            if tile.val is None:
                all_checked = False
                continue

            if isinstance(tile.val, int):
                if tile.val == tile.checked_value:
                    if tile.state == States.nonactive:
                        tile.stateChange(States.good)
                    continue

                tile.stateChange(States.bad)
                all_checked = False
                continue

            if tile.checked_value not in tile.val:
                tile.stateChange(States.bad)
        self.has_been_checked = True

        if all_checked:
            end_time = int(time.time() - self.start)
            if end_time % 60 < 10:
                self.info.config(text="čas: {}:0{}\n nápověd: {}".format(end_time // 60, end_time % 60, self.helps))
                return
            self.info.config(text="čas: {}:{}\n nápověd: {}".format(end_time // 60, end_time % 60, self.helps))
            return
        self.helps += 1
        return

    def move_selected(self, command) -> None:
        if self.selected_tile is None:
            return
        row, col = self.selected_tile.y, self.selected_tile.x
        if command.keysym == "Left":
            offset_row, offset_col = Directions.Left.value
        elif command.keysym == "Right":
            offset_row, offset_col = Directions.Right.value
        elif command.keysym == "Up":
            offset_row, offset_col = Directions.Up.value
        elif command.keysym == "Down":
            offset_row, offset_col = Directions.Down.value
        else:
            print(command.keysym)
            return
        if 0 <= row + offset_row <= 8 and 0 <= col + offset_col <= 8:
            new_position = (row + offset_row, col + offset_col)
            if self.tiles[new_position].state == States.nonactive:
                self.select_tile(self.tiles[new_position])
        return

class SudokuPalet():
    def __init__(self, master: tk.Canvas) -> None:
        master.create_rectangle(0, 0, tile_size*9, tile_size*9)

        self.squares: list[SudokuSquare] = []

        for row in range(3):
            for col in range(3):
                if (row + col) % 2 == 0:
                    self.squares.append(SudokuSquare(master, row, col, "#aeaeae"))
                else:
                    self.squares.append(SudokuSquare(master, row, col, "#8e8e8e"))

class SudokuSquare():
    def __init__(self, master: tk.Canvas, row: int, col: int, default_color: str) -> None:
        self.master = master
        master.create_rectangle((row * 3 + 1) * tile_size, (col * 3 + 1) * tile_size,\
                                ((row + 1) * 3 + 1) * tile_size, ((col + 1) * 3 + 1) * tile_size)

        self.row = row
        self.col = col
        self.tiles: list[Tile] = []
        
        for tile_col in range(3):
            for tile_row in range(3):
                self.tiles.append(Tile(master, row * 3 + tile_row, col * 3 + tile_col, default_color))

class Tile():
    def __init__(self, master: tk.Canvas, row_pos: int, col_pos: int, default_color: str) -> None:
        self.master = master
        self.x = row_pos
        self.y = col_pos
        self.checked_value: int | set[int] | None = None
        self.val: int | set[int] | None = None
        self.state: States = States.nonactive
        self.default_color = default_color

        self.commander: SudokuCommander | None = None

        self.button = tk.Button(self.master, text="", command=self.notice_commander, bg=default_color)
        self.button.place(width=tile_size, height=tile_size, x = tile_size * (row_pos + 1), y = tile_size * (col_pos + 1))

        master.create_rectangle((row_pos + 1) * tile_size, (col_pos + 1) * tile_size,\
                                (row_pos + 2) * tile_size, (col_pos + 2) * tile_size)

    def draw_values(self) -> None:
        if isinstance(self.val, int):
            self.button.config(text=self.val, font=Font(size=30))
            return

        if self.val is None:
            self.button.config(text="")
            return

        new_text = ""
        for row in range(3):
            for i in range(1, 4):
                checking_val = (row * 3 + i)
                if checking_val in self.val:
                    new_text += str(checking_val)
                else:
                    new_text += "  "
                if i != 3:
                    new_text += "   "
            if row != 2:
                new_text += "\n"
        self.button.config(text=new_text, font=Font(size=10))

        pass

    def update(self) -> None:
        if self.state.value == States.active.value:
            self.button.configure(bg="#ffffff", state="normal")
        elif self.state.value == States.nonactive.value:
            self.button.configure(bg=self.default_color, state="normal")
        elif self.state.value == States.locked.value:
            self.button.configure(bg=self.default_color, state="disabled", disabledforeground="#ffffff")
        elif self.state.value == States.good.value:
            self.button.configure(bg="#6eff77", state="disabled", disabledforeground="#000000")
        elif self.state.value == States.bad.value:
            self.button.configure(bg="#ff3d64", state="normal")
        elif self.state.value == States.focus.value:
            self.button.configure(bg="#fff024", state="normal")
        else:
            assert False
        return

    def stateChange(self, state: 'States') -> None:
        self.state = state
        self.update()

    def notice_commander(self) -> None:
        if self.state.value == 3:
            return
        if self.commander is None:
            return
        self.commander.select_tile(self)

class States(Enum):
    active = 1
    nonactive = 2
    locked = 3
    good = 4
    bad = 5
    focus = 6

class Directions(Enum):
    Left = (0, -1)
    Right = (0, 1)
    Up = (-1, 0)
    Down = (1, 0)

class Toggle_button():
    def __init__(self, root, __text) -> None:
        self.button = tk.Button(root, text=__text, bg = "#dedede", command=self.state_toggle)
        self.state: bool = False

        self.commander: SudokuCommander | None = None


    def state_toggle(self) -> None:
        assert self.commander is not None
        if self.state:
            self.button.configure(bg="#dedede")
            self.commander.lock_state()
        else:
            self.button.configure(bg="#696969")
            self.commander.lock_state()

        self.state = not self.state

class Number_dial():
    def __init__(self, root, commander: SudokuCommander) -> None:
        ttk.Button(root, text = 1, command=lambda:commander.change_number(1)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 1.75, y = tile_size * 10.1)
        ttk.Button(root, text = 2, command=lambda:commander.change_number(2)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 2.25, y = tile_size * 10.1)
        ttk.Button(root, text = 3, command=lambda:commander.change_number(3)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 2.75, y = tile_size * 10.1)
        ttk.Button(root, text = 4, command=lambda:commander.change_number(4)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 1.75, y = tile_size * 10.6)
        ttk.Button(root, text = 5, command=lambda:commander.change_number(5)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 2.25, y = tile_size * 10.6)
        ttk.Button(root, text = 6, command=lambda:commander.change_number(6)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 2.75, y = tile_size * 10.6)
        ttk.Button(root, text = 7, command=lambda:commander.change_number(7)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 1.75, y = tile_size * 11.1)
        ttk.Button(root, text = 8, command=lambda:commander.change_number(8)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 2.25, y = tile_size * 11.1)
        ttk.Button(root, text = 9, command=lambda:commander.change_number(9)).place(width = tile_size//2, height = tile_size//2, x = tile_size * 2.75, y = tile_size * 11.1)

def main() -> None:
    main_window = tk.Tk()
    main_window.geometry(str(tile_size*11) + "x" + str(round(tile_size*11.5)))
    main_window.title("Sudoku které dává rozhodně validní odpovědi 3000")

    root = Canvas(main_window, width=tile_size*11, height=tile_size*12)
    sudokugrid = SudokuPalet(root)

    tbutt = Toggle_button(root, "režim zadávání")
    info = tk.Label(root, text="----")
    info.place(x=tile_size*3.5,y=tile_size*10.6)

    hardness = tk.Scale(root, from_=0, to=15, orient="horizontal")
    hardness.place(x=tile_size*3.5,y=tile_size*11.2)

    commander = SudokuCommander(sudokugrid, tbutt, info, hardness)

    ttk.Button(root, text="resetovat a zadat nové zadání", command=commander.reset).place(x=tile_size*7,y=tile_size*10.15)
    ttk.Button(root, text="řeš", command=commander.solve).place(x=tile_size*7, y=tile_size*10.5)
    ttk.Button(root, text="nápověda", command=commander.help).place(x=tile_size*8, y=tile_size*10.5)
    ttk.Button(root, text="zkontroluj", command=commander.check).place(x=tile_size*9, y=tile_size*10.5)
    ttk.Button(root, text="generovat zadání", command=commander.generate).place(x=tile_size*7,y=tile_size*10.95)

    ttk.Label(root, text="informace:").place(x=tile_size*3.5,y=tile_size*10.2)

    ttk.Label(root, text="složitost:").place(x=tile_size*3.5,y=tile_size*11)

    for i in range(1, 10):
        main_window.bind(str(i), commander.change_number_key)

    main_window.bind("<Left>", commander.move_selected)
    main_window.bind("<Down>", commander.move_selected)
    main_window.bind("<Right>", commander.move_selected)
    main_window.bind("<Up>", commander.move_selected)

    tbutt.button.place(x=tile_size*5,y=tile_size*10.5)
    root.place(x=tile_size*5.5, y=tile_size*5.25, anchor="center")

    Number_dial(root, commander)

    main_window.mainloop()

if __name__ == "__main__":
    main()