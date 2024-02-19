from enum import Enum
import tkinter as tk
from tkinter import Canvas

import chess_api

ROWS_TITLES = "ABCDEFGH"

class TileColors(Enum):
    normal_white = "#ffffff"
    normal_black = "#7e7e7e"

    selected = "#33ff00"

    can_attack = "#ff2b2b"

    can_move_to_white = "#3eefff"
    can_move_to_black = "#3e8eff"


class Tile():
    def __init__(self, tile: chess_api.Tile, master: Canvas, pos: tuple[int, int], size: int, handler: 'Chess_Handler') -> None:
        self.tile: chess_api.Tile = tile
        self.master = master
        self.x, self.y = pos
        self.square_size: int = size
        self.handler = handler

        color = 'gray'
        if self.tile.tile_color.name == "White":
            color = 'white'

        self.image: tk.PhotoImage | None = tk.PhotoImage(file="resources/blank.png")
        self.image = self.image.subsample(260//self.square_size + 1)

        self.button: tk.Button = tk.Button(self.master, image=self.image, width=self.square_size, height=self.square_size, border=4, bg=color, command=self.select)
        self.button.grid(row=9-self.y, column=self.x)

    def draw(self) -> None:
        figure = self.tile.figure
        zoom_by = 260//self.square_size + 1

        if figure is None:
            self.image = tk.PhotoImage(file="resources/blank.png")
            self.image = self.image.subsample(zoom_by)

            self.button.configure(image=self.image)

            return

        self.image = tk.PhotoImage(file="resources/{}_{}.png".format(figure.color.name, figure.type.name))
        self.image = self.image.subsample(zoom_by)

        self.button.configure(image=self.image)

    def select(self) -> None:
        updates_tiles = self.handler.board.needs_update()
        self.handler.board.select_tile(self.tile)

        self.handler.update(updates_tiles.union(self.handler.board.needs_update()))

    def change_color(self, color_State: TileColors) -> None:
        self.button.config(bg = color_State.value)

class Chess_Handler():
    def __init__(self, master: Canvas, size: int) -> None:
        self.board = chess_api.Board()
        self.master = master
        self.board_drawing = {col + str(row): Tile(self.board.board[col + str(row)], self.master, (i, row), size, self) for i, col in enumerate(ROWS_TITLES) for row in range(1, 9)}
        self.turn = self.board.turn
        self.square_size = size

        for tile in self.board_drawing.values():
            tile.draw()

    def update(self, tile_coords: set[str]):
        for coords in tile_coords:
            tile = self.board_drawing[coords].tile

            if tile.tile_state == chess_api.TileState.Normal:
                self.board_drawing[coords].draw()
                if tile.tile_color.name == "White":
                    self.board_drawing[coords].change_color(TileColors.normal_white)
                    continue
                self.board_drawing[coords].change_color(TileColors.normal_black)

            if tile.tile_state == chess_api.TileState.Selected:
                self.board_drawing[coords].change_color(TileColors.selected)
                continue

            if tile.tile_state == chess_api.TileState.Can_move_to:
                if tile.tile_color.name == "White":
                    self.board_drawing[coords].change_color(TileColors.can_move_to_white)
                    continue
                self.board_drawing[coords].change_color(TileColors.can_move_to_black)

            if tile.tile_state == chess_api.TileState.Can_take:
                self.board_drawing[coords].change_color(TileColors.can_attack)
                continue


screen_width = 1920
screen_height = 1080

def main() -> None:
    main_window = tk.Tk()
    screen_width = main_window.winfo_screenheight()
    screen_height = main_window.winfo_screenwidth()

    main_window.geometry("{}x{}".format(screen_height, screen_width))
    main_window.title("Chess viewer")

    tile_size = min(screen_height, screen_width) // 10

    board = Canvas(main_window, width = (tile_size * 10), height = (tile_size * 10))
    moves = Canvas(main_window, width = (tile_size * 10), height = (tile_size * 10))
    moves.config(background='red')

    board.pack(side="left", padx=(tile_size, 0))

    grid = Chess_Handler(board, tile_size)

    board.update()
    moves.pack(side="left")

    main_window.mainloop()

if __name__ == "__main__":
    main()