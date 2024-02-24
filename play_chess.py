import subprocess
import chess
import random
from PIL import Image, ImageDraw, ImageTk
import time
import tkinter as tk
import numpy as np
from tkinter import ttk

def start_game():
    global previous_notes
    update_board_and_color()
    wrong_count = 0
    board_canvas["state"] = tk.NORMAL
    color_dropdown["state"] = tk.DISABLED
    start_button["state"] = tk.DISABLED
    restart_button["state"] = tk.NORMAL
    previous_notes = []
    if color_var.get() == "Black":
        cpu_move()

def board_to_image(board):
    global square_size, image, image_size
    board = str(board)
    rows = board.split('\n')
    spaces = []
    for row in rows:
        spaces.append(row.split(" "))

    square_size = 60
    image_size = 8 * square_size
    image = Image.new("RGB", (image_size, image_size), "white")
    draw = ImageDraw.Draw(image)

    colors = ["white", "steelblue"]
    for i, row in enumerate(spaces):
        for j, piece in enumerate(row):
            color = colors[(i+j) % 2]
            draw.rectangle([j * square_size, i * square_size, (j + 1) * square_size, (i + 1) * square_size], fill=color)
            if piece.isupper():
                piece_image_path = f"pieces/{piece.lower()}_white.png"  # Replace with the path to your piece images
                piece_image = Image.open(piece_image_path)
                image.paste(piece_image, (j * square_size, i * square_size), piece_image)
            elif piece.islower():
                piece_image_path = f"pieces/{piece}_black.png"  # Replace with the path to your piece images
                piece_image = Image.open(piece_image_path)
                image.paste(piece_image, (j * square_size, i * square_size), piece_image)
    return image

def update_board_image():
    global board, board_canvas, tk_image
    image = board_to_image(board)
    tk_image = ImageTk.PhotoImage(image)
    board_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    board_canvas.image = tk_image

def update_board_and_color():
    global board, board_canvas, color_var, tk_image
    update_board_image()
    if color_var.get() == "Black":
        board_canvas.delete("all")
        tk_image = ImageTk.PhotoImage(board_to_image(flip_board(board)))
        board_canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        board_canvas.image = tk_image

def flip_board(board):
    board = str(board)
    rows = board.split('\n')
    inverse_rows = [rows[i] for i in range(len(rows)-1, -1, -1)]
    board_str = ""
    for inv_row in inverse_rows:
        board_str += f"{inv_row[-1::-1]}\n"
    return board_str.strip("\n")

def show_note(event):
    global previous_notes, previous_event, board, piece_str, clicked_square, previous_click, clm, piece_var, piece_dropdown, piece_select_label, select_piece_button
    if board_canvas["state"] == tk.NORMAL:
        board_canvas.delete("dots")
        board_canvas.delete("suggest")
        note_square = get_clicked_square(event.x, event.y)
        if note_square in previous_notes:
            previous_notes.remove(note_square)
            board_canvas.delete(f"{note_square}")
            return
        previous_notes.append(note_square)
        highlight_square_on_board(note_square, "green", f"{note_square}")


def show_legal_moves(event):
    global previous_notes, previous_event, board, piece_str, clicked_square, previous_click, clm, piece_var, piece_dropdown, piece_select_label, select_piece_button, select_box
    previous_event = event
    board_canvas.delete("dots")
    board_canvas.delete("suggest")
    piece_select_label.pack_forget()
    piece_dropdown.pack_forget()
    select_piece_button.pack_forget()
    if board_canvas["state"] == tk.NORMAL:
        if event:
            clicked_square = get_clicked_square(event.x, event.y)
            piece = board.piece_at(chess.parse_square(clicked_square))
            if clicked_square == previous_click and piece:
                previous_click = None
                previous_event = None
                return
            previous_click = clicked_square
            if piece:
                if (str(piece).isupper() and color_var.get() == "White") or (str(piece).islower() and color_var.get() == "Black"):
                    highlight_square_on_board(clicked_square, "yellow")
                else:
                    for tag in previous_notes:
                        board_canvas.delete(tag)
                        previous_notes = []
                        previous_click = None
                piece_str = str(piece).upper()
                piece_str += clicked_square
                piece_str = piece_str.replace("P", "")
                moves = [str(move) for move in board.legal_moves if str(move)[:2] == clicked_square]
                show_dots_for_moves(moves)
            else:
                for tag in previous_notes:
                    board_canvas.delete(tag)
                previous_notes = []
                previous_click = None

