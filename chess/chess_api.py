from enum import Enum

ROWS_TITLES = "ABCDEFGH"

Notation = str | tuple[int, int]

class Figure_type(Enum):

    Pawn = 0
    Rook = 1
    Bishop = 2
    Horse = 3
    Queen = 4
    King = 5

class Color(Enum):
    White = 0
    Black = 1

class TileState(Enum):
    Normal = 0
    Selected = 1
    Can_move_to = 2
    Can_take = 3
    Check = 4
    Cant_Select = 5

class Places():
    attacks: list[tuple[int, int]]
    attacks_limit: int | None

    movement: list[tuple[int, int]]
    movement_limit: int | None

class Figure():
    def __init__(self, type: Figure_type, color: Color) -> None:
        self.type: Figure_type = type
        self.color: Color = color
        self.moved_from_start: bool = False

    def movement_options(self) -> Places:
        aux = Places()
        if self.type.name == "Pawn":            # PAWN

            aux.movement = [(0, 1)]
            aux.attacks = [(1, 1), (-1, 1)]
            aux.attacks_limit = 1

            if not self.moved_from_start:
                aux.movement_limit = 2
            else:
                aux.movement_limit = 1

        elif self.type.name == "Bishop":        # BISHOP

            aux.movement = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
            aux.movement_limit = None

            aux.attacks = aux.movement
            aux.attacks_limit = None
        
        elif self.type.name == "Horse":         # HORSE

            aux.movement = [(2, -1), (2, 1), (1, -2), (1, 2), (-1, -2), (-1, 2), (-2, -1), (-2, 1)]
            aux.movement_limit = 1

            aux.attacks = aux.movement
            aux.attacks_limit = 1

        elif self.type.name == "Rook":          # ROOK
            
            aux.movement = [(1, 0), (-1, 0), (0, -1), (0, 1)]
            aux.movement_limit = None

            aux.attacks = aux.movement
            aux.attacks_limit = None

        elif self.type.name == "Queen":         # QUEEN

            aux.movement = [(1, 0), (-1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            aux.movement_limit = None

            aux.attacks = aux.movement
            aux.attacks_limit = None

        elif self.type.name == "King":          # KING

            aux.movement = [(1, 0), (-1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            aux.movement_limit = 1

            aux.attacks = aux.movement
            aux.attacks_limit = 1

        else:
            assert False

        return aux

    def select_figure(self):
        pass

class Tile():
    def __init__(self, color: Color, position: str) -> None:
        self.figure: Figure | None = None
        self.tile_color: Color = color
        self.tile_state: TileState = TileState.Normal
        self.position: str = position

        # if true can be en passant or can castle
        self.special_tile: bool = False

    def optional_positions(self) -> Places:
        if self.figure is None:
            return Places()
        
        return self.figure.movement_options()

    def move(self, from_tile: 'Tile') -> None:
        self.figure = from_tile.figure
        self.figure.moved_from_start = True
        from_tile.figure = None

class Board():

    white_king_tile: Tile
    black_king_tile: Tile

    def __init__(self):
        self.board: dict[str, Tile] = {col + str(row): Tile(Color((i + row) % 2), col + str(row)) for i, col in enumerate(ROWS_TITLES) for row in range(1, 9)}
        self.setup_board(None)

        self.selected_tile: Tile | None = None
        self.attacked_tiles: set[Tile] | None = None
        self.can_move_tiles: set[Tile] | None = None

        self.en_passant_tile: Tile | None = None
        self.en_passant_fig: Figure | None = None

        self.turn: Color = Color.White

    def needs_update(self) -> set[str]:
        aux: set[str] = set()
        if self.selected_tile is not None:
            aux.add(self.selected_tile.position)

        if self.attacked_tiles is not None:
            for tile in self.attacked_tiles:
                aux.add(tile.position)
        
        if self.can_move_tiles is not None:
            for tile in self.can_move_tiles:
                aux.add(tile.position)        

        return aux

    def setup_board(self, special_setup: dict[str, tuple[Figure_type, Color]] | None) -> None:
        if special_setup is None:
            # White
            self.board["A1"].figure = Figure(Figure_type.Rook, Color.White)
            self.board["H1"].figure = Figure(Figure_type.Rook, Color.White)

            self.board["B1"].figure = Figure(Figure_type.Horse, Color.White)
            self.board["G1"].figure = Figure(Figure_type.Horse, Color.White)

            self.board["C1"].figure = Figure(Figure_type.Bishop, Color.White)
            self.board["F1"].figure = Figure(Figure_type.Bishop, Color.White)

            self.board["D1"].figure = Figure(Figure_type.Queen, Color.White)
            self.board["E1"].figure = Figure(Figure_type.King, Color.White)

            for row in ROWS_TITLES:
                self.board[row+"2"].figure = Figure(Figure_type.Pawn, Color.White)

            # Black

            self.board["A8"].figure = Figure(Figure_type.Rook, Color.Black)
            self.board["H8"].figure = Figure(Figure_type.Rook, Color.Black)

            self.board["B8"].figure = Figure(Figure_type.Horse, Color.Black)
            self.board["G8"].figure = Figure(Figure_type.Horse, Color.Black)

            self.board["C8"].figure = Figure(Figure_type.Bishop, Color.Black)
            self.board["F8"].figure = Figure(Figure_type.Bishop, Color.Black)

            self.board["D8"].figure = Figure(Figure_type.Queen, Color.Black)
            self.board["E8"].figure = Figure(Figure_type.King, Color.Black)
            
            for row in ROWS_TITLES:
                self.board[row+"7"].figure = Figure(Figure_type.Pawn, Color.Black)

            self.white_king_tile = self.board["E1"]
            self.black_king_tile = self.board["E8"]

            return
        
        for pos, (fig, color) in special_setup.items():
            self.board[pos].figure = Figure(fig, color)
    
    def select_tile(self, tile: Tile) -> None:

        if tile.tile_state == TileState.Normal:
            self.reset_states()

            if tile.figure is None or tile.figure.color != self.turn:
                return
 
            tile.tile_state = TileState.Selected

            can_move_to, can_attack = self.optional_places(tile.position, True)
            self.selected_tile = tile
            self.attacked_tiles = set()
            self.can_move_tiles = set()

            if can_move_to is not None:
                for tile_cord in can_move_to:
                    self.board[tile_cord].tile_state = TileState.Can_move_to
                    self.attacked_tiles.add(self.board[tile_cord])

            if can_attack is not None:
                for tile_cord in can_attack:
                    self.board[tile_cord].tile_state = TileState.Can_take
                    self.attacked_tiles.add(self.board[tile_cord])
            return

        if tile.tile_state == TileState.Selected:
            self.reset_states()
            return
        
        if tile.tile_state == TileState.Can_move_to or tile.tile_state == TileState.Can_take:
            if self.selected_tile is None:
                assert False
            
            tile.move(self.selected_tile)
            if self.turn == Color.White:
                self.turn = Color.Black
            else:
                self.turn = Color.White
            self.reset_states()

    def reset_states(self) -> None:
        if self.selected_tile is not None:
            self.selected_tile.tile_state = TileState.Normal
            if self.attacked_tiles is not None:
                for sub_tiles in self.attacked_tiles:
                    sub_tiles.tile_state = TileState.Normal
                self.attacked_tiles = None

            if self.can_move_tiles is not None:
                for sub_tiles in self.can_move_tiles:
                    sub_tiles.tile_state = TileState.Normal
                self.can_move_tiles = None

    def optional_places(self, position: str, attacks: bool) -> tuple[set[str], set[str]]:
        tile = self.board[position]
        fig = tile.figure

        assert fig is not None

        if tile is None:
            return set(), set()
        
        aux_movement: set[str] = set()

        movement_data = tile.optional_positions()

        o_x, o_y = convert_to_computer_notation(position)

        for movement_x, movement_y in movement_data.movement:

            if fig.color == Color.Black:
                movement_x, movement_y = movement_x * -1, movement_y * -1

            if movement_data.movement_limit is None:
                for i in range(1, 9):
                    checking_tile = o_x + movement_x * i, o_y + movement_y * i

                    if not self.in_bounds(checking_tile) or self.is_occupied(checking_tile):
                        break
                    aux_movement.add(convert_to_chess_notation(checking_tile))
                
                continue

            for i in range(1, movement_data.movement_limit + 1):
                checking_tile = o_x + movement_x * i, o_y + movement_y * i

                if not self.in_bounds(checking_tile) or self.is_occupied(checking_tile):
                    break
                aux_movement.add(convert_to_chess_notation(checking_tile))

        if not attacks:
            return aux_movement, set()
        
        aux_attacks: set[str] = set()
        
        attacker_figure = self.board[position].figure
        assert attacker_figure is not None

        for movement_x, movement_y in movement_data.attacks:

            if fig.color == Color.Black:
                movement_x, movement_y = movement_x * -1, movement_y * -1

            if movement_data.attacks_limit is None:
                for i in range(1, 9):
                    checking_tile = o_x + movement_x * i, o_y + movement_y * i
                    if not self.in_bounds(checking_tile):
                        break
                    
                    if self.board[convert_to_chess_notation(checking_tile)].figure is None:
                        continue

                    if self.board[convert_to_chess_notation(checking_tile)].figure.color != attacker_figure.color:
                        aux_attacks.add(convert_to_chess_notation(checking_tile))
                    break
                    

                continue

            for i in range(1, movement_data.attacks_limit + 1):
                    checking_tile = o_x + movement_x * i, o_y + movement_y * i
                    if not self.in_bounds(checking_tile):
                        break
                    
                    attacking_tile = self.board[convert_to_chess_notation(checking_tile)]

                    if attacking_tile.figure is None and self.en_passant_tile != attacking_tile:
                        continue

                    # holy shit
                    if attacking_tile.figure.color != attacker_figure.color or\
                            (self.en_passant_fig is not None and self.en_passant_tile is not None and\
                            attacker_figure.type == Figure_type.Pawn and attacker_figure.color != self.en_passant_fig.color) :
                        aux_attacks.add(convert_to_chess_notation(checking_tile))
                    break

        return aux_movement, aux_attacks

    def in_bounds(self, tile: Notation) -> bool:
        
        if isinstance(tile, str):
            tile = convert_to_computer_notation(tile)
        
        x, y = tile

        return 0 < x < 9 and  0 < y < 9
    
    def is_occupied(self, tile: Notation) -> bool:

        if isinstance(tile, tuple):
            tile = convert_to_chess_notation(tile)

        return self.board[tile].figure != None
    
    # whether or not can figure be moved without exposing king to enemy
    def can_attack(self, tile: Notation, attackers_color: Color) -> bool:

        if isinstance(tile, tuple):
            tile = convert_to_chess_notation(tile)
        
        fig = self.board[tile].figure

        # this makes 0 sense idk what i was doing TODO
        return fig != None and fig.color != attackers_color and self.is_protected(tile, attackers_color)
    
        # TODO -- en passaunt

    def en_passant(self):
        pass


    # if by moving the figure, same color king doesn't get checked (if current figure is pinned or not)
    def is_protected(self, tile: str, color: Color) -> bool:

        new_board = Board()
        # copies current board and removes the figure
        new_board.setup_board({position: (tile.figure.type, tile.figure.color) for position, tile in self.board.items() if tile.figure != None})
        new_board.board[tile].figure = None
        print(new_board.check_check(color))
        return not new_board.check_check(color)

    def check_check(self, color: Color) -> bool:
        print("check check")
        king_tile = self.black_king_tile
        if color == Color.White:
            king_tile = self.white_king_tile

        o_x, o_y = convert_to_computer_notation(king_tile.position)
        for type in Figure_type:
            temp_fig = Figure(type, color)
            movement_data = temp_fig.movement_options()
            for movement_x, movement_y in movement_data.attacks:

                if color == Color.Black:
                    movement_x, movement_y = movement_x * -1, movement_y * -1

                if movement_data.attacks_limit is None:
                    for i in range(1, 9):
                        checking_tile = o_x + movement_x * i, o_y + movement_y * i

                        if not self.in_bounds(checking_tile) or not self.can_attack(checking_tile, color):
                            break
                        return True

                    break

                for i in range(1, movement_data.attacks_limit + 1):
                    checking_tile = o_x + movement_x * i, o_y + movement_y * i

                    if not self.in_bounds(checking_tile) or not self.can_attack(checking_tile, color):
                        break
                    return True
        return False
            
#   DEBUGGING
    
    def print(self) -> None:
        for i in range(1, 9):
            line = "{}.line - ".format(i)
            line2 = "       - "
            for letter in ROWS_TITLES:
                fig = self.board[letter + str(i)].figure
                if fig is None:
                    line += "None   "
                    continue

                line += "{}   ".format(fig.type.name)
                line2 += "{}   ".format(fig.moved_from_start)


            print(line)
            print(line2)


def convert_to_computer_notation(notation: str) -> tuple[int, int]:
    col_index = ROWS_TITLES.find(notation[0].capitalize()) + 1
    row_index = int(notation[1])

    return col_index, row_index

def convert_to_chess_notation(notation: tuple[int, int]) -> str:

    col_index, row_index = notation
    
    return ROWS_TITLES[col_index - 1] + str(row_index)

# DEBUGGING

# new_board = Board()
# new_board.setup_board(None)
# new_board.board["E4"].figure = new_board.board["E2"].figure
# new_board.board["E2"].figure = None
# print(new_board.optional_places("E1", True))
# print(new_board.optional_places("E8", True))
# print(new_board.optional_places("D1", True))