import tkinter as tk

class ChessBoard:
    def __init__(self, master):
        self.master = master
        self.master.title("Xadrez")
        self.board = self.create_board()
        self.selected_piece = None
        self.selected_position = None
        self.turn = 'branco'  # Começa com as peças brancas
        self.create_widgets()

    def create_board(self):
        board = [[' ' for _ in range(8)] for _ in range(8)]
        # Peças pretas
        board[0] = ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']
        board[1] = ['♟' for _ in range(8)]
        # Peças brancas
        board[6] = ['♙' for _ in range(8)]
        board[7] = ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']
        return board

    def create_widgets(self):
        self.canvas = tk.Canvas(self.master, width=400, height=450)
        self.canvas.pack()
        self.draw_board()

        # Bind de eventos para arrastar
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def draw_board(self):
        colors = ['#f0d9b5', '#b58863']
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                x1 = col * 50
                y1 = row * 50
                x2 = x1 + 50
                y2 = y1 + 50
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                piece = self.board[row][col]
                if piece != ' ':
                    self.canvas.create_text(x1 + 25, y1 + 25, text=piece, font=("Arial", 24))

        self.canvas.create_text(200, 420, text=f"Turno: {self.turn.capitalize()}", font=("Arial", 16), fill="black")

    def on_button_press(self, event):
        col = event.x // 50
        row = event.y // 50
        self.select_piece(row, col)

    def on_mouse_move(self, event):
        if self.selected_piece:
            self.canvas.coords("selected", event.x - 25, event.y - 25)

    def on_button_release(self, event):
        if self.selected_piece:
            col = event.x // 50
            row = event.y // 50
            if self.move_piece(row, col):
                self.draw_board()  # Redesenha o tabuleiro após o movimento
            else:
                self.return_piece()  # Retorna a peça se o movimento não for válido

            self.selected_piece = None
            self.selected_position = None

    def select_piece(self, row, col):
        piece = self.board[row][col]
        if piece != ' ' and self.is_correct_turn(piece):
            self.selected_piece = piece
            self.selected_position = (row, col)
            # Adiciona a peça selecionada como um item temporário para arrastar
            self.canvas.create_text(0, 0, text=piece, font=("Arial", 24), tags="selected")

    def move_piece(self, row, col):
        if self.selected_piece:
            if self.is_valid_move(self.selected_piece, self.selected_position, (row, col)):
                # Move a peça
                self.board[row][col] = self.selected_piece
                self.board[self.selected_position[0]][self.selected_position[1]] = ' '
                # Troca de turno
                self.turn = 'preto' if self.turn == 'branco' else 'branco'
                return True
        return False

    def return_piece(self):
        start_row, start_col = self.selected_position
        self.board[start_row][start_col] = self.selected_piece  # Retorna a peça para a posição original
        self.draw_board()  # Redesenha o tabuleiro

    def is_correct_turn(self, piece):
        return (self.turn == 'branco' and piece in ['♙', '♖', '♘', '♗', '♕', '♔']) or \
               (self.turn == 'preto' and piece in ['♟', '♜', '♞', '♝', '♛', '♚'])

    def is_valid_move(self, piece, start, end):
        start_row, start_col = start
        end_row, end_col = end

        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            return False  # Verifica se a posição de destino é válida

        target_piece = self.board[end_row][end_col]
        if target_piece != ' ' and self.is_correct_turn(target_piece):
            return False  # Não pode capturar peça aliada

        # Validação para peões
        if piece in ['♙', '♟']:
            direction = 1 if piece == '♙' else -1
            start_row_limit = 1 if piece == '♙' else 6

            if start_col == end_col:  # Movimento normal
                if (end_row == start_row + direction and self.board[end_row][end_col] == ' '):
                    return True
                if (start_row == start_row_limit and
                    end_row == start_row + 2 * direction and
                    self.board[start_row + direction][end_col] == ' ' and
                    self.board[end_row][end_col] == ' '):
                    return True
            if (end_row == start_row + direction) and (end_col == start_col + 1 or end_col == start_col - 1):
                if self.board[end_row][end_col] != ' ':
                    return True

        # Validação para torres
        if piece in ['♖', '♜']:
            if start_row == end_row or start_col == end_col:
                if self.path_clear(start, end):
                    return True

        # Validação para cavalos
        if piece in ['♘', '♞']:
            if (abs(start_row - end_row), abs(start_col - end_col)) in [(2, 1), (1, 2)]:
                return True

        # Validação para bispos
        if piece in ['♗', '♝']:
            if abs(start_row - end_row) == abs(start_col - end_col):
                if self.path_clear(start, end):
                    return True

        # Validação para rainhas
        if piece in ['♕', '♛']:
            if (start_row == end_row or start_col == end_col or
                abs(start_row - end_row) == abs(start_col - end_col)):
                if self.path_clear(start, end):
                    return True

        # Validação para reis
        if piece in ['♔', '♚']:
            if max(abs(start_row - end_row), abs(start_col - end_col)) == 1:
                return True

        return False

    def path_clear(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        if start_row == end_row:  # Horizontal
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if self.board[start_row][col] != ' ':
                    return False
        elif start_col == end_col:  # Vertical
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if self.board[row][start_col] != ' ':
                    return False
        else:  # Diagonal
            row_step = 1 if end_row > start_row else -1
            col_step = 1 if end_col > start_col else -1
            row, col = start_row + row_step, start_col + col_step
            while (row != end_row and col != end_col):
                if self.board[row][col] != ' ':
                    return False
                row += row_step
                col += col_step

        return True

if __name__ == "__main__":
    root = tk.Tk()
    chess_board = ChessBoard(root)
    root.mainloop()