def get_clicked_square(x, y):
    if color_var.get() == "Black":
        centerx = image_size // 2
        centery = image_size // 2
        x = centerx - (x - centerx)
        y = centery - (y - centery)
    file_index = x // square_size
    rank_index = y // square_size
    file = chr(ord("a") + file_index)
    rank = 8 - rank_index
    return file + str(rank)

def highlight_square_on_board(square, color, tag="suggest"):
    global select_box
    x, y = get_coordinates_from_square(square)
    x = x-0.4
    y = y-1
    if color_var.get() == "Black":
        centerx = image_size // 2
        centery = image_size // 2
        x = centerx - (x - centerx) - square_size-0.5
        y = centery - (y - centery) - square_size-1.5
    
    select_box = board_canvas.create_rectangle(x+1.5, y+1.5, x + square_size-1.5, y + square_size-1.5, outline=color, width=3, tags=tag)

def remove_highlight():
    board_canvas.delete("suggest")
    board_canvas["state"] = tk.NORMAL

def show_dots_for_moves(moves):
    global valid_moves, clm
    valid_moves = []
    dotr = square_size//8
    for move in moves:
        # print(f"Move: {move}")
        destination = move[2:4]
        valid_moves.append(destination)
        x, y = get_coordinates_from_square(destination)
        dotx = x + square_size//2
        doty = y + square_size//2
        if color_var.get() == "Black":
            centerx = image_size // 2
            centery = image_size // 2
            dotx = centerx - (dotx - centerx)
            doty = centery - (doty - centery)
            x = centerx - (x - centerx) - square_size
            y = centery - (y - centery) - square_size
        if show_hide_moves.get():
            board_canvas.create_oval(dotx-dotr, doty-dotr, dotx+dotr, doty+dotr, fill="lightgrey", outline="lightgrey", tags="dots")
        clm = board_canvas.bind("<Button-1>", check_legal_move)

def check_legal_move(event):
    global valid_moves
    to_move_square = get_clicked_square(event.x, event.y)
    # print(to_move_square, valid_moves)
    if to_move_square in valid_moves:
        make_move_click(event)
    else:
        show_legal_moves(event)

def choose_promotion_piece():
    global piece_var, piece_dropdown, piece_select_label, select_piece_button
    piece_select_label.pack()
    piece_dropdown.pack()
    select_piece_button.pack()

def promote_piece():
    global previous_notes, previous_event, select_box, toggle, board, moves_string, coach_mode, wrong_count, piece_str, clicked_square, best, get_move, best_move, previous_click, move_to_add
    piece = piece_var.get()
    if piece != "Knight":
        promotion_piece = piece[0]
    else:
        promotion_piece = "N"
    move_to_add += f"={promotion_piece}"
    if coach_mode.get():
        # previous_event = None
        if get_move:
            stockfish.stdin.write(f"position startpos moves{moves_string}\n")
            stockfish.stdin.flush()

            stockfish.stdin.write("go depth 10\n")
            stockfish.stdin.flush()

            response = ""
            while "bestmove" not in response:
                response = stockfish.stdout.readline()
            best_move = chess.Move.from_uci(response.split(" ")[1].strip("\n"))
            best = str(board.san(best_move))
            get_move = False
        move = str(board.san(board.parse_san(move_to_add)))
        if move != best:
            board_canvas.delete("dots")
            previous_click = None
            wrong_count += 1
            if wrong_count >= 2:
                draw_arrow(best_move)
                board_canvas["state"] = tk.DISABLED
                root.after(1000, remove_arrow)
            else:
                best_str = str(best_move)
                highlight_square_on_board(best_str[:2], "red")
                board_canvas["state"] = tk.DISABLED
                root.after(1000, remove_highlight)
            return
        
    wrong_count = 0
    coord = str(board.parse_san(move_to_add))
    board.push_san(coord)
    moves_string += f" {coord}"
    update_board_and_color()
    highlight_square_on_board(coord[:2], "yellow")
    highlight_square_on_board(coord[2:], "yellow")
    if board.is_checkmate():
        start_button["state"] = tk.DISABLED
        display_result(f"Checkmate! {colors[toggle % 2]} wins!")
        return
    elif board.is_stalemate():
        start_button["state"] = tk.DISABLED
        display_result("Stalemate!")
        return
    toggle += 1
    get_move = True
    root.after(500, cpu_move)
    piece_select_label.pack_forget()
    piece_dropdown.pack_forget()
    select_piece_button.pack_forget()
    previous_notes = []

def make_move_click(event):
    global previous_notes, previous_event, select_box, toggle, board, moves_string, coach_mode, wrong_count, piece_str, clicked_square, best, get_move, best_move, previous_click, move_to_add
    tags = board_canvas.gettags(select_box)
    if "suggest" in tags:
        # clicked_item = event.widget.find_withtag(tk.CURRENT)
        clicked_dot = get_clicked_square(event.x, event.y)
        # tags = event.widget.gettags(clicked_item)
        # if "dots" in tags:
        board_canvas.unbind("<Button-1>", clm)
        board_canvas.bind("<Button-1>", show_legal_moves)
        board_canvas.delete("suggest")
        move_to_add = piece_str + clicked_dot
        if move_to_add[0].islower():
            if (color_var.get() == "White" and move_to_add[-1] == "8") or (color_var.get() == "Black" and move_to_add[-1] == "1"):
                choose_promotion_piece()
                highlight_square_on_board(clicked_square, "yellow")
                highlight_square_on_board(move_to_add[2:4], "yellow")
                # wait_for_pack_forget()
                return
        elif move_to_add[0] == "K":
            if ord(move_to_add[-2]) - ord(clicked_square[-2]) == 2:
                move_to_add = "O-O"
            elif ord(move_to_add[-2]) - ord(clicked_square[-2]) == -2:
                move_to_add = "O-O-O"

        if coach_mode.get():
            # previous_event = None
            if get_move:
                stockfish.stdin.write(f"position startpos moves{moves_string}\n")
                stockfish.stdin.flush()

                stockfish.stdin.write("go depth 10\n")
                stockfish.stdin.flush()

                response = ""
                while "bestmove" not in response:
                    response = stockfish.stdout.readline()
                best_move = chess.Move.from_uci(response.split(" ")[1].strip("\n"))
                best = str(board.san(best_move))
                get_move = False
            move = str(board.san(board.parse_san(move_to_add)))
            if move != best:
                board_canvas.delete("dots")
                previous_click = None
                wrong_count += 1
                if wrong_count >= 2:
                    draw_arrow(best_move)
                    board_canvas["state"] = tk.DISABLED
                    root.after(1000, remove_arrow)
                else:
                    best_str = str(best_move)
                    highlight_square_on_board(best_str[:2], "red")
                    board_canvas["state"] = tk.DISABLED
                    root.after(1000, remove_highlight)
                return
            
        wrong_count = 0
        coord = str(board.parse_san(move_to_add))
        board.push_san(coord)
        moves_string += f" {coord}"
        update_board_and_color()
        highlight_square_on_board(coord[:2], "yellow")
        highlight_square_on_board(coord[2:], "yellow")
        previous_notes = []
        if board.is_checkmate():
            start_button["state"] = tk.DISABLED
            display_result(f"Checkmate! {colors[toggle % 2]} wins!")
            return
        elif board.is_stalemate():
            start_button["state"] = tk.DISABLED
            display_result("Stalemate!")
            return
        toggle += 1
        get_move = True
        root.after(500, cpu_move)

def draw_arrow(move):
    move = str(move)
    start = move[:2]
    end = move[2:]
    startx, starty = get_coordinates_from_square(start)
    startx, starty = startx + square_size//2, starty + square_size//2
    endx, endy = get_coordinates_from_square(end)
    endx, endy = endx + square_size//2, endy + square_size//2
    if color_var.get() == "Black":
        centerx = image_size // 2
        centery = image_size // 2
        startx, starty = centerx - (startx - centerx), centery - (starty - centery)
        endx, endy = centerx - (endx - centerx), centery - (endy - centery)
    arrow = board_canvas.create_line(startx, starty, endx, endy, arrow=tk.LAST, fill="red", width=5, tags="arrow")

def remove_arrow():
    board_canvas.delete("arrow")
    board_canvas["state"] = tk.NORMAL

def get_coordinates_from_square(square):
    file_index = ord(square[0]) - ord("a")
    rank_index = 8 - int(square[1])
    x = file_index * square_size
    y = rank_index * square_size
    return x, y

def cpu_move():
    global toggle, board, moves_string
    stockfish.stdin.write(f"position startpos moves{moves_string}\n")
    stockfish.stdin.flush()
    board_canvas.delete("suggest")
    difficulty_levels = {
        "Beginner": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 50],
        "Intermediate": [4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 10],
        "Expert": [50, 9.5, 8.5, 7.5, 6.5, 5.5, 4.5, 3.5, 2.5, 1.5, 0.5],
        "Impossible": [100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    probability_list = difficulty_levels.get(difficulty_var.get())
    move_to_highlight_start = ""
    move_to_highlight_end = ""
    legal_moves = list(board.legal_moves)
    random_move = random.choice(legal_moves)
    random_str = str(random_move)
    stockfish.stdin.write(f"go depth 5 multipv 10\n")  # Adjust multipv for the number of top moves you want
    stockfish.stdin.flush()
    response = ""
    top_moves = []
    while True:
        line = stockfish.stdout.readline()
        if "bestmove" in line:
            break
        if " pv " in line:
            move = chess.Move.from_uci(line.split(" pv ")[1].split(" ")[0].strip("\n"))
            top_moves.append(move)

    # a_best_move = random.choice(top_moves[:min(len(top_moves), )])
    # for prob in probability_list:

    if random.random() < probability_list[-1]*0.01:
        selected_move = random_move
    else:
        new_probs = list(np.array(probability_list[:len(top_moves)])*(10/len(top_moves))*0.01*100/(100-probability_list[-1]))
        selected_move = random.choices(top_moves, weights=new_probs, k=1)[0]
     
    selected_str = str(selected_move)
    move_to_highlight_start = selected_str[:2]
    move_to_highlight_end = selected_str[2:]
    board.push_san(str(selected_move))
    moves_string += f" {selected_move}"
    
    update_board_and_color()
    highlight_square_on_board(move_to_highlight_start, "yellow")
    highlight_square_on_board(move_to_highlight_end, "yellow")

    if board.is_checkmate():
        start_button["state"] = tk.DISABLED
        display_result(f"Checkmate! {colors[toggle % 2]} wins!")
        return
    elif board.is_stalemate():
        start_button["state"] = tk.DISABLED
        display_result("Stalemate!")
        return
    toggle += 1

def display_result(message):
    board_canvas["state"] = tk.DISABLED
    result_label.pack()
    coach_mode_checkbox.pack_forget()
    result_label.config(text=message, foreground="black")
    restart_button.pack()

def restart_game():
    global toggle, board, moves_string
    # Reset board and variables
    moves_string = ""
    board = chess.Board()
    toggle = 0

    # Enable text entry and buttons
    restart_button.pack_forget()
    coach_mode_checkbox.pack_forget()
    board_canvas["state"] = tk.DISABLED
    # color_var.set("White")
    color_dropdown["state"] = "readonly"
    # difficulty_var.set("Beginner")
    diff_dropdown["state"] = "readonly"
    start_button["state"] = tk.NORMAL
    restart_button.pack()
    restart_button["state"] = tk.DISABLED
    coach_mode_checkbox.pack()
    result_label.pack_forget()

    # Update the board image
    update_board_and_color()

def toggle_show_hide_moves():
    global previous_click, previous_event, clicked_square
    previous_click = None
    show_legal_moves(previous_event)
    if not show_hide_moves.get():
        board_canvas.delete("dots")
        # previous_click = clicked_square


stockfish = subprocess.Popen("stockfish/stockfish-windows-x86-64-avx2.exe", universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

moves_string = ""
board = chess.Board()
player_color = "White"
colors = ["White", "Black"]
diff_level = "Beginner"
difficulties = ["Beginner", "Intermediate", "Expert", "Impossible"]
toggle = 0
wrong_count = 0
previous_click = None
clicked_square = None
get_move = True
best = None
best_move = None
valid_moves = []
clm = None
select_box = None
move_to_add = None
previous_event = None
previous_notes = []

def main():
    global root, board_canvas, color_label, color_var, color_dropdown, diff_label, difficulty_var, diff_dropdown, start_button, restart_button, coach_mode, coach_mode_checkbox, result_label, show_hide_moves, show_hide_moves_checkbox, piece_var, piece_dropdown, piece_select_label, select_piece_button
    root = tk.Tk()
    root.title("Chess GUI")

    board_canvas = tk.Canvas(root, width=480, height=480, state=tk.DISABLED)
    board_canvas.pack()
    board_canvas.bind("<Button-1>", show_legal_moves)
    board_canvas.bind("<Button-3>", show_note)

    color_label = ttk.Label(root, text="Play as: ")
    color_label.pack()

    color_var = tk.StringVar()
    color_var.set(player_color)
    color_dropdown = ttk.Combobox(root, textvariable=color_var, values=colors, state="readonly")
    color_dropdown.bind("<<ComboboxSelected>>", lambda event: update_board_and_color())
    color_dropdown.pack()

    diff_label = ttk.Label(root, text="Difficulty level: ")
    diff_label.pack()

    difficulty_var = tk.StringVar()
    difficulty_var.set(diff_level)
    diff_dropdown = ttk.Combobox(root, textvariable=difficulty_var, values=difficulties, state="readonly")
    diff_dropdown.pack()

    show_hide_moves = tk.BooleanVar()
    show_hide_moves_checkbox = ttk.Checkbutton(root, text="Show legal moves", variable=show_hide_moves, command=toggle_show_hide_moves)
    show_hide_moves_checkbox.pack()

    start_button = ttk.Button(root, text="Start", command=start_game)
    start_button.pack()

    restart_button = ttk.Button(root, text="Restart game", command=restart_game, state=tk.DISABLED)
    restart_button.pack()

    coach_mode = tk.BooleanVar()
    coach_mode_checkbox = ttk.Checkbutton(root, text="Training mode", variable=coach_mode)
    coach_mode_checkbox.pack()

    result_label = ttk.Label(root)

    piece_select_label = ttk.Label(root, text="Promote to: ")
    piece_var = tk.StringVar()
    piece_var.set("Queen")
    piece_dropdown = ttk.Combobox(root, textvariable=piece_var, values=["Queen", "Rook", "Bishop", "Knight"], state="readonly")
    select_piece_button = ttk.Button(root, text="Select", command=promote_piece)

    update_board_image()

    root.mainloop()

    stockfish.stdin.write("quit\n")
    stockfish.stdin.flush()

if __name__ == "__main__":
    main()